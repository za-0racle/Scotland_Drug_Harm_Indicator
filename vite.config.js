import {defineConfig} from 'vite';

const proxy={
 '/api':{
  target:'http://127.0.0.1:8000',changeOrigin:true,
  configure(server){
   server.on('error',(_error,_request,response)=>{
    if(response&&!response.headersSent&&typeof response.writeHead==='function'){
     response.writeHead(502,{'Content-Type':'application/json'});
     response.end(JSON.stringify({state:'error',kind:'unavailable_evidence',data:[],total:0,metadata:{},message:'Research backend is unreachable. Start FastAPI on port 8000 and retry Refresh API data.'}));
    }
   });
  },
 },
};
export default defineConfig({server:{port:5173,strictPort:true,proxy},preview:{proxy}});
