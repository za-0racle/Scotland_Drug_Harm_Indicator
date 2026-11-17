import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
const read=path=>readFileSync(new URL('../public/'+path,import.meta.url));
const pngSize=path=>{const bytes=read(path);assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a');return [bytes.readUInt32BE(16),bytes.readUInt32BE(20)];};

test('sharing and canonical metadata are present once in initial HTML',()=>{
 assert.match(html,/<html lang="en">/);
 assert.equal((html.match(/<title>/g)||[]).length,1);
 assert.match(html,/<title>Scotland Drug Harm Intelligence \| Research Dashboard<\/title>/);
 assert.equal((html.match(/rel="canonical"/g)||[]).length,1);
 assert.match(html,/<link rel="canonical" href="https:\/\/sdhi.cc\/"/);
 for(const key of ['description','theme-color','viewport','twitter:card','twitter:title','twitter:description','twitter:image'])assert.equal((html.match(new RegExp(`name="${key}"`,'g'))||[]).length,1,key);
 for(const key of ['type','site_name','title','description','url','image','image:width','image:height','image:type','image:alt'])assert.equal((html.match(new RegExp(`property="og:${key}"`,'g'))||[]).length,1,key);
 assert.match(html,/property="og:image" content="https:\/\/sdhi.cc\/og-image.png"/);
 assert.match(html,/name="twitter:card" content="summary_large_image"/);
 assert.doesNotMatch(html,/twitter:(site|creator)/);
});

test('linked icons and sharing image have real production formats and dimensions',()=>{
 assert.deepEqual(pngSize('og-image.png'),[1200,630]);
 assert.deepEqual(pngSize('apple-touch-icon.png'),[180,180]);
 for(const size of [192,512])assert.deepEqual(pngSize(`brand/sdhi-icon-${size}.png`),[size,size]);
 for(const path of ['favicon.svg','favicon.ico','apple-touch-icon.png','brand/sdhi-icon-192.png','brand/sdhi-icon-512.png'])assert.ok(html.includes(`href="/${path}"`),path);
 const ico=read('favicon.ico');assert.equal(ico.readUInt16LE(0),0);assert.equal(ico.readUInt16LE(2),1);
 const sizes=Array.from({length:ico.readUInt16LE(4)},(_,i)=>ico[6+i*16]||256);
 assert.deepEqual(sizes,[16,32,48,64,128,256]);
 assert.match(read('favicon.svg').toString(),/viewBox="0 0 64 64"/);
 for(const path of ['brand/sdhi-logo.svg','brand/sdhi-logo-dark.svg','brand/sdhi-icon.svg'])assert.match(read(path).toString(),/<svg /);
});
