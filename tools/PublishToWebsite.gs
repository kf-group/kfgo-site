/**
 * kfGo Packages → kfgo.in
 * Adds a "kfGo website" menu to the kfGo_Packages_Database sheet.
 * "Publish to website" sends every row with is_enabled = TRUE (public columns only)
 * to github.com/kf-group/kfgo-site/data/packages.json. GitHub then rebuilds kfgo.in automatically.
 *
 * One-time setup: Extensions → Apps Script → Project Settings → Script properties →
 * add GITHUB_TOKEN = a fine-grained token with "Contents: Read and write" on kf-group/kfgo-site only.
 */
const REPO = 'kf-group/kfgo-site';
const PATH = 'data/packages.json';
const SHEET = 'Packages';
const PUBLIC_COLS = ['Package_ID','State','Origin_District','Origin_City','Package_Name','Short_Name','Type','Category','Headline','Duration','Days','Nights','Km',
  'Interstate','One_Way','Shared_Seat_INR','Price_From_INR','Price_Hatchback_INR','Price_Sedan_INR','Price_MPV_INR','Price_Premium_SUV_INR','Price_Traveller_INR',
  'Description','Highlights','Itinerary','Good_To_Know','Inclusions','Exclusions','What_To_Carry','is_enabled'];

function onOpen() {
  SpreadsheetApp.getUi().createMenu('kfGo website').addItem('Publish to website', 'publishToWebsite').addToUi();
}

function publishToWebsite() {
  const sh = SpreadsheetApp.getActive().getSheetByName(SHEET);
  const values = sh.getDataRange().getDisplayValues();
  const head = values[0];
  const idx = PUBLIC_COLS.map(c => head.indexOf(c));
  const en = head.indexOf('is_enabled');
  const rows = values.slice(1).filter(r => String(r[en]).toUpperCase() === 'TRUE' && r[0]);
  const out = rows.map(r => { const o = {}; PUBLIC_COLS.forEach((c, i) => o[c] = idx[i] >= 0 ? String(r[idx[i]]).trim() : ''); return o; });
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('Add GITHUB_TOKEN in Project Settings → Script properties first.');
  const api = 'https://api.github.com/repos/' + REPO + '/contents/' + PATH;
  const h = { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json' };
  let sha = null;
  const cur = UrlFetchApp.fetch(api, { headers: h, muteHttpExceptions: true });
  if (cur.getResponseCode() === 200) sha = JSON.parse(cur.getContentText()).sha;
  const body = { message: 'Publish ' + out.length + ' packages from sheet', content: Utilities.base64Encode(JSON.stringify(out), Utilities.Charset.UTF_8) };
  if (sha) body.sha = sha;
  const res = UrlFetchApp.fetch(api, { method: 'put', headers: h, contentType: 'application/json', payload: JSON.stringify(body), muteHttpExceptions: true });
  if (res.getResponseCode() >= 300) throw new Error('GitHub said ' + res.getResponseCode() + ': ' + res.getContentText().slice(0, 300));
  SpreadsheetApp.getActive().toast(out.length + ' packages published. kfgo.in updates in about 2 minutes.', 'kfGo website', 8);
}
