// Read-only acquisition of public aggregate evidence. No application/DB access.
import { chromium } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const directory = path.join(path.dirname(fileURLToPath(import.meta.url)), 'sources');
fs.mkdirSync(directory, { recursive: true });
const dashboard = 'https://scotland.shinyapps.io/phs-drugs-radar-dashboard/';
const report = 'https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-october-2026/about-this-release/printversion';
const annex = 'https://www.gov.scot/publications/suspected-drug-deaths-scotland-october-december-2025/pages/7/';
const entries = [];
const hash = data => createHash('sha256').update(data).digest('hex');
function save(filename, data, source, extra = {}) {
  fs.writeFileSync(path.join(directory, filename), data);
  entries.push({ filename, canonical_source_url: source, retrieved_at_utc: new Date().toISOString(), sha256: hash(data), ...extra });
}
const browser = await chromium.launch({ channel: process.platform === 'win32' ? 'msedge' : undefined, headless: true });
try {
  const page = await browser.newPage({ acceptDownloads: true });
  for (const [filename, url] of [['radar_october_2026.html', report], ['legacy_methodology_annex.html', annex]]) {
    const response = await page.request.get(url);
    if (!response.ok()) throw new Error(`${filename}: HTTP ${response.status()}`);
    save(filename, await response.body(), url, { http_status: response.status() });
  }
  await page.goto(dashboard, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.getByRole('link', { name: 'Harm indicators', exact: true }).click();
  await page.locator('a').filter({ hasText: /^Suspected drug deaths$/ }).first().click();
  await page.waitForFunction(() => document.body.innerText.includes('25 December 2016'));
  save('dashboard_suspected_deaths.txt', await page.locator('body').innerText(), dashboard,
    { note: 'Rendered live dashboard; weekly series and reporting-method warning.' });
  await page.getByRole('link', { name: 'Download data', exact: true }).first().click();
  await page.locator('#download_dataset').selectOption('Suspected drug deaths', { force: true });
  await page.waitForFunction(() => document.querySelector('#data_download_output')?.getAttribute('href')?.includes('/download/'));
  const downloading = page.waitForEvent('download', { timeout: 45000 });
  await page.locator('#data_download_output').click();
  const download = await downloading;
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  save('suspected_deaths_download.csv', Buffer.concat(chunks), dashboard,
    { dataset_selector: 'Suspected drug deaths', suggested_filename: download.suggestedFilename() });
  fs.writeFileSync(path.join(directory, 'retrieval_manifest.json'), JSON.stringify({ entries }, null, 2) + '\n');
  console.log(JSON.stringify(entries, null, 2));
} finally {
  await browser.close();
}
