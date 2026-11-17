const allowed=new Set(['geography_id','boundary_type','indicator','category','model','start_year','end_year','start_date','end_date','offset','limit','signals_only','compare_to','resource','format']);
export class ApiError extends Error {
 constructor(message,status=0,code='request'){super(message);this.status=status;this.code=code;}
}
export function queryString(params={},analytical=false){
 const query=new URLSearchParams();
 for(const[key,value]of Object.entries(params)){
  if(!allowed.has(key)&&!(analytical&&key==='expected_collection'))throw new ApiError(`Unsupported filter: ${key}`);
  if(value!==undefined&&value!==null&&value!=='')query.set(key,String(value));
 }
 return query.toString();
}
export function resolveApiBase(value=import.meta.env?.VITE_API_BASE_URL){
 const base=(value?.trim()||'/api/v1').replace(/\/+$/,'');
 if(base==='/api/v1')return base;
 try{
  const url=new URL(base);
  if(['http:','https:'].includes(url.protocol)&&url.pathname==='/api/v1'&&!url.username&&!url.password&&!url.search&&!url.hash)return base;
 }catch{/* Configuration errors deliberately omit the supplied value. */}
 throw new ApiError('Invalid API base URL. Use /api/v1 or the backend URL ending in /api/v1.',0,'configuration');
}
export async function request(path,params={},options={}){
 if(!/^\/[a-z0-9/_-]+$/i.test(path))throw new ApiError('Invalid API path');
 const analytical=['/analytical/v1/mortality-trends','/analytical/v1/forensic-toxicology'].includes(path);
 const url=`${resolveApiBase(options.base)}${path}?${queryString(params,analytical)}`;
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),options.timeout??60000);
 let status=0,contentType='';
 try{
  const response=await(options.fetcher??fetch)(url,{signal:controller.signal,headers:{Accept:'application/json'}});
  status=response.status;contentType=response.headers?.get('content-type')??'';
  if([502,503,504].includes(status)&&!contentType.toLowerCase().includes('json'))throw new ApiError('These research results could not be loaded. Please try Refresh data.',status,'unreachable');
  if(!contentType.toLowerCase().includes('application/json'))throw new ApiError('The research service returned an unexpected response. Please try Refresh data.',status,'non_json');
  let data;
  try{data=await response.json();}catch{throw new ApiError('The research service returned unreadable results. Please try Refresh data.',status,'invalid_json');}
  if(!response.ok)throw new ApiError(typeof data.message==='string'?data.message:status===422?'Invalid filters or incompatible geography':`Research API returned HTTP ${status}.`,status,'http');
  if(analytical){
   // This route has its own typed shape. The collector performs full validation.
   if(!data||typeof data!=='object'||Array.isArray(data))throw new ApiError('Unexpected analytical response schema.',status,'schema');
  }else if(!['ready','empty','error','unavailable'].includes(data.state)||!Array.isArray(data.data)||data.data.some(row=>!row||typeof row!=='object'||Array.isArray(row))||!Number.isInteger(data.total)||data.total<0)throw new ApiError('The research results could not be verified. Please try Refresh data.',status,'schema');
  return data;
 }catch(error){
  const safe=error.name==='AbortError'?new ApiError('The research service took too long to respond. Please try Refresh data.',status,'timeout'):error instanceof ApiError?error:new ApiError('Cannot reach the research service. Please try Refresh data.',0,'unreachable');
  // Development diagnostics contain no body, headers, credentials or stack trace.
  if(import.meta.env?.DEV)console.warn('[research-api]',{path,status,contentType,code:safe.code});
  throw safe;
 }finally{clearTimeout(timer);}
}
export const exportUrl=(resource,format,params={})=>`${resolveApiBase()}/exports?${queryString({...params,resource,format})}`;
