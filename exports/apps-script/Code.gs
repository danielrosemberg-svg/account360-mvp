var SHEET_ID   = "1EyOE_jZg7qU5ofzN7SLiRi3baKSMVraqJlXJw2uR2gQ";
var SHEET_NAME = "Accounts";

function doGet(e) {
  return HtmlService.createHtmlOutputFromFile("Index")
    .setTitle("Account 360")
    .addMetaTag("viewport", "width=device-width, initial-scale=1")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function getFirstSheet() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  return ss.getSheetByName(SHEET_NAME) || ss.getSheets()[0];
}

// Convert all cell values to plain strings (handles Date objects, nulls, etc.)
function serializeRow(headers, row) {
  var obj = {};
  headers.forEach(function(h, i) {
    var v = row[i];
    if (v instanceof Date) {
      obj[h] = Utilities.formatDate(v, Session.getScriptTimeZone(), "yyyy-MM-dd");
    } else if (v === null || v === undefined) {
      obj[h] = "";
    } else {
      obj[h] = String(v);
    }
  });
  return obj;
}

function searchAccounts(query) {
  var q = String(query || "").trim().toLowerCase();
  if (!q) return [];
  var sheet   = getFirstSheet();
  var data    = sheet.getDataRange().getValues();
  var headers = data[0].map(function(h){ return String(h).trim(); });
  var results = [];
  for (var i = 1; i < data.length; i++) {
    var row  = serializeRow(headers, data[i]);
    var nameMatch = (row["ACCOUNT_NAME"] || "").toLowerCase().indexOf(q) !== -1;
    var idMatch   = (row["BOB_COMPANY_ID"] || "") === q;
    if (nameMatch || idMatch) results.push(row);
    if (results.length >= 20) break;
  }
  return results;
}

function getAccountById(id) {
  var sheet   = getFirstSheet();
  var data    = sheet.getDataRange().getValues();
  var headers = data[0].map(function(h){ return String(h).trim(); });
  for (var i = 1; i < data.length; i++) {
    var row = serializeRow(headers, data[i]);
    if (row["BOB_COMPANY_ID"] === String(id)) return row;
  }
  return null;
}

function test() {
  Logger.log(JSON.stringify(searchAccounts("Finalto")));
}
