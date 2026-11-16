// Lossless mapping into the existing Geographic Explorer presentation model.
import {collectMortality} from '../api/mortality-collector.js';
const originalFields=['indicator_id','source_id','source_path','geography','period','ordinal','observed_value','unit','period_basis','period_start','period_end','quality_status','limitations','year','quarter','publication_date','share_of_national_pct','previous_value','period_change','period_change_pct','year_reference_value','year_change_pct','rolling_average','rolling_periods','historical_reference_mean','reference_periods','reference_change_pct','direction','percentage_point_change','year_comparison_basis','calculation_method','comparison_status','source_sha256','source_url','source_data_cutoff','analysis_as_of','data_age_days','publication_lag_days','publication_status','scientific_status'];
export function mortalityPresentation(collection){
 if(!collection.complete||collection.observations.length!==collection.total)throw Error('Complete analytical mortality history is required.');
 const {source:s,indicator:i,artifact:a,research_metadata:r}=collection;
 const data=collection.observations.map(o=>{
  const values={indicator_id:i.indicator_id,source_id:s.source_id,source_path:s.source_path,geography:o.geography.original_name,
   period:o.period.label,ordinal:o.period.ordinal,observed_value:o.value,unit:i.unit,period_basis:i.period_basis,
   period_start:o.period.period_start,period_end:o.period.period_end,quality_status:o.availability_status,
   limitations:i.original_reporting_qualification,year:o.period.year,quarter:o.period.quarter,publication_date:s.publication_date,
   rolling_periods:i.rolling_periods,reference_periods:i.reference_periods,year_comparison_basis:i.year_comparison_basis,
   calculation_method:i.calculation_method,source_sha256:s.source_version,source_url:s.source_url,
   source_data_cutoff:s.source_data_cutoff,publication_status:s.publication_status,scientific_status:i.scientific_status,
   ...r,...o.research_context};
  const row=Object.fromEntries(originalFields.map(k=>[k,values[k]]));
  Object.assign(row,{geography_id:o.geography.geography_id,name:o.geography.canonical_name,boundary_type:o.geography.boundary_type,source_geography:o.geography.original_name});
  // Preserve new identity without changing historical JSON/CSV record contents.
  Object.defineProperty(row,'analyticalIdentity',{value:Object.freeze({observation_id:o.observation_id,contract_version:collection.contract_version,source_version:s.source_version,availability_status:o.availability_status,collection_token:collection.collection_token}),enumerable:false});
  return row;
 });
 const metadata={resource:a.resource,storage:a.storage,analytical_version:a.analytical_version,executed_at_utc:a.executed_at_utc,
  artifact_sha256:a.artifact_sha256,source_path:a.source_path,provenance_manifest:a.provenance_manifest,limitations:a.limitations};
 return{state:'ready',data,total:collection.total,metadata,message:'',analytical:collection};
}
export async function completeAnalyticalMortality(api,options){return mortalityPresentation(await collectMortality(api,options));}
