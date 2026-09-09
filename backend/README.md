Backend (FastAPI). Wszystkie poniższe komendy uruchamiane z wnętrza `backend/`
(`cd backend` po sklonowaniu repo — repo jest monorepo z `backend/` i `frontend/`).

Python versja 3.14

Tworzenie venv
python.exe -m venv venv
D:\Python\3.14\python.exe -m venv venv

// Instalacja pakietow
.\venv\Scripts\python.exe -m pip install -r requirements.txt
(w venv)

// Zapisywanie nowej konfiguracji pakietow
.\venv\Scripts\python.exe -m pip freeze > requirements.txt (musi byc wywolane w venv)

Aby skorzysta z venv w powershell
.\venv\Scripts\Activate.ps1

Aby skorzysta z venv w ubuntu terminal
source .\venv\bin\activate




Aby uruchomi aplikacje
.\venv\Scripts\python.exe .\main.py




// Migracje
alembic revision --autogenerate -m "opis zmiany" - dodawanie migracji
alembic upgrade head --sql      - test updatu
alembic upgrade head            - aplikowanie migracji


alembic upgrade +1 - migracja do przodu
alembic upgrade <revision_id> - konkretna
alembic downgrade -1 - migracja do tylu

alembic history - lista migracji
alembic current - aktualna wersja db
alembic downgrade base
