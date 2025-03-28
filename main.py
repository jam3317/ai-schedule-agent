from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from llm_utils import parse_user_query
import sqlite3
import os


# FastAPI 앱 인스턴스
app = FastAPI()

# 템플릿 & 정적 파일 폴더 설정
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# DB 파일명
db_file = "data.db"

# DB 초기화 함수
def init_db():
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                description TEXT
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS checklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                date TEXT
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS checklist_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checklist_id INTEGER,
                item_name TEXT,
                is_checked INTEGER DEFAULT 0,
                FOREIGN KEY(checklist_id) REFERENCES checklist(id)
            );
        ''')
init_db()

# 홈
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 일정 목록 조회
@app.get("/schedule", response_class=HTMLResponse)
def get_schedule_page(request: Request):
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM schedule ORDER BY date ASC")
        schedules = cur.fetchall()
    return templates.TemplateResponse("schedule.html", {
        "request": request,
        "schedules": schedules
    })

# 일정 등록
@app.post("/schedule")
def post_schedule(date: str = Form(...), description: str = Form(...)):
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO schedule (date, description) VALUES (?, ?)", (date, description))
        conn.commit()
    return RedirectResponse("/schedule", status_code=302)

# 점검일지 목록
@app.get("/checklist", response_class=HTMLResponse)
def get_checklist_page(request: Request):
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM checklist ORDER BY date DESC")
        checklists = cur.fetchall()
    return templates.TemplateResponse("checklist.html", {
        "request": request,
        "checklists": checklists
    })

# 점검일지 등록
@app.post("/checklist")
def post_checklist(title: str = Form(...), date: str = Form(...), items: str = Form(...)):
    item_list = [item.strip() for item in items.split(",") if item.strip()]
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO checklist (title, date) VALUES (?, ?)", (title, date))
        checklist_id = cur.lastrowid
        for item in item_list:
            cur.execute("INSERT INTO checklist_item (checklist_id, item_name) VALUES (?, ?)", (checklist_id, item))
        conn.commit()
    return RedirectResponse("/checklist", status_code=302)

# 점검일지 상세 보기
@app.get("/checklist/{checklist_id}", response_class=HTMLResponse)
def view_checklist(request: Request, checklist_id: int):
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM checklist WHERE id = ?", (checklist_id,))
        checklist = cur.fetchone()
        cur.execute("SELECT * FROM checklist_item WHERE checklist_id = ?", (checklist_id,))
        items = cur.fetchall()
    return templates.TemplateResponse("checklist_detail.html", {
        "request": request,
        "checklist": checklist,
        "items": items
    })

# AI 명령어 입력 및 처리
@app.api_route("/ai", methods=["GET", "POST"], response_class=HTMLResponse)
def ai_execute(request: Request, prompt: str = Form(None)):
    # GET 요청 처리
    if request.method == "GET":
        return templates.TemplateResponse("ai_interface.html", {"request": request})

    # POST 요청 처리
    parsed = parse_user_query(prompt)
    intent = parsed.get("intent")

    if intent == "일정조회":
        start_date = parsed.get("start_date")
        end_date = parsed.get("end_date")

        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()
            if start_date and end_date:
                cur.execute("SELECT date, description FROM schedule WHERE date BETWEEN ? AND ? ORDER BY date ASC", (start_date, end_date))
            else:
                cur.execute("SELECT date, description FROM schedule ORDER BY date ASC")
            schedules = cur.fetchall()

        response_text = "📅 일정 목록:\n" + "\n".join([f"{s[0]} - {s[1]}" for s in schedules]) if schedules else "일정이 없습니다."

    elif intent == "일정등록":
        date = parsed.get("date")
        description = parsed.get("description")

        if not (date and description):
            response_text = "❌ 날짜나 설명이 빠졌어요. 다시 시도해주세요."
        else:
            with sqlite3.connect(db_file) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO schedule (date, description) VALUES (?, ?)", (date, description))
                conn.commit()
            response_text = f"✅ 일정이 등록되었습니다: {date} - {description}"

    else:
        response_text = f"🤔 아직 처리할 수 없는 intent: {intent}"

    return templates.TemplateResponse("ai_interface.html", {
        "request": request,
        "result": response_text,
        "user_input": prompt
    })