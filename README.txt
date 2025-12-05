Aziz AI Super Digital Clone - 6 Core Architecture

Bu loyiha Aziz_AI raqamli kloni uchun backend yadrosidir.

Yadrolar:
1) Personality Engine
2) Memory Engine
3) Chat Engine (GPT-5.1)
4) Internet Agent (Telegram + Instagram)
5) Office Agent (Word / Excel / PowerPoint)
6) Voice + Animation Engine

Backend texnologiyasi:
- FastAPI
- SQLAlchemy
- SQLite (lokal uchun, keyin Railway/PostgreSQL ga oson ko'chadi)

Ishga tushurish (lokal):

    cd AzizAI_Core
    pip install -r requirements.txt
    uvicorn app:app --reload

So'ngra:
- Swagger UI: http://127.0.0.1:8000/docs
- Asosiy status: GET http://127.0.0.1:8000/
- Personality: GET http://127.0.0.1:8000/api/personality/profile
- 6 ta yadro statusi: 
    - /api/memory/status
    - /api/chat/status
    - /api/agent/status
    - /api/office/status
    - /api/voice/status

Eski matn:
Aziz AI Super Digital Clone - 6 Core Architecture

