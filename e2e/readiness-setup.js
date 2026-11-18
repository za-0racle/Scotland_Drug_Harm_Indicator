// A listening health route does not establish database readiness.
export default async function readiness(){
 for(const path of ['/health','/mortality/quarterly?limit=1','/monitoring/configurations?limit=1','/monitoring/results?limit=1']){
  const response=await fetch('http://127.0.0.1:8000/api/v1'+path,{signal:AbortSignal.timeout(30000)});
  if(!response.ok)throw new Error(`Readiness failed for ${path}: HTTP ${response.status}. Inspect the local API database diagnostics.`);
  const body=await response.json();
  if(body.state!=='ready'||!Array.isArray(body.data)||!body.data.length)throw new Error(`Readiness failed for ${path}: no verified accessible records. Do not treat empty/RLS access as ready.`);
  console.log(`[readiness] ${path}: HTTP ${response.status}, ${body.data.length} accessible record(s)`);
 }
}
