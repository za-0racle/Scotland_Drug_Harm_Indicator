import csv
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from backend.config import ROOT

CATALOG={
 'mortality_trends':('phase4','mortality_quarterly.csv'), 'forensic':('phase4','forensic_counts.csv'),
 'assist':('phase4','assist_percentages.csv'), 'treatment':('phase4','treatment_counts.csv'),
 'naloxone':('phase4','naloxone_weekly.csv'), 'anomalies':('phase5','anomaly_results.csv'),
 'sensitivity':('phase5','sensitivity_results.csv'), 'enhanced':('phase5c','enhanced_model_results.csv'),
 'diagnostics':('phase5c','statistical_diagnostics.csv'), 'model_metrics':('phase5c','model_evaluation_metrics.csv'),
 'runs':('phase5c','signal_runs.json'), 'evidence':('phase5c','cross_source_evidence.json'),
 'candidates':('phase5c','cross_source_candidates.json'), 'zero_baseline':('phase5c','zero_baseline_review.json'),
 'summary':('phase5c','summary.json'), 'registry':('phase5c','source_compatibility_registry.json'),
 'gaps':('phase5c','source_gap_register.json'), 'annual':('phase6','validated_geographic_observations.csv'),
 'geographic_trends':('phase6','inverclyde_trends.csv'), 'comparisons':('phase6','registered_scotland_comparisons.csv'),
 'rates':('phase6','published_five_year_rates.csv'), 'rate_comparisons':('phase6','published_rate_comparisons.csv'),
 'case_study':('phase6','dashboard_data_contract.json'), 'geographic_findings':('phase6','research_findings.json'),
 'forecast':('','forecast.json'), 'forecast_models':('','model_metrics.json'),
 'backtest':('','rolling_origin_predictions.csv'), 'forecast_observations':('','validated_mortality.csv'),
}


class ArtifactError(Exception):
    pass


def scalar(value):
    if value=='':return None
    if value in ('True','False'):return value=='True'
    try:
        parsed=json.loads(value)
        return parsed if isinstance(parsed,(int,float,bool,list,dict)) else value
    except (ValueError,TypeError):return value


class ArtifactRepository:
    def __init__(self,root=ROOT):self.root=Path(root)

    def load(self,key):
        if key not in CATALOG:raise ArtifactError('Unknown approved artifact')
        phase,name=CATALOG[key]
        directory=self.root/'analysis'/phase/'outputs' if phase else self.root/'analysis/outputs'
        path=directory/name;manifest=directory/'run_manifest.json'
        try:
            return self._cached(key,path.stat().st_mtime_ns,manifest.stat().st_mtime_ns)
        except (OSError,ValueError,KeyError,TypeError) as error:
            raise ArtifactError('Analytical artifact unavailable or failed integrity/schema validation') from error

    @lru_cache(maxsize=40)
    def _cached(self,key,mtime,manifest_mtime):
        phase,name=CATALOG[key]
        directory=self.root/'analysis'/phase/'outputs' if phase else self.root/'analysis/outputs'
        path=directory/name
        manifest=json.loads((directory/'run_manifest.json').read_text(encoding='utf-8'))
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if manifest['output_hashes'].get(name)!=digest:raise ArtifactError('Artifact checksum mismatch')
        if path.suffix=='.csv':
            with path.open(encoding='utf-8',newline='') as handle:
                data=[{k:scalar(v) for k,v in row.items()} for row in csv.DictReader(handle)]
        else:
            obj=json.loads(path.read_text(encoding='utf-8'));data=obj if isinstance(obj,list) else [obj]
        if not isinstance(data,list) or any(not isinstance(r,dict) for r in data):raise ArtifactError('Invalid artifact record shape')
        if key in ('mortality_trends','forensic','assist','treatment','naloxone','anomalies','annual','geographic_trends'):
            if any(not {'geography','indicator_id','observed_value'}<=r.keys() for r in data):raise ArtifactError('Required observation fields absent')
        meta=dict(resource=key,storage='approved_local_artifact',analytical_version=manifest.get('version',manifest.get('model_version','phase2-1.0.0')),
                  executed_at_utc=manifest.get('executed_at_utc'),artifact_sha256=digest,
                  source_path=path.relative_to(self.root).as_posix(),provenance_manifest=(directory/'run_manifest.json').relative_to(self.root).as_posix(),
                  limitations=['Frozen retrospective research output; not live conditions or a validated warning','Source periods, populations, geographies and measurement definitions must remain distinct'])
        return data,meta
