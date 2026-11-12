"""Strict, read-only validation of the frozen national mortality series."""
import hashlib
import json
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / 'g3-indicator/public/data/quarterly_input_table.json'
WORKBOOK = ROOT / 'datasets/Group3_Item2_Data/police_suspected_drug_deaths_Jan2017-Dec2025.xlsx'
SOURCE_URL = 'https://www.gov.scot/publications/suspected-drug-deaths-scotland-october-december-2025/'


def period(index):
    return f'{index // 4} Q{index % 4 + 1}'


def validate(rows):
    if not rows:
        raise ValueError('Mortality series is empty')
    indices = []
    for row in rows:
        year, quarter, value = row['year'], row['quarter'], row['suspected_deaths']
        if any(type(v) is not int for v in (year, quarter, value)):
            raise ValueError('Year, quarter and count must be integers, not missing or boolean values')
        if not 2000 <= year <= 2100 or not 1 <= quarter <= 4 or value < 0:
            raise ValueError('Invalid year, quarter or negative count')
        indices.append(year * 4 + quarter - 1)
    if len(set(indices)) != len(indices):
        raise ValueError('Duplicate quarter')
    if indices != sorted(indices):
        raise ValueError('Series must already be in chronological order; not silently sorting')
    if indices != list(range(indices[0], indices[-1] + 1)):
        raise ValueError('Missing quarter; interpolation is not permitted')
    return rows


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def integer(value):
    if type(value) is int:
        return value
    if isinstance(value, str) and value.isascii() and value.isdigit():
        return int(value)
    raise ValueError('Expected an integer or digit-only string; no silent coercion')


def load_verified():
    raw = json.loads(FROZEN.read_text(encoding='utf-8-sig'))
    rows = []
    for row in raw:
        # Reject fractional/missing/non-numeric strings instead of coercing them.
        if row['quarter'] not in ('Q1', 'Q2', 'Q3', 'Q4'):
            raise ValueError('Invalid frozen quarter label')
        year = integer(row['year'])
        quarter = int(row['quarter'][1:])
        if row['calendar_quarter'] != f'{year} Q{quarter}':
            raise ValueError('Inconsistent frozen period label')
        rows.append(dict(year=year, quarter=quarter, suspected_deaths=integer(row['police_suspected_deaths'])))
    validate(rows)
    if len(rows) != 36 or (rows[0]['year'], rows[0]['quarter']) != (2017, 1) or (rows[-1]['year'], rows[-1]['quarter']) != (2025, 4):
        raise ValueError('Unexpected frozen research coverage')

    workbook = load_workbook(WORKBOOK, read_only=True, data_only=True)
    try:
        sheet = workbook['A - Police Division']
        total_rows = [r for r in sheet.iter_rows(values_only=True) if r[0] == 'Total']
        if len(total_rows) != 1:
            raise ValueError('Expected exactly one national Total row')
        cells = total_rows[0][1:37]
        if any(type(value) not in (int, float) or int(value) != value for value in cells):
            raise ValueError('Invalid national source count')
        if list(cells) != [row['suspected_deaths'] for row in rows]:
            raise ValueError('Source workbook differs from frozen mortality counts')
        # Validate merged year headers and explicit quarter labels, not just counts.
        header_year = None
        names = ['January to March', 'April to June', 'July to September', 'October to December']
        for column, observation in enumerate(rows, 2):
            header_year = sheet.cell(3, column).value or header_year
            if int(header_year) != observation['year'] or sheet.cell(4, column).value != names[observation['quarter'] - 1]:
                raise ValueError('Source workbook period headers do not align')
    finally:
        workbook.close()
    metadata = dict(
        geography='Scotland national total', outcome='Police Scotland suspected drug deaths',
        source_url=SOURCE_URL, observations=len(rows), first_period='2017 Q1', data_cutoff='2025 Q4',
        validation='36 counts and period headers exactly match source workbook; no interpolation',
        sources={str(p.relative_to(ROOT)).replace('\\', '/'): sha256(p) for p in (FROZEN, WORKBOOK)},
    )
    return rows, metadata
