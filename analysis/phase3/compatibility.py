"""Conservative outcome gate. Period agreement alone is not definition agreement."""
import calendar
from datetime import date


def compatible_calendar_quarter(record):
    start, end = date.fromisoformat(record['start']), date.fromisoformat(record['end'])
    quarter_month = start.month in (1, 4, 7, 10) and start.day == 1
    end_month = start.month + 2
    exact = quarter_month and end == date(start.year, end_month, calendar.monthrange(start.year, end_month)[1])
    return exact and record.get('definition_compatibility_reviewed') is True and record.get('geography') == 'Scotland national total'
