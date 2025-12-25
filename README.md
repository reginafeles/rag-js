# RAG-system for JS #

1. Clone this repository
2. Install requirements.txt:
```commandline
pip install -r requirements.txt
```
2. Create a file `.env` with a token for `GROQ_API_KEY`. It should contain:
```txt
GROQ_API_KEY = gsk_*** #your full API-Token
```
2. Run code in Terminal:
```commandline
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```


