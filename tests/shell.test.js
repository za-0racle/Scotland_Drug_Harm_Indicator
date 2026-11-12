import test from 'node:test';
import assert from 'node:assert/strict';
import {screens,isRoute,screenFor,routeTitle} from '../src/platform/shell.js';
test('eight primary destinations preserve all original deep links',()=>{
 assert.equal(screens.length,8);assert.equal(new Set(screens.map(([id])=>id)).size,8);
 for(const id of ['overview','geography','trends','anomalies','signals','forecasting','reports','methodology','comparison','substance'])assert.equal(isRoute(id),true,id);
 assert.equal(isRoute('unknown'),false);assert.equal(screenFor('signals'),'anomalies');assert.equal(screenFor('methodology'),'reports');
 assert.equal(routeTitle('trends'),'Mortality Analytics');assert.equal(routeTitle('signals'),'Surveillance Signals');
});
