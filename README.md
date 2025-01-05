### Venv 
- C/venvs 이동
- python -m venv llm-fastapi
- IDE settings -> python interpreter 설정
- python -m pip install --upgrade pip

### 설치
    pip install fastapi[all] langchain langchain-openai langchain-community python-dotenv
    pip install "uvicorn[standard]"
    pip install sqlalchemy pymysql python-jose[cryptography] passlib[bcrypt] python-multipart

### 서버 실행
    uvicorn main:app --reload

### 메모
- 유비콘(Uvicorn)은 비동기 호출을 지원하는 파이썬용 웹 서버이다.

### .env
```text
OPENAI_API_KEY=
SECRET_KEY=

DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=
```