import test from 'node:test';
import assert from 'node:assert/strict';
import {request,resolveApiBase} from '../src/api/client.js';
import config from '../vite.config.js';
const response=(body,type='application/json',status=200)=>({status,ok:status<400,headers:new Headers({'Content-Type':type}),json:async()=>JSON.parse(body)});
const call=reply=>request('/health',{},{fetcher:async()=>reply});
test('HTML fallback, invalid JSON, schema and HTTP errors remain distinct',async()=>{
 await assert.rejects(call(response('<!doctype html>','text/html')),e=>e.code==='non_json'&&e.status===200);
 await assert.rejects(call(response('broken')),e=>e.code==='invalid_json');
 await assert.rejects(call(response('{}')),e=>e.code==='schema');
 await assert.rejects(call(response('{}','application/json',404)),e=>e.code==='http'&&e.status===404);
 await assert.rejects(call(response('','text/plain',502)),e=>e.code==='unreachable');
 await assert.rejects(request('/health',{},{fetcher:async()=>{throw new Error('synthetic network');}}),e=>e.code==='unreachable');
 for(const state of ['empty','unavailable'])assert.equal((await call(response(JSON.stringify({state,data:[],total:0})))).state,state);
});
test('one validated API base prevents HTML routes and credential-bearing overrides',()=>{
 for(const value of [undefined,'',' /api/v1/ '])assert.equal(resolveApiBase(value),'/api/v1');
 assert.equal(resolveApiBase('http://localhost:8000/api/v1/'),'http://localhost:8000/api/v1');
 for(const value of ['/','/api','http://localhost:5173','http://user:password@localhost:8000/api/v1','/api/v1?key=test'])assert.throws(()=>resolveApiBase(value),e=>e.code==='configuration'&&!e.message.includes('password'));
});
test('dev and preview proxy target actual API; outage gives JSON without raw errors',()=>{
 assert.equal(config.server.port,5173);assert.equal(config.server.strictPort,true);
 assert.equal(config.server.proxy['/api'].target,'http://127.0.0.1:8000');
 assert.equal(config.preview.proxy['/api'].target,'http://127.0.0.1:8000');
 let handler,status,body,type;config.server.proxy['/api'].configure({on:(_event,fn)=>{handler=fn;}});
 handler(new Error('TEST PRIVATE DETAILS'),{}, {writeHead:(code,headers)=>{status=code;type=headers['Content-Type'];},end:value=>{body=value;}});
 assert.equal(status,502);assert.equal(type,'application/json');assert.equal(JSON.parse(body).state,'error');assert.ok(!body.includes('PRIVATE'));
});
