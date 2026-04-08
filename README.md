## API ML Iris (FastAPI + Docker)

API udostepnia endpointy:

- `GET /`
- `GET /health`
- `GET /info`
- `POST /predict`
- `GET /predictions`

## Zmienne srodowiskowe bazy danych

Mozesz ustawic polaczenie do PostgreSQL na dwa sposoby.

1. Przez `DATABASE_URL`:

```powershell
$env:DATABASE_URL="postgresql://mluser:mlpassword@localhost:5432/ml_db"
```

2. Przez osobne zmienne:

```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DB_NAME="ml_db"
$env:DB_USER="mluser"
$env:DB_PASSWORD="mlpassword"
```

Jesli nie ustawisz danych bazy, endpoint `POST /predict` nadal dziala, ale bez zapisu do bazy, a `GET /predictions` zwroci pusta liste.

## Inicjalizacja tabeli

Po ustawieniu zmiennych srodowiskowych uruchom:

```powershell
python init_db.py
```

Skrypt tworzy tabele `predictions`, jesli jeszcze nie istnieje.

## Uruchomienie lokalne

```powershell
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 2
```

## Uruchomienie w Dockerze

Budowa obrazu:

```powershell
docker build -t ml-api .
```

Start aplikacji:

```powershell
docker run --rm -p 8080:8080 ml-api
```

Start aplikacji z konfiguracja bazy:

```powershell
docker run --rm -p 8080:8080 `
  -e DB_HOST=host.docker.internal `
  -e DB_PORT=5432 `
  -e DB_NAME=ml_db `
  -e DB_USER=mluser `
  -e DB_PASSWORD=mlpassword `
  ml-api
```
