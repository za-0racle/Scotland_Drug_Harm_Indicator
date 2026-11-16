function object(value){
 return value!==null&&typeof value==='object'&&!Array.isArray(value);
}

export function stableJson(value){
 if(Array.isArray(value))return '['+value.map(stableJson).join(',')+']';
 if(object(value))return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+stableJson(value[key])).join(',')+'}';
 return JSON.stringify(value);
}

export async function sha256Bytes(value){
 if(!(value instanceof Uint8Array))throw new TypeError('SHA-256 byte input must be a Uint8Array.');
 if(!globalThis.crypto?.subtle)throw new Error('Secure SHA-256 verification is unavailable.');
 const result=await globalThis.crypto.subtle.digest('SHA-256',value);
 return Array.from(new Uint8Array(result),byte=>byte.toString(16).padStart(2,'0')).join('');
}

export async function sha256Text(value){
 if(typeof value!=='string')throw new TypeError('SHA-256 text input must be a string.');
 return sha256Bytes(new TextEncoder().encode(value));
}

export async function sha256Canonical(value){
 return sha256Bytes(new TextEncoder().encode(stableJson(value)));
}
