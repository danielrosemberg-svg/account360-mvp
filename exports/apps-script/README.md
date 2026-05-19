# Account 360 — Google Apps Script Setup

## שלב 1 — העלה את ה-CSV ל-Google Sheets

1. פתח [sheets.google.com](https://sheets.google.com)
2. צור spreadsheet חדש → שם: `Account 360 Data`
3. File → Import → העלה את הקובץ: `Data/360 Account overview - Accounts.csv`
4. בחר: **Replace spreadsheet** + **Comma separator**
5. שנה את שם ה-sheet tab ל: `Accounts`
6. העתק את ה-**Sheet ID** מה-URL (החלק בין `/d/` לבין `/edit`):
   `https://docs.google.com/spreadsheets/d/[SHEET_ID_HERE]/edit`

## שלב 2 — צור Apps Script project

1. פתח [script.google.com](https://script.google.com)
2. לחץ **New project**
3. שם הפרויקט: `Account 360`

## שלב 3 — הכנס את הקבצים

**Code.gs:**
- מחק את הקוד הקיים
- הדבק את כל התוכן מ-`Code.gs`
- החלף `YOUR_GOOGLE_SHEET_ID_HERE` עם ה-Sheet ID שהעתקת

**Index.html:**
- לחץ **+** → **HTML file** → שם: `Index`
- מחק את הקוד הקיים
- הדבק את כל התוכן מ-`Index.html`

## שלב 4 — Deploy כ-Web App

1. לחץ **Deploy** → **New deployment**
2. בחר type: **Web app**
3. הגדרות:
   - Execute as: **Me**
   - Who has access: **Anyone** (או Anyone within HiBob)
4. לחץ **Deploy**
5. העתק את ה-URL שמתקבל — זה הקישור הקבוע שלך

## הערות

- הקישור עובד תמיד — לא צריך להפעיל שרת
- כל עדכון בגיליון Google Sheets מתעדכן אוטומטית
- ניתן לשתף את ה-URL עם כל CSM בארגון
