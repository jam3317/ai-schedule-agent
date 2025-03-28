import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 🔽 .env 파일 로드
load_dotenv()

# 🔑 환경변수에서 API 키 가져오기
client = OpenAI()

def parse_user_query(prompt: str):
    system_prompt = """
너는 일정관리 비서야.
사용자 명령을 분석해서 아래 JSON 형태로 응답해. intent는 아래 중 하나야.

- 일정조회
- 일정등록

각 intent에 필요한 필드는 다음과 같아:

✅ 일정조회:
{
  "intent": "일정조회",
  "start_date": "2025-03-25",
  "end_date": "2025-03-31"
}

✅ 일정등록:
{
  "intent": "일정등록",
  "date": "2025-04-05",
  "description": "회의"
}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"intent": "None", "raw": raw}
