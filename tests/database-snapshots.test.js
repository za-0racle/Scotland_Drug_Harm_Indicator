import test from 'node:test';
import assert from 'node:assert/strict';
import {databaseSnapshotCsv,databaseSnapshotResources} from '../src/platform/database-snapshots.js';

test('live database snapshot exports preserve zero, missing values and injection-safe CSV',()=>{
 assert.deepEqual(Object.keys(databaseSnapshotResources),['naloxone_activity','geographic_areas','data_sources']);
 const csv=databaseSnapshotCsv('naloxone_activity',[{
  week_beginning:'2024-01-01',geography_display:'National Aggregate — Scotland',
  geography_class:'national',administrations:0,moving_average:null,
  source_dataset:'=unsafe.csv'
 }]);
 assert.ok(csv.startsWith('\uFEFF'));
 assert.ok(csv.includes('"0","","\'=unsafe.csv"'));
 assert.ok(csv.includes("'=unsafe.csv"));
 assert.ok(csv.includes('Source-reported moving average'));
 assert.throws(()=>databaseSnapshotCsv('radar_intelligence',[]),/Unsupported/);
});
