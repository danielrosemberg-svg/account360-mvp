from __future__ import annotations

import os
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

import math
from backend.services.accounts import build_account_view, load_accounts, search_accounts
from backend.services.pptx_export import generate_base_deck, generate_deck
from backend.services.docx_export import generate_full360_docx, generate_snapshot_docx
from backend.services.research_context import build_research_context

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
_FIND_ACCOUNT_HTML = PROJECT_ROOT / "exports" / "Find_an_Account.html"

load_dotenv(PROJECT_ROOT / ".env")


def _csv_path() -> Path:
    raw = os.getenv("CSV_PATH", "Data/360 Account overview - Accounts.csv").strip()
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


app = FastAPI(title="Account 360 (local CSV MVP)")

templates = Jinja2Templates(directory=str(BACKEND_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BACKEND_DIR / "static")), name="static")


@app.get("/find", response_class=HTMLResponse)
def find_account_standalone():
    """Serves exports/Find_an_Account.html at the app origin (relative / and /search work on any host/port)."""
    if not _FIND_ACCOUNT_HTML.is_file():
        raise HTTPException(status_code=404, detail="exports/Find_an_Account.html not found")
    return HTMLResponse(_FIND_ACCOUNT_HTML.read_text(encoding="utf-8"))


def get_dataframe():
    path = _csv_path()
    if not path.is_file():
        raise RuntimeError(
            f"CSV file not found: {path}. Set CSV_PATH in .env (see .env.example)."
        )
    return load_accounts(path)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("search.html", {"request": request, "query": ""})


@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str = ""):
    query = (q or "").strip()
    if not query:
        return templates.TemplateResponse(
            "empty_state.html",
            {
                "request": request,
                "title": "Enter a search",
                "message": "Type an account name or Bob company ID, then press Search.",
                "query": query,
            },
        )

    df = get_dataframe()
    hits = search_accounts(df, query)

    if hits.empty:
        return templates.TemplateResponse(
            "empty_state.html",
            {
                "request": request,
                "title": "No accounts found",
                "message": "Try a different spelling, another ID, or a shorter name fragment.",
                "query": query,
            },
        )

    if len(hits) == 1:
        cid = int(hits.iloc[0]["BOB_COMPANY_ID"])
        return RedirectResponse(url=f"/account/{cid}", status_code=302)

    rows_out = []
    for _, r in hits.iterrows():
        rows_out.append(
            {
                "bob_company_id": int(r["BOB_COMPANY_ID"]),
                "account_name": str(r["ACCOUNT_NAME"]),
            }
        )
    return templates.TemplateResponse(
        "account_list.html",
        {"request": request, "query": query, "accounts": rows_out},
    )


_PPTX_NO_CACHE = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
}


@app.get("/api/export/pptx")
def api_export_pptx():
    """Return the Account 360 presentation as a PPTX file download."""
    pptx_bytes = generate_base_deck()
    headers = {
        "Content-Disposition": 'attachment; filename="Account360_Presentation.pptx"',
        **_PPTX_NO_CACHE,
    }
    return StreamingResponse(
        iter([pptx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers=headers,
    )


@app.get("/presentation", response_class=HTMLResponse)
def presentation(request: Request, account_id: Optional[int] = None):
    back_url = f"/account/{account_id}" if account_id else None
    return templates.TemplateResponse(
        "presentation.html",
        {"request": request, "back_url": back_url, "account_id": account_id},
    )


@app.get("/account/{bob_company_id}", response_class=HTMLResponse)
def account_detail(request: Request, bob_company_id: int):
    df = get_dataframe()
    match = df[df["BOB_COMPANY_ID"] == bob_company_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Account not found")

    row = match.iloc[0]
    account_name = str(row["ACCOUNT_NAME"])
    sections = build_account_view(row)
    external = build_research_context(account_name)
    return templates.TemplateResponse(
        "account_360.html",
        {
            "request": request,
            "bob_company_id": bob_company_id,
            "account_name": account_name,
            "sections": sections,
            "research_notice": external["research_notice"],
            "external_enabled": external["external_enabled"],
            "website": external["website"],
            "external_hits": external["external_hits"],
            "references": external["references"],
        },
    )


def _safe_row(row) -> dict:
    """Convert a pandas Series row to a plain string dict, NaN → empty string."""
    import pandas as pd
    return {
        col: ("" if (isinstance(val, float) and math.isnan(val)) or pd.isna(val)
              else str(val).strip())
        for col, val in row.items()
    }


@app.get("/account/{bob_company_id}/snapshot", response_class=HTMLResponse)
def account_snapshot(request: Request, bob_company_id: int):
    df = get_dataframe()
    match = df[df["BOB_COMPANY_ID"] == bob_company_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Account not found")
    row = match.iloc[0]
    return templates.TemplateResponse(
        "snapshot.html",
        {
            "request": request,
            "bob_company_id": bob_company_id,
            "account_name": str(row["ACCOUNT_NAME"]),
            "r": _safe_row(row),
        },
    )


@app.get("/account/{bob_company_id}/full360", response_class=HTMLResponse)
def account_full360(request: Request, bob_company_id: int):
    df = get_dataframe()
    match = df[df["BOB_COMPANY_ID"] == bob_company_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Account not found")
    row = match.iloc[0]
    return templates.TemplateResponse(
        "account360_doc.html",
        {
            "request": request,
            "bob_company_id": bob_company_id,
            "account_name": str(row["ACCOUNT_NAME"]),
            "r": _safe_row(row),
            "sections": build_account_view(row),
        },
    )


@app.get("/account/{bob_company_id}/download/full360-docx")
def download_full360_docx(bob_company_id: int):
    """Download the Full Account 360 as a .docx (drag into Google Drive to convert)."""
    df = get_dataframe()
    match = df[df["BOB_COMPANY_ID"] == bob_company_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Account not found")
    row = _safe_row(match.iloc[0])
    docx_bytes = generate_full360_docx(row)
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_"
                        for c in row.get("ACCOUNT_NAME", str(bob_company_id))).strip()
    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="Account360_{safe_name}.docx"'},
    )


@app.get("/account/{bob_company_id}/download/snapshot-docx")
def download_snapshot_docx(bob_company_id: int):
    """Download the Account Snapshot as a .docx (drag into Google Drive to convert)."""
    df = get_dataframe()
    match = df[df["BOB_COMPANY_ID"] == bob_company_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Account not found")
    row = _safe_row(match.iloc[0])
    docx_bytes = generate_snapshot_docx(row)
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_"
                        for c in row.get("ACCOUNT_NAME", str(bob_company_id))).strip()
    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="Snapshot_{safe_name}.docx"'},
    )


@app.get("/account/{bob_company_id}/download/pptx")
def download_pptx(bob_company_id: int):
    df = get_dataframe()
    match = df[df["BOB_COMPANY_ID"] == bob_company_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Account not found")

    account_name = str(match.iloc[0]["ACCOUNT_NAME"])
    pptx_bytes = generate_deck(account_name)
    # Safe filename: no spaces (avoids odd client paths); strip problematic chars.
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in account_name).strip()
    safe_name = "_".join(s for s in safe_name.split("_") if s) or str(bob_company_id)
    filename = f"Account360_{safe_name}.pptx"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        **_PPTX_NO_CACHE,
    }
    return StreamingResponse(
        iter([pptx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers=headers,
    )
