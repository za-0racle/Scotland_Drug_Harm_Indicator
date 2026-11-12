"""Existing results are contextual records, never relabelled as chemical detections."""
import csv
import json
from .extract import ROOT,sha

NRS_URL='https://www.nrscotland.gov.uk/publications/drug-related-deaths-in-scotland-2024/'
PHS_ROOT='https://publichealthscotland.scot/'

def chronology():
    # Reuse verified references from the feasibility assessment, without re-dating the frozen list.
    return [
      dict(type='original_official_issue',date='2023-01-24',subject='Nitazene-type drugs',scope='Scotland dissemination',reference=PHS_ROOT+'publications/rapid-action-drug-alerts-and-response-radar-alert-nitazenes/rapid-action-drug-alerts-and-response-radar-alert-nitazenes-version-20/public-health-alert-for-action-nitazene-type-drugs-in-scotland/'),
      dict(type='original_official_issue',date='2023-07-05',subject='Bromazolam',scope='Scotland dissemination',reference=PHS_ROOT+'publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-october-2023/'),
      dict(type='original_official_issue',date='2024-05-09',subject='Xylazine',scope='Scotland dissemination',reference=PHS_ROOT+'news/2024/may/radar-alert-issued-on-new-synthetic-drug-xylazine/'),
      *[dict(type='nitazene_alert_update',date=date,subject='Nitazene alert version '+version,scope='Scotland dissemination',reference=PHS_ROOT+'publications/rapid-action-drug-alerts-and-response-radar-alert-nitazenes/rapid-action-drug-alerts-and-response-radar-alert-nitazenes-version-20/public-health-alert-for-action-nitazene-type-drugs-in-scotland/') for date,version in [('2023-03-29','1.1'),('2023-11-20','1.2'),('2024-07-08','1.3'),('2025-01-16','1.4'),('2025-08-12','2.0')]],
      dict(type='source_publication',date='2024-08-20',subject='NRS edition through registration year 2023',scope='Scotland',reference='workbook Cover_sheet'),
      dict(type='source_publication',date='2025-09-02',subject='NRS edition through registration year 2024',scope='Scotland',reference=NRS_URL),
      dict(type='later_alert_version',date='2026-02-05',subject='New benzodiazepines / medetomidine version 2.0',scope='Scotland dissemination',reference=PHS_ROOT+'news/2026/february/phs-urges-caution-following-reports-of-increased-harm-from-changes-in-scotland-s-drug-supply/'),
      dict(type='page_last_update_not_first_issue',date='2026-07-14',subject='New benzodiazepines / medetomidine page updates',scope='Scotland dissemination',reference='See verified links in analysis/early_warning_feasibility/FEASIBILITY_REPORT.md'),
    ]

def existing_context():
    paths=['analysis/phase4/outputs/forensic_counts.csv','analysis/phase5/outputs/anomaly_results.csv','analysis/phase5/outputs/sensitivity_results.csv','analysis/phase5c/outputs/enhanced_model_results.csv','analysis/phase5c/outputs/summary.json','analysis/early_warning_feasibility/FEASIBILITY_REPORT.md','g3-indicator/data/derived/ALERT_LIST_2022_2026.csv']
    tables=[]
    for path in paths[:4]:
        with (ROOT/path).open(encoding='utf-8',newline='') as handle:tables.append(list(csv.DictReader(handle)))
    def key(r):return r.get('indicator_id'),r.get('geography'),r.get('period')
    primary={key(r):r for r in tables[1]};sensitivity={key(r):r for r in tables[2]};enhanced={key(r):r for r in tables[3] if r['method']=='nb2_moments'}
    result=[]
    for row in tables[0]:
        if row['indicator_id'] not in ('forensic:Opioids','forensic:Street Benzodiazepines','forensic:Prescribable Benzodiazepines'):continue
        k=key(row);result.append(dict(original_phase4_row=row,original_phase5_row=primary.get(k),original_sensitivity_row=sensitivity.get(k),original_nb2_moments_row=enhanced.get(k),relationship='Broad-group context only; death-quarter testing counts versus annual registration-year substance involvement; not matched cases, chemical identification or corroboration'))
    return result,json.loads((ROOT/paths[4]).read_text()),{path:sha(ROOT/path) for path in paths}
