// Lossless mapping from the forensic analytical contract to Substance Intelligence rows.
import {collectForensic} from '../api/forensic-collector.js';

const originalFields=[
 'indicator_id','source_id','source_path','geography','period','ordinal','observed_value','unit','period_basis',
 'period_start','period_end','quality_status','limitations','previous_value','period_change','period_change_pct',
 'year_reference_value','year_change_pct','rolling_average','rolling_periods','historical_reference_mean',
 'reference_periods','reference_change_pct','direction','percentage_point_change','year_comparison_basis',
 'calculation_method','comparison_status','within_source_period_dense_rank','source_sha256','source_url',
 'publication_date','source_data_cutoff','analysis_as_of','data_age_days','publication_lag_days',
 'publication_status','scientific_status','geography_id','name','boundary_type','source_geography',
];

export function forensicPresentation(collection){
 if(!collection.complete||collection.observations.length!==collection.total||collection.total!==210)
  throw new Error('Complete analytical forensic history is required.');
 const {source,artifact,measure,research_metadata:research}=collection;
 const categories=new Map(collection.categories.map(category=>[category.category_id,category]));
 const data=collection.observations.map(observation=>{
  const category=categories.get(observation.category_id);
  if(!category)throw new Error('Forensic category definition is unavailable.');
  const geo=observation.geography,period=observation.period,context=observation.research_context;
  const values={
   indicator_id:observation.indicator_id,source_id:source.source_id,source_path:source.source_path,
   geography:geo.original_name,period:period.label,ordinal:period.ordinal,observed_value:observation.value,
   unit:measure.unit,period_basis:measure.period_basis,period_start:period.period_start,period_end:period.period_end,
   quality_status:observation.availability_status,limitations:observation.limitations,
   previous_value:context.previous_value,period_change:context.period_change,period_change_pct:context.period_change_pct,
   year_reference_value:context.year_reference_value,year_change_pct:context.year_change_pct,
   rolling_average:context.rolling_average,rolling_periods:context.rolling_periods,
   historical_reference_mean:context.historical_reference_mean,reference_periods:context.reference_periods,
   reference_change_pct:context.reference_change_pct,direction:context.direction,
   percentage_point_change:context.percentage_point_change,year_comparison_basis:measure.year_comparison_basis,
   calculation_method:measure.calculation_method,comparison_status:context.comparison_status,
   within_source_period_dense_rank:context.within_source_period_dense_rank,source_sha256:source.source_version,
   source_url:source.source_url,publication_date:source.publication_date,source_data_cutoff:source.source_data_cutoff,
   analysis_as_of:research.analysis_as_of,data_age_days:research.data_age_days,
   publication_lag_days:context.publication_lag_days,publication_status:source.publication_status,
   scientific_status:measure.scientific_status,geography_id:geo.geography_id,name:geo.canonical_name,
   boundary_type:geo.boundary_type,source_geography:geo.original_name,
  };
  const row=Object.fromEntries(originalFields.map(key=>[key,values[key]]));
  Object.defineProperty(row,'analyticalIdentity',{
   value:Object.freeze({
    observation_id:observation.observation_id,category_id:observation.category_id,
    contract_version:collection.contract_version,source_version:source.source_version,
    artifact_sha256:artifact.artifact_sha256,availability_status:observation.availability_status,
    collection_token:collection.collection_token,
   }),
   enumerable:false,
  });
  return row;
 });
 const metadata={
  resource:artifact.resource,storage:artifact.storage,analytical_version:artifact.analytical_version,
  executed_at_utc:artifact.executed_at_utc,artifact_sha256:artifact.artifact_sha256,
  source_path:artifact.source_path,provenance_manifest:artifact.provenance_manifest,limitations:artifact.limitations,
 };
 return {state:'ready',data,total:collection.total,metadata,message:'',analytical:collection};
}

export async function completeAnalyticalForensic(api,options){
 return forensicPresentation(await collectForensic(api,options));
}
