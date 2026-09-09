# ai-ec-agent

Monorepo zawierające backend w FastAPI oraz frontend w React.

## Structure

* [`backend/`](backend/README.md) — aplikacja FastAPI w Pythonie. Odpowiada za pełny pipeline:
  `offer → knowledge → strategy → ads/page`, opisany w [`APPLICATION_FLOW.md`](APPLICATION_FLOW.md).
* [`frontend/`](frontend/) — aplikacja React zbudowana przy użyciu Vite + TypeScript.

---

## Installation

### Backend

Przejdź do katalogu backendu:

```powershell
cd backend
```

Utwórz środowisko wirtualne Python 3.10:

```powershell
py -3.10 -m venv venv
```

Jeżeli `py` nie jest dostępne, możesz użyć bezpośredniej ścieżki do Pythona:

```powershell
~\3.10\python.exe -m venv venv
```

Zainstaluj zależności:

```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

### Frontend

Przejdź do katalogu frontendu:

```powershell
cd frontend
```

Zainstaluj zależności:

```powershell
npm install
```

---

## Quick Start

### Backend — Windows PowerShell

Przejdź do katalogu backendu:

```powershell
cd backend
```

Jeżeli PowerShell blokuje uruchamianie skryptów, ustaw politykę tylko dla bieżącej sesji:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Aktywuj środowisko:

```powershell
.\venv\Scripts\Activate.ps1
```

Uruchom backend:

```powershell
python main.py
```

Backend można również uruchomić bez aktywowania środowiska:

```powershell
.\venv\Scripts\python.exe main.py
```

### Backend — Linux / macOS

```bash
cd backend
source venv/bin/activate
python main.py
```

---

### Frontend

Przejdź do katalogu frontendu:

```bash
cd frontend
```

Zainstaluj zależności:

```bash
npm install
```

Skopiuj przykładowy plik konfiguracyjny:

#### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

#### Linux / macOS

```bash
cp .env.example .env
```

W pliku `.env` ustaw adres backendu:

```env
VITE_API_URL=http://localhost:8000
```

Następnie uruchom frontend:

```bash
npm run dev
```

---

## Development

Backend i frontend powinny działać jednocześnie w dwóch osobnych terminalach.

Przykładowo:

**Terminal 1 — Backend**

```powershell
cd backend
.\venv\Scripts\python.exe main.py
```

**Terminal 2 — Frontend**

```powershell
cd frontend
npm run dev
```
