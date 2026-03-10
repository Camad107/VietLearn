from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime, timedelta
import os
import json

from version import VERSION, VERSION_NAME
from database import get_db, init_db
from ocr import extract_text_from_image, parse_vocabulary_lines

app = FastAPI(title="VietLearn", version=VERSION)

BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.on_event("startup")
def startup():
    init_db()


# --- Pages ---

@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(BASE_DIR, "templates", "index.html")) as f:
        return f.read()


# --- API: Version ---

@app.get("/api/version")
def get_version():
    return {"version": VERSION, "name": VERSION_NAME}


# --- API: Vocabulary CRUD ---

@app.get("/api/vocab")
def list_vocab(category: str = "", search: str = ""):
    db = get_db()
    query = "SELECT * FROM vocabulary WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (vietnamese LIKE ? OR french LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY created_at DESC"
    rows = db.execute(query, params).fetchall()
    db.close()
    return [dict(r) for r in rows]


@app.post("/api/vocab")
def add_vocab(vietnamese: str = Form(...), french: str = Form(...),
              category: str = Form(""), notes: str = Form("")):
    db = get_db()
    cur = db.execute(
        "INSERT INTO vocabulary (vietnamese, french, category, notes) VALUES (?, ?, ?, ?)",
        (vietnamese.strip(), french.strip(), category.strip(), notes.strip())
    )
    vocab_id = cur.lastrowid
    db.execute(
        "INSERT INTO review_stats (vocab_id, next_review) VALUES (?, ?)",
        (vocab_id, datetime.now().isoformat())
    )
    db.commit()
    db.close()
    return {"id": vocab_id, "status": "ok"}


@app.put("/api/vocab/{vocab_id}")
async def update_vocab(vocab_id: int, request: Request):
    data = await request.json()
    db = get_db()
    row = db.execute("SELECT id FROM vocabulary WHERE id = ?", (vocab_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, "Not found")
    fields = []
    values = []
    for key in ["vietnamese", "french", "category", "notes", "difficulty"]:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if fields:
        values.append(vocab_id)
        db.execute(f"UPDATE vocabulary SET {', '.join(fields)} WHERE id = ?", values)
        db.commit()
    db.close()
    return {"status": "ok"}


@app.delete("/api/vocab/{vocab_id}")
def delete_vocab(vocab_id: int):
    db = get_db()
    db.execute("DELETE FROM vocabulary WHERE id = ?", (vocab_id,))
    db.commit()
    db.close()
    return {"status": "ok"}


# --- API: Bulk add ---

@app.post("/api/vocab/bulk")
async def bulk_add(request: Request):
    data = await request.json()
    entries = data.get("entries", [])
    db = get_db()
    added = 0
    for e in entries:
        if e.get("vietnamese") and e.get("french"):
            cur = db.execute(
                "INSERT INTO vocabulary (vietnamese, french, category) VALUES (?, ?, ?)",
                (e["vietnamese"].strip(), e["french"].strip(), e.get("category", ""))
            )
            db.execute(
                "INSERT INTO review_stats (vocab_id, next_review) VALUES (?, ?)",
                (cur.lastrowid, datetime.now().isoformat())
            )
            added += 1
    db.commit()
    db.close()
    return {"added": added}


# --- API: OCR Upload ---

@app.post("/api/ocr")
async def ocr_upload(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")

    raw_text = extract_text_from_image(contents, file.filename)
    entries = parse_vocabulary_lines(raw_text)

    return {"raw_text": raw_text, "entries": entries}


# --- API: Categories ---

@app.get("/api/categories")
def list_categories():
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT category FROM vocabulary WHERE category != '' ORDER BY category"
    ).fetchall()
    db.close()
    return [r["category"] for r in rows]


# --- API: Review (spaced repetition) ---

@app.get("/api/review")
def get_review_cards(limit: int = 20, category: str = ""):
    db = get_db()
    query = """
        SELECT v.*, rs.correct, rs.incorrect, rs.ease_factor, rs.interval_days
        FROM vocabulary v
        JOIN review_stats rs ON rs.vocab_id = v.id
        WHERE rs.next_review <= ?
    """
    params = [datetime.now().isoformat()]
    if category:
        query += " AND v.category = ?"
        params.append(category)
    query += " ORDER BY rs.next_review ASC LIMIT ?"
    params.append(limit)
    rows = db.execute(query, params).fetchall()
    db.close()
    if not rows:
        # If no cards due, return random ones
        db = get_db()
        fallback_query = "SELECT v.*, rs.correct, rs.incorrect, rs.ease_factor, rs.interval_days FROM vocabulary v JOIN review_stats rs ON rs.vocab_id = v.id"
        fparams = []
        if category:
            fallback_query += " WHERE v.category = ?"
            fparams.append(category)
        fallback_query += " ORDER BY RANDOM() LIMIT ?"
        fparams.append(limit)
        rows = db.execute(fallback_query, fparams).fetchall()
        db.close()
    return [dict(r) for r in rows]


@app.post("/api/review/{vocab_id}")
async def submit_review(vocab_id: int, request: Request):
    data = await request.json()
    correct = data.get("correct", False)

    db = get_db()
    stats = db.execute("SELECT * FROM review_stats WHERE vocab_id = ?", (vocab_id,)).fetchone()
    if not stats:
        db.close()
        raise HTTPException(404, "Not found")

    ease = stats["ease_factor"]
    interval = stats["interval_days"]

    if correct:
        if interval == 0:
            interval = 1
        elif interval == 1:
            interval = 6
        else:
            interval = int(interval * ease)
        ease = max(1.3, ease + 0.1)
        db.execute(
            "UPDATE review_stats SET correct = correct + 1, ease_factor = ?, interval_days = ?, "
            "last_reviewed = ?, next_review = ? WHERE vocab_id = ?",
            (ease, interval, datetime.now().isoformat(),
             (datetime.now() + timedelta(days=interval)).isoformat(), vocab_id)
        )
    else:
        interval = 0
        ease = max(1.3, ease - 0.2)
        db.execute(
            "UPDATE review_stats SET incorrect = incorrect + 1, ease_factor = ?, interval_days = 0, "
            "last_reviewed = ?, next_review = ? WHERE vocab_id = ?",
            (ease, datetime.now().isoformat(), datetime.now().isoformat(), vocab_id)
        )

    db.commit()
    db.close()
    return {"status": "ok", "next_interval": interval}


# --- API: Stats ---

@app.get("/api/stats")
def get_stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) as c FROM vocabulary").fetchone()["c"]
    reviewed = db.execute("SELECT COUNT(*) as c FROM review_stats WHERE last_reviewed IS NOT NULL").fetchone()["c"]
    due = db.execute(
        "SELECT COUNT(*) as c FROM review_stats WHERE next_review <= ?",
        (datetime.now().isoformat(),)
    ).fetchone()["c"]
    top_correct = db.execute(
        "SELECT v.vietnamese, v.french, rs.correct FROM vocabulary v "
        "JOIN review_stats rs ON rs.vocab_id = v.id ORDER BY rs.correct DESC LIMIT 5"
    ).fetchall()
    top_incorrect = db.execute(
        "SELECT v.vietnamese, v.french, rs.incorrect FROM vocabulary v "
        "JOIN review_stats rs ON rs.vocab_id = v.id WHERE rs.incorrect > 0 ORDER BY rs.incorrect DESC LIMIT 5"
    ).fetchall()
    db.close()
    return {
        "total_vocab": total,
        "reviewed": reviewed,
        "due_today": due,
        "top_correct": [dict(r) for r in top_correct],
        "top_incorrect": [dict(r) for r in top_incorrect],
    }
