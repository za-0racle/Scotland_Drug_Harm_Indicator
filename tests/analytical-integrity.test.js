import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {sha256Bytes,sha256Canonical,sha256Text,stableJson} from '../src/api/analytical-integrity.js';
import {stableJson as mortalityStableJson} from '../src/api/mortality-collector.js';

test('canonical JSON preserves sorted keys, nested values, Unicode and JavaScript number encoding',async()=>{
 const value={z:'\u00e9',a:{'\u03b2':[1,1.0,-0.0,null,true]},n:1e-7};
 const serialized='{"a":{"\u03b2":[1,1,0,null,true]},"n":1e-7,"z":"\u00e9"}';
 assert.equal(stableJson(value),serialized);
 assert.equal(await sha256Canonical(value),'9a469cbe0f88e773a87c2967efe9272f230433cf733c93d9e710792af9bfd938');
 assert.equal(await sha256Canonical({b:2,a:1}),'43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777');
 assert.equal(mortalityStableJson,stableJson);
});

test('canonical-object, raw-text and raw-byte hashes retain their distinct inputs',async()=>{
 const serialized='{"a":1,"b":2}';
 const expected=createHash('sha256').update(serialized,'utf8').digest('hex');
 assert.equal(await sha256Canonical({b:2,a:1}),expected);
 assert.equal(await sha256Text(serialized),expected);
 assert.equal(await sha256Bytes(new TextEncoder().encode(serialized)),expected);
 assert.notEqual(await sha256Canonical(serialized),expected);
 assert.notEqual(await sha256Text('é'),await sha256Bytes(new Uint8Array([0xe9])));
});

test('raw hashing rejects values outside its explicit text and byte representations',async()=>{
 await assert.rejects(sha256Text(new Uint8Array()),TypeError);
 await assert.rejects(sha256Bytes('text'),TypeError);
 await assert.rejects(sha256Bytes(new DataView(new ArrayBuffer(1))),TypeError);
});

test('canonical hashing retains prior TextEncoder behavior for non-JSON inputs',async()=>{
 assert.equal(await sha256Canonical(undefined),'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
 assert.equal(await sha256Canonical(Number.NaN),await sha256Text('null'));
 assert.equal(stableJson({value:undefined}),'{"value":undefined}');
});

test('all SHA-256 entry points fail closed without Web Crypto',async()=>{
 const descriptor=Object.getOwnPropertyDescriptor(globalThis,'crypto');
 try{
  Object.defineProperty(globalThis,'crypto',{configurable:true,value:undefined});
  await assert.rejects(sha256Bytes(new Uint8Array()),/Secure SHA-256 verification is unavailable/);
  await assert.rejects(sha256Text('value'),/Secure SHA-256 verification is unavailable/);
  await assert.rejects(sha256Canonical({value:1}),/Secure SHA-256 verification is unavailable/);
 }finally{
  if(descriptor)Object.defineProperty(globalThis,'crypto',descriptor);
  else delete globalThis.crypto;
 }
});
