"""Read-only public release evidence. Stores headers and shapes, never datasets or credentials."""
import concurrent.futures
import datetime
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

BASE = 'https://scotland-drug-harm-api.onrender.com/api/v1'
ROUTES = ['health', 'overview', 'geographies', 'analytical/v1/mortality-trends?limit=1',
          'analytical/v1/forensic-toxicology?limit=1', 'mortality/annual?limit=1',
          'toxicology/assist?limit=1', 'toxicology/treatment?limit=1', 'geography/inverclyde?limit=1',
          'geography/comparisons?limit=1', 'anomalies?limit=1', 'anomalies/models?limit=1',
          'monitoring/results?limit=1', 'forecasting/models?limit=1', 'forecasting/results?limit=1',
          'sources?limit=1', 'reports', 'exports?resource=forecast_models&format=json&limit=1',
          'database/v1/naloxone-activity?limit=1']
ASSETS = ['favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'og-image.png',
          'brand/sdhi-logo.svg', 'brand/sdhi-logo-dark.svg', 'brand/sdhi-icon.svg',
          'brand/sdhi-icon-192.png', 'brand/sdhi-icon-512.png']


def check(url):
    record = {'url': url}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'SDHI-read-only-release-check'})
        try:
            response = urllib.request.urlopen(request, timeout=60)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = response.read()
            record.update(status=response.status, content_type=response.headers.get('Content-Type', ''),
                          resolved_url=response.url, revision=response.headers.get('X-SDHI-Revision'),
                          bytes=len(body))
        if 'json' in record['content_type']:
            data = json.loads(body)
            rows = data.get('data', data.get('observations', []))
            record.update(state=data.get('state'), total=data.get('total'), returned=len(rows) if isinstance(rows, list) else None,
                          has_expected_data=200 <= record['status'] < 300 and bool(rows),
                          first_record_fields=sorted(rows[0]) if isinstance(rows, list) and rows and isinstance(rows[0], dict) else [])
            message = data.get('message', '')
            if record['status'] >= 400:
                # Only persist the application's known generic messages; no arbitrary server payloads.
                record['error'] = message if message in [
                    'Verified analytical resource unavailable; check server artifact integrity',
                    'Request could not be completed safely'] else 'Public request failed; response body omitted'
        elif 'text/html' in record['content_type'] and record['status'] == 200:
            html = body.decode('utf-8', errors='replace')
            record['title'] = re.findall(r'<title>(.*?)</title>', html)
            record['canonical'] = re.findall(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', html)
            record['social_keys'] = re.findall(r'(?:property|name)="((?:og:|twitter:)[^"]+)"', html)
            record['scripts'] = re.findall(r'<script[^>]+src="([^"]+)"', html)
    except Exception as error:
        record['transport_error'] = type(error).__name__
    return record


if __name__ == '__main__':
    output = Path('docs/evidence/task08s-phase5')
    output.mkdir(parents=True, exist_ok=True)
    urls = [BASE + '/' + route for route in ROUTES]
    urls += ['https://sdhi.cc/', 'https://www.sdhi.cc/']
    urls += ['https://sdhi.cc/' + asset for asset in ASSETS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        first = list(executor.map(check, urls))
    retry = [check(item['url']) for item in first if item.get('status', 0) >= 500 or 'transport_error' in item]
    result = {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Existing public deployment; no release was published', 'first_attempt': first, 'retry': retry}
    (output / 'public-endpoints.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    for item in first:
        print(item['url'], item.get('status', item.get('transport_error')), item.get('state', ''), item.get('revision', ''))
    print('Retries:', len(retry))
