### FastAPI 프로젝트 구조
├── main.py
├── database.py
├── models.py
├── domain
│   ├── answer/
│   ├── question/
│   └── user/
└── frontend

### venv 설정 
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

### alembic
- 리비전 파일은 git으로 관리해야 함
- env.py 수정 
```python
# 1. env 설정
from dotenv import load_dotenv

load_dotenv()

# 2. models 설정
import models

target_metadata = models.Base.metadata
```

```shell
# 최초 설정
alembic init migrations

# 새로운 리비전(마이그레이션) 생성
alembic revision --autogenerate -m "create users table" # -> 이 명령은 models.py의 변경사항을 감지해서 자동으로 마이그레이션 파일을 생성

# 마이그레이션 실행 (가장 최신 버전으로)
alembic upgrade head # -> 실제 데이터베이스에 테이블이 생성됨

# 특정 리비전으로 이동
alembic upgrade {revision_id}

# 이전 버전으로 롤백
alembic downgrade -1

# 현재 리비전 확인
alembic current

# 마이그레이션 히스토리 보기
alembic history
```

### 의존성 주입
### Pydantic
### 라우터에 Pydantic 적용하기

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