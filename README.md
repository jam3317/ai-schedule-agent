# AI Schedule Agent - 시설관리 시스템 POC

AI 기반 자연어 처리를 활용한 일정 관리 및 점검일지 시스템입니다. 아파트케어 서비스 착수 전에 개발한 POC(Proof of Concept) 프로젝트입니다.

## 기능

- **📅 일정 관리**: 일정 등록 및 조회
- **✅ 점검일지**: 시설 점검 체크리스트 작성 및 관리
- **🤖 AI 명령어**: GPT-4를 활용한 자연어 기반 일정 조회 및 등록
  - "3월 25일부터 31일까지 일정을 보여줄래?"
  - "내일 회의 등록해줄래?"

## 기술 스택

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: Jinja2 템플릿, HTML/CSS
- **LLM**: OpenAI GPT-4
- **환경 관리**: python-dotenv

## 프로젝트 구조

```
.
├── main.py              # FastAPI 메인 서버 (라우팅, DB 조작)
├── llm_utils.py         # LLM 통합 (GPT-4 API, 자연어 파싱)
├── requirements.txt     # Python 의존성
├── templates/           # HTML 템플릿
│   ├── index.html       # 홈 페이지
│   ├── schedule.html    # 일정 관리 페이지
│   ├── checklist.html   # 점검일지 목록 페이지
│   ├── checklist_detail.html  # 점검일지 상세 보기
│   └── ai_interface.html      # AI 명령어 인터페이스
├── static/              # 정적 파일 (CSS, JS)
└── data.db              # SQLite 데이터베이스 (자동 생성)
```

### 데이터베이스 스키마

- **schedule**: 일정 정보 (날짜, 설명)
- **checklist**: 점검일지 (제목, 날짜)
- **checklist_item**: 점검 항목 (항목명, 완료 여부)

## 실행 방법

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성 (OpenAI API 키 필요)
# .env
# OPENAI_API_KEY=your_api_key_here
```

### 2. 서버 실행
```bash
uvicorn main:app --reload
```

### 3. 웹 접속
브라우저에서 `http://localhost:8000` 접속

## 주요 API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 홈 페이지 |
| GET/POST | `/schedule` | 일정 조회/등록 |
| GET/POST | `/checklist` | 점검일지 조회/등록 |
| GET | `/checklist/{id}` | 점검일지 상세 보기 |
| GET/POST | `/ai` | AI 명령어 인터페이스 |

## 라이센스

미지정

---

**Note**: 이 프로젝트는 아파트케어 서비스 개발 전의 초기 POC 프로토타입입니다.
