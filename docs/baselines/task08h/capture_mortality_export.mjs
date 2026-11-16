import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import {mortalityCsv} from '../../../src/platform/mortality-data.js';

const directory=new URL('.',import.meta.url);
const legacy=JSON.parse(readFileSync(new URL('../task08d/legacy-response.json',directory),'utf8'));
const output=new URL('mortality-legacy-export.csv',directory);
const area=legacy.data.find(row=>row.geography==='L: Argyll & West Dunbartonshire');
if(!area)throw new Error('Immutable Task 08D fixture lacks the selected police division.');
const filters={boundary:'police_division',indicator:'suspected_deaths',
 area:area.geography_id,from:'2017 Q1',to:'2025 Q4'};
const rows=legacy.data.filter(row=>row.boundary_type===filters.boundary
 &&row.indicator_id===filters.indicator&&row.geography_id===filters.area);
const metadata={...legacy.metadata,filters,
 export_scope:'Complete eligible selected-area history across API and table pages; not necessarily complete source history.'};
const csv=mortalityCsv(rows,metadata);
writeFileSync(output,csv,{encoding:'utf8',flag:'wx'});
const summary={
 baseline:'Task 08D immutable legacy fixture passed through the unchanged legacy CSV exporter',
 rows:rows.length,bytes:Buffer.byteLength(csv),
 sha256:createHash('sha256').update(csv).digest('hex'),
 source_fixture_sha256:createHash('sha256').update(readFileSync(new URL('../task08d/legacy-response.json',directory))).digest('hex'),
};
writeFileSync(new URL('mortality-export-summary.json',directory),JSON.stringify(summary,null,2)+'\n',{encoding:'utf8',flag:'wx'});
console.log(JSON.stringify(summary,null,2));
