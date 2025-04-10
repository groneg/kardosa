# Kardosa Project Terminal Commands

## Database Operations

### SQLite Commands

#### Delete All Cards Except First Card
```bash
sqlite3 app.db "DELETE FROM card WHERE id != 1;"
```

#### View All Cards
```bash
sqlite3 app.db "SELECT * FROM card;"
```

#### View All Players
```bash
sqlite3 app.db "SELECT * FROM player;"
```

## Python Scripts

### Add Current NBA Players
```bash
python scripts/add_current_players.py
```

### Set Environment Variables (PowerShell)
```powershell
$env:FLASK_APP = "run.py"
$env:FLASK_ENV = "development"
```

### Set Environment Variables (Bash/Zsh)
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
```

## Flask Commands

### Run Development Server
```bash
flask run
```

### Create User (Custom CLI Command)
```bash
flask create-user [username] [email] [password]
```

## Git Operations

### Commit Changes
```bash
git add .
git commit -m "Descriptive commit message"
```

### Push to Repository
```bash
git push origin main
```

## Virtual Environment

### Activate Virtual Environment (Windows)
```powershell
.\venv\Scripts\Activate
```

### Activate Virtual Environment (Unix/Mac)
```bash
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Debugging

### Check Python Version
```bash
python --version
```

### List Installed Packages
```bash
pip list
``` 