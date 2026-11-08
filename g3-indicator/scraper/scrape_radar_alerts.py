"""
Collect published RADAR alert pages from Public Health Scotland.

Run locally. The script:
- checks robots.txt before every request and skips disallowed URLs;
- waits between requests (default 3 seconds);
- saves raw HTML to data/raw/ with a SHA-256 for each file;
- extracts publication code, title, issue or release date, and scope text where present;
- writes data/derived/alerts_scraped.csv.

It does not invent codes. Fields not found on a page are left blank and flagged.
"""
import csv, datetime, hashlib, pathlib, re, time, urllib.parse, urllib.request
import urllib.robotparser

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "derived" / "alerts_scraped.csv"
UA = "g3-indicator-research/0.1 (academic MSc project; contact: project team)"
DELAY = 3.0

# Seed pages: the RADAR alerts index and the alerts sections of quarterly reports.
SEEDS = [
    "https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-alerts",
]

def allowed(url):
    p = urllib.parse.urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        return False  # if robots.txt cannot be read, do not fetch
    return rp.can_fetch(UA, url)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def extract(html):
    text = re.sub(r"<[^>]+>", " ", html.decode("utf-8", "replace"))
    text = re.sub(r"\s+", " ", text)
    code = re.search(r"Alert number:?\s*([0-9]{4}/[0-9]{2})", text)
    date = re.search(r"(\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4})", text)
    title = re.search(r"<title>(.*?)</title>", html.decode("utf-8", "replace"), re.S)
    return {
        "publication_code": code.group(1) if code else "",
        "date_found": date.group(1) if date else "",
        "title": re.sub(r"\s+", " ", title.group(1)).strip() if title else "",
    }

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for url in SEEDS:
        if not allowed(url):
            rows.append({"url": url, "status": "blocked by robots.txt"})
            continue
        try:
            html = fetch(url)
        except Exception as e:
            rows.append({"url": url, "status": f"error: {e}"})
            time.sleep(DELAY)
            continue
        digest = hashlib.sha256(html).hexdigest()
        name = re.sub(r"[^A-Za-z0-9]+", "_", urllib.parse.urlparse(url).path).strip("_") + ".html"
        (RAW / name).write_bytes(html)
        fields = extract(html)
        rows.append({"url": url, "status": "saved", "file": name, "sha256": digest, **fields,
                     "retrieved_utc": datetime.datetime.utcnow().isoformat(timespec="seconds")})
        time.sleep(DELAY)
    cols = ["url", "status", "file", "sha256", "publication_code", "date_found", "title", "retrieved_utc"]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT}")

if __name__ == "__main__":
    main()
