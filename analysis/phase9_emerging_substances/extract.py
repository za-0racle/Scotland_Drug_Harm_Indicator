"""Read NRS cells with explicit definitions, quality states and provenance."""
import hashlib
import math
import re
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

ROOT=Path(__file__).resolve().parents[2]
SOURCES={
 'nrs_drd_deaths_by_individual_substance.xlsx':('2024','2025-09-02',('SUB1a','SUB1b','SUB2a','SUB2b')),
 'nrs_drd_2023_sub1.xlsx':('2023','2024-08-20',('SUB1a','SUB1b')),
 'nrs_drd_2023_sub2.xlsx':('2023','2024-08-20',('SUB2a','SUB2b')),
}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def count(value):
    if value is None or value=='':return None,'missing'
    if isinstance(value,bool):raise ValueError('Boolean is not a count')
    if isinstance(value,str):
        if value.strip() in ('[c]','[s]','*','..'):return None,'suppressed'
        if value.strip() in ('[x]','[z]','-'):return None,'unavailable'
        if re.fullmatch(r'\d+',value.strip()):return int(value),'observed'
        return None,'non_numeric'
    if not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or int(value)!=value:
        raise ValueError('Invalid count')
    return int(value),'observed'

def definition(sheet,year):
    if sheet not in ('SUB1a','SUB1b','SUB2a','SUB2b'):raise ValueError('Unsupported sheet')
    endpoint='drug_misuse' if sheet.startswith('SUB1') else 'drug_poisoning'
    status='present_not_considered_contributory' if sheet.endswith('b') else 'reported_not_necessarily_implicated' if year<2008 else 'implicated_or_potentially_contributing'
    return endpoint,status

def extract(path,vintage,publication_date,sheets):
    path=Path(path);digest=sha(path);workbook=load_workbook(path,read_only=True,data_only=True)
    rows=[];totals=[];metadata=[]
    try:
        cover=' '.join(str(cell) for row in workbook['Cover_sheet'].iter_rows(values_only=True) for cell in row if cell is not None)
        if '2024' not in cover and vintage=='2024':raise ValueError('Wrong workbook vintage')
        expected='2 September 2025' if vintage=='2024' else '20 August 2024'
        if expected not in cover:raise ValueError('Unexpected publication-date metadata')
        for name in sheets:
            if name not in workbook.sheetnames:raise ValueError('Required sheet missing: '+name)
            sheet=workbook[name];raw=list(sheet.iter_rows(values_only=True))
            headings=[i for i,row in enumerate(raw) if row[0]=='Drug / substance name']
            if len(headings)!=1:raise ValueError('Ambiguous substance header')
            header=headings[0];years=[]
            for value in raw[header][1:]:
                match=re.fullmatch(r'(\d{4})(?: \[[a-z]\])?',str(value))
                if not match:raise ValueError('Invalid year header')
                years.append(int(match.group(1)))
            start=2008 if name.endswith('b') else 2000
            if years!=list(range(start,int(vintage)+1)):raise ValueError('Unexpected/nonchronological years')
            description=' '.join(str(c) for row in raw[:header] for c in row if c is not None)
            if name.endswith('b') and 'NOT considered' not in description:raise ValueError('Present-only definition missing')
            if name.endswith('a') and '2008' not in description:raise ValueError('Definition-break metadata missing')
            metadata.append(dict(workbook=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name,sheet=name,header_cell=f'A{header+1}',first_year=years[0],last_year=years[-1],description=description,publication_date=publication_date,source_sha256=digest))
            seen=set();total_rows=0
            for row_number,raw_row in enumerate(raw[header+1:],header+2):
                label=raw_row[0]
                if label is None:
                    if any(v is not None for v in raw_row[1:]):raise ValueError('Unlabelled count row')
                    continue
                if not isinstance(label,str) or label in seen:raise ValueError('Invalid/duplicate original label')
                seen.add(label);is_total=label.startswith('Total number of ')
                if is_total:total_rows+=1
                for column,year in enumerate(years,2):
                    value,quality=count(raw_row[column-1]);endpoint,status=definition(name,year)
                    record=dict(vintage=vintage,publication_date=publication_date,geography='Scotland',year=year,year_header_raw=raw[header][column-1],sheet=name,endpoint=endpoint,reporting_definition=status,substance_label=label,count=value,quality_status=quality,raw_value=raw_row[column-1],source_workbook=metadata[-1]['workbook'],source_sha256=digest,source_cell=f'{get_column_letter(column)}{row_number}',label_cell=f'A{row_number}',year_cell=f'{get_column_letter(column)}{header+1}',label_class='published_total' if is_total else 'original_source_label_identity_not_normalised')
                    (totals if is_total else rows).append(record)
            if total_rows!=1:raise ValueError('Expected one source total per sheet')
    finally:workbook.close()
    return rows,totals,metadata
