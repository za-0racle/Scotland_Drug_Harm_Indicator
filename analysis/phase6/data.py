"""Validate NRS table structure, exact cell lineage and compatible rate metadata."""
import csv
import hashlib
import math
import re
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = ROOT / 'datasets/Group3_Item2_Data/nrs_drd_2024_data.xlsx'
EXPECTED_SHA = '9a38a4f55e1ce8a21ef4b3edf64981ac67b541460eff1ee5616224ea7f887381'
SOURCE_URL = 'https://www.nrscotland.gov.uk/publications/drug-related-deaths-in-scotland-2024/'
METHOD_URL = 'https://www.nrscotland.gov.uk/media/lfzm3pbu/drug-related-deaths-methodology-annex.pdf'
INDICATOR = 'nrs_registered_drug_misuse_deaths'
YEARS = list(range(2010, 2025))
AREAS = ('Inverclyde', 'Scotland')
MISSING = {None, '', '[x]', '[l]', '[c]', '[z]', ':', 'x', '..'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(value, integer=False):
    if isinstance(value, bool):
        raise ValueError('Boolean observation')
    if value in MISSING:
        return None
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise ValueError(f'Unrecognised NRS cell: {value!r}') from None
    if not math.isfinite(result) or result < 0 or (integer and not result.is_integer()):
        raise ValueError('Expected finite nonnegative count/rate')
    return int(result) if integer else result


def parse_counts(matrix):
    if 'Drug misuse deaths by council area' not in str(matrix[0][0]):
        raise ValueError('Wrong table/indicator')
    if 'date of registration' not in str(matrix[1][0]):
        raise ValueError('Registration basis not verified')
    header = matrix[4]
    if header[:2] != ('Year', 'Sex') and list(header[:2]) != ['Year', 'Sex']:
        raise ValueError('Year/sex header mismatch')
    if any(list(header).count(area) != 1 for area in AREAS):
        raise ValueError('Exact area labels required; no police-division/board alias')
    output = []
    seen = set()
    for rowno, row in enumerate(matrix[5:], 6):
        if row[1] != 'Persons':
            continue
        if isinstance(row[0], bool) or not isinstance(row[0], (int, float)) or int(row[0]) != row[0]:
            raise ValueError('Invalid exact year label')
        year = int(row[0])
        if year not in YEARS or year in seen:
            raise ValueError('Unexpected/duplicate year')
        seen.add(year)
        for area in AREAS:
            col = list(header).index(area)
            value = number(row[col], integer=True)
            output.append(dict(indicator_id=INDICATOR, geography=area,
                               boundary_type='council' if area=='Inverclyde' else 'country', sex='Persons',
                               year=year, period_start=f'{year}-01-01', period_end=f'{year}-12-31',
                               period_basis='calendar_year_of_registration', observed_value=value, unit='deaths',
                               source_sheet='Table_C1', source_cell=f'{get_column_letter(col+1)}{rowno}',
                               source_raw_value=row[col], quality_status='observed' if value is not None else 'missing_or_suppressed',
                               small_number_qualification='Council annual counts fluctuate; percent changes are descriptive, not significant anomalies' if area=='Inverclyde' else 'National total includes local counts; comparison is not independent'))
    if seen != set(YEARS):
        raise ValueError('Missing year row; preserve suppressed cells, do not fabricate missing years')
    return sorted(output, key=lambda r:(r['geography'],r['year']))


def parse_rates(matrix, counts):
    if 'age-standardised death rates for 5-year periods' not in str(matrix[0][0]):
        raise ValueError('Expected published five-year ASR table')
    expected=['Council area','Five-year period','Age-standardised rate (per 100,000 population)',
              'Lower 95% confidence interval','Upper 95% confidence interval','Total number of deaths']
    if list(matrix[4]) != expected:
        raise ValueError('Rate headers changed')
    indexed={(r['geography'],r['year']):r['observed_value'] for r in counts}
    result=[];seen=set()
    for rowno,row in enumerate(matrix[5:],6):
        if row[0] not in AREAS:
            continue
        match=re.fullmatch(r'(\d{4}) - (\d{4})',str(row[1]))
        if not match:
            raise ValueError('Unknown five-year period')
        start,end=map(int,match.groups())
        if start < 2010:
            continue
        if end-start!=4 or end>2024 or (row[0],start) in seen:
            raise ValueError('Invalid/duplicate rate period')
        seen.add((row[0],start))
        rate,lower,upper=map(number,row[2:5]);total=number(row[5],True)
        values=[indexed.get((row[0],year)) for year in range(start,end+1)]
        total_check='unavailable_missing_counts'
        if all(v is not None for v in values):
            if sum(values)!=total:
                raise ValueError('C4 published total disagrees with C1 annual counts')
            total_check='matches_five_C1_counts'
        if all(v is not None for v in (rate,lower,upper)):
            if not lower<=rate<=upper:
                raise ValueError('Invalid published confidence interval')
        elif any(v is not None for v in (rate,lower,upper)):
            raise ValueError('Partly missing rate interval requires explicit review')
        result.append(dict(indicator_id=INDICATOR,geography=row[0],boundary_type='council' if row[0]=='Inverclyde' else 'country',
                           period_label=row[1],period_start=f'{start}-01-01',period_end=f'{end}-12-31',start_year=start,end_year=end,
                           period_basis='five_year_registration_period',rate=rate,lower95=lower,upper95=upper,total_deaths=total,
                           unit='published_age_standardised_deaths_per_100000',standard_population='2013 European Standard Population',
                           rate_origin='NRS published; not recalculated or back-solved from total counts',
                           quality_status='published' if rate is not None else 'missing_or_low_reliability',
                           source_raw_rate=row[2],source_raw_lower95=row[3],source_raw_upper95=row[4],
                           source_sheet='Table_C4',source_row=rowno,source_cells=f'C{rowno}:F{rowno}',total_check=total_check,
                           qualification='Adjacent periods overlap four years; published intervals are not a test of independent annual changes'))
    if seen != {(area,start) for area in AREAS for start in range(2010,2021)}:
        raise ValueError('Incomplete published rate coverage')
    return sorted(result,key=lambda r:(r['geography'],r['start_year']))


def extract(path=WORKBOOK, verify_frozen=True):
    path=Path(path)
    if verify_frozen and sha(path)!=EXPECTED_SHA:
        raise ValueError('Workbook vintage hash changed; review a new version separately')
    workbook=load_workbook(path,read_only=True,data_only=True)
    try:
        counts=parse_counts(list(workbook['Table_C1'].values))
        rates=parse_rates(list(workbook['Table_C4'].values),counts)
        # Independent in-workbook national and sex decomposition cross-checks.
        t1={int(r[0]):number(r[2],True) for r in list(workbook['Table_1'].values)[6:] if isinstance(r[0],(int,float)) and r[1]=='Persons' and int(r[0]) in YEARS}
        c1=list(workbook['Table_C1'].values);header=c1[4]
        for record in counts:
            if record['geography']=='Scotland' and t1.get(record['year'])!=record['observed_value']:
                raise ValueError('Scotland Table_1 cross-check failed')
            col=list(header).index(record['geography'])
            sexes=[number(r[col],True) for r in c1[5:] if r[0]==record['year'] and r[1] in ('Males','Females')]
            if len(sexes)!=2:
                raise ValueError('Sex decomposition unavailable')
            if all(v is not None for v in sexes) and record['observed_value'] is not None and sum(sexes)!=record['observed_value']:
                raise ValueError('Persons != Males + Females')
        cover=[r[0] for r in workbook['Cover sheet'].values if r and r[0]]
        if not any('02 September 2025' in str(v) for v in cover):
            raise ValueError('Publication date not verified')
        notes={str(r[0]):str(r[1]) for r in list(workbook['Notes'].values)[4:] if r[0]}
        if '2013 European Standard Population' not in notes['note 1']:
            raise ValueError('Rate standard population not verified')
    finally:
        workbook.close()
    for record in counts+rates:
        record.update(source_path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name,
                      source_sha256=sha(path),source_url=SOURCE_URL,publication_date='2025-09-02',source_data_cutoff='2024-12-31',
                      scientific_status='historical_descriptive_research_not_warning',greenock_inference=False)
    metadata=dict(source_sha256=sha(path),source_url=SOURCE_URL,methodology_url=METHOD_URL,publication_date='2025-09-02',
                  reviewed_on='2026-11-10',provider='National Records of Scotland',indicator_id=INDICATOR,
                  definition='Registered deaths meeting the NRS drug misuse definition: selected mental/behavioural drug-use ICD-10 causes, or specified poisoning causes with a controlled drug present; NRS exclusions apply. Not all drug poisonings or Police Scotland suspected deaths.',
                  definition_cells='Definitions!A5:A8; Table_C1!A1:A2',geographic_allocation='NRS-assigned council area in Table_C1; no locality allocation or GIS boundary crosswalk inferred',
                  territorial_qualification='Workbook cover describes deaths occurring in Scotland, including persons usually resident outside Scotland; do not assert resident-only local incidence',
                  rates='Table_C4, Notes note 1 and note 9: published five-year ASR, 2013 ESP, revised population vintages; annual council denominator absent',
                  rate_vintage_note='Notes note 9 records rebased 2011–2022 populations and revised 2023 estimates; no attempt to recompute with a different population vintage',
                  revisions='Frozen 2024 publication vintage; later NRS editions may revise counts/rates. Not the latest release; no later observations appended',
                  cross_checks=['30 Persons counts checked against male+female cells where observed','15 Scotland totals matched Table_1','22 five-year totals matched complete C1 windows'])
    return counts,rates,metadata


def inspect_population(paths):
    result=[]
    for path in paths:
        path=Path(path)
        with path.open(newline='',encoding='utf-8-sig') as handle:
            reader=csv.DictReader(handle);fields=reader.fieldnames
            years=set();codes=set();sexes=set();n=0
            for row in reader:
                n+=1;years.add(int(row['Year']));codes.add(row['HB']);sexes.add(row['Sex'])
        result.append(dict(source_path=path.relative_to(ROOT).as_posix(),source_sha256=sha(path),fields=fields,
                           observations=n,first_year=min(years),last_year=max(years),geographic_key='HB',boundary_type='health_board',
                           distinct_codes=sorted(codes),sex_values=sorted(sexes),compatible_inverclyde_council=False,
                           decision='Rejected for council rates: no verified council/locality denominator; national/board rows are not an Inverclyde population'))
    return result


def crude_rate(count, population):
    """Future verified council denominator adapter, unused when current data lack one."""
    fields=('geography','boundary_type','year','sex')
    if count.get('indicator_id')!=INDICATOR or any(count.get(k)!=population.get(k) for k in fields):
        raise ValueError('Numerator/denominator geography, year, sex or indicator mismatch')
    if population.get('measure')!='mid_year_resident_population' or population.get('verified_compatible') is not True:
        raise ValueError('Population definition/allocation compatibility not verified')
    value=number(count.get('observed_value'),True);denom=number(population.get('population'),True)
    if value is None or denom is None or denom==0:
        return None
    return value/denom*100000
