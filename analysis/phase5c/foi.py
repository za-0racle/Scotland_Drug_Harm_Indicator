"""Local JSON staging contract; never writes a database or calculates alert metrics."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path

FIELDS = ['issuer','official_alert_id','issue_date','publication_date','event_date_start','event_date_end','detection_date',
          'date_precision','substances','geographic_scope','alert_category','description','source_locator',
          'revision_status','withdrawal_status','record_version','supersedes_record_id','missingness_notes']


def validate(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('records'), list):
        raise ValueError('Expected object with records array and response metadata')
    response = payload.get('response', {})
    if not isinstance(response, dict):
        raise ValueError('Response metadata must be an object')
    problems, staged, seen = [], [], set()
    for i, record in enumerate(payload['records']):
        issues = []
        if not isinstance(record, dict):
            problems.append(dict(row=i, issues=['Record is not an object']))
            continue
        for field in FIELDS:
            if field not in record:
                issues.append('Missing field: '+field)
        for field in ('issue_date','publication_date','event_date_start','event_date_end','detection_date'):
            value = record.get(field)
            if value is not None:
                try:
                    if not isinstance(value,str) or len(value)!=10:
                        raise ValueError()
                    date.fromisoformat(value)
                except ValueError:
                    issues.append('Invalid exact date: '+field+'; keep uncertain raw date in missingness_notes')
        if record.get('revision_status') not in ('original','revised','unknown'):
            issues.append('Invalid revision status')
        if record.get('withdrawal_status') not in ('withdrawn','not_withdrawn','unknown'):
            issues.append('Invalid withdrawal status')
        if record.get('revision_status')=='revised' and not record.get('supersedes_record_id'):
            issues.append('Revision parent unresolved')
        if record.get('revision_status')=='revised' and record.get('supersedes_record_id') not in [r.get('official_alert_id') for r in payload['records'] if isinstance(r,dict)]:
            issues.append('Revision parent absent from batch; historical link requires review')
        if not isinstance(record.get('missingness_notes'),dict):
            issues.append('Missingness notes must be a field-to-reason object')
        for field in ('official_alert_id','issue_date','publication_date','event_date_start','event_date_end','detection_date'):
            if record.get(field) is None and not (isinstance(record.get('missingness_notes'),dict) and record['missingness_notes'].get(field)):
                issues.append('Missing value needs explicit reason: '+field)
        if record.get('date_precision') not in ('day','mixed','unknown'):
            issues.append('Invalid date precision; retain uncertain raw dates in notes')
        if not isinstance(record.get('substances'),list) or not isinstance(record.get('geographic_scope'),dict):
            issues.append('Substances must be a list and geography an explicit scope object')
        for field in ('issuer','alert_category','source_locator','record_version'):
            if not isinstance(record.get(field),str) or not record[field].strip():
                issues.append('Required nonempty field: '+field)
        if not record.get('official_alert_id'):
            issues.append('Official identifier unavailable; local row ID is not an official ID')
        ident = (record.get('issuer'), str(record.get('official_alert_id')), str(record.get('record_version')))
        if ident in seen:
            issues.append('Duplicate alert version')
        seen.add(ident)
        if record.get('event_date_start') and record.get('event_date_end'):
            if str(record['event_date_start']) > str(record['event_date_end']):
                issues.append('Event interval reversed')
        staged.append(dict(local_record_id=f'row-{i+1}', original=record, review_status='quarantined' if issues else 'structurally_valid_pending_review', issues=issues))
    metadata_issues = [f'Missing response metadata: {field}' for field in ('request_reference','received_date','source_sha256','completeness','coverage','limitations') if field not in response]
    if response.get('completeness') not in ('complete_within_stated_scope','partial','unknown',None):
        metadata_issues.append('Invalid completeness decision')
    if not isinstance(response.get('coverage'),dict) or not isinstance(response.get('limitations'),list):
        metadata_issues.append('Coverage must be an explicit scope object; limitations must be a list')
    if response.get('received_date') is not None:
        try:
            date.fromisoformat(response['received_date'])
        except (ValueError,TypeError):
            metadata_issues.append('Invalid response receipt date')
    if 'source_sha256' in response and (not isinstance(response['source_sha256'],str) or len(response['source_sha256'])!=64 or any(c not in '0123456789abcdef' for c in response['source_sha256'])):
        metadata_issues.append('Invalid source hash')
    return dict(response=response, records=staged, rejected_records=problems, metadata_issues=metadata_issues,
                external_validation_eligible=False, status='pending_scientific_compatibility_and_protocol_review',
                negative_labels='Missing records never establish no-alert periods',
                public_export_approved=False, metrics='blocked: no completeness/compatibility/protocol approval implemented')


def stage(input_path, output_path):
    source, target = Path(input_path).resolve(), Path(output_path).resolve()
    if source == target:
        raise ValueError('Preserve original input')
    if target.exists():
        raise ValueError('Use a new output path; staging never overwrites')
    result = validate(json.loads(source.read_text(encoding='utf-8-sig')))
    result['staging_input_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return result


def specification():
    return dict(version='phase5c-1.0.0', input_format='JSON response object and records array; document extraction is a human-reviewed upstream step',
                fields=FIELDS, response_fields=['request_reference','received_date','source_sha256','completeness','coverage','limitations'],
                status='FOI response pending; no real alert records staged',
                raw_preservation='Keep original response/attachments immutable, hashes and extraction page/row locators; do not publish private descriptions',
                unknown_values='null plus missingness_notes; unknown dates are not inferred',
                revisions='Separate versions and parent references; updates are not automatically new alerts',
                metrics_gate='Always false in this phase, including syntactically valid complete responses; independent scientific review and predefined protocol required')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input');parser.add_argument('output')
    args=parser.parse_args()
    stage(args.input,args.output)
