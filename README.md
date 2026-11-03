# Poll / Survey API

A robust, production-ready JSON REST API built with Django and Django REST Framework (DRF) that allows users to create polls, cast secure votes with duplicate-prevention constraints, and view live results with automated percentage calculations.

---

## Features

- **Poll Management**: Create polls with 2 to 5 multiple-choice options. Creators can edit the question, close the poll, or delete it.
- **Secure Voting**: Authenticated users can vote exactly once per poll. The system enforces this constraint both at the application logic layer and via database-level unique constraints.
- **Live Results & Percentages**: Dedicated results endpoint computing vote counts and percentage shares per option dynamically.
- **Filtering & Pagination**: Filter polls by status (`?status=open` or `?status=closed`) backed by standard DRF PageNumberPagination (10 items per page).
- **Custom Permissions**: Built-in `IsPollCreator` permission ensuring only poll creators can modify, close, or delete their respective polls.

---

## Setup

Requires Python 3.12+.

```bash
git clone https://github.com/ajahwisdomagaba/pollingapi.git
cd pollingapi
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

macOS and Linux:

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is at `http://127.0.0.1:8000`. Swagger UI is at `http://127.0.0.1:8000/api/schema/swagger-ui/`.

Get a token, then send it on every poll request as `Authorization: Token <token>`.

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"jane\",\"password\":\"your-password\"}"
```

```json
{ "token": "a1b2c3d4e5f6" }
```

On PowerShell, call `curl.exe` so the command is not sent to `Invoke-WebRequest`.

---

## Endpoints

| Method | Path | Who | Purpose |
|---|---|---|---|
| `POST` | `/api/token/` | Anyone | Exchange username and password for a token |
| `GET` | `/api/polls/` | Any logged-in user | List polls. Filter with `?status=open` or `?status=closed` |
| `POST` | `/api/polls/` | Any logged-in user | Create a poll with 2 to 5 options |
| `GET` | `/api/polls/{id}/` | Any logged-in user | Retrieve one poll |
| `PATCH` | `/api/polls/{id}/` | Creator | Update the question |
| `DELETE` | `/api/polls/{id}/` | Creator | Delete the poll |
| `POST` | `/api/polls/{id}/vote/` | Any logged-in user | Cast one vote while the poll is open |
| `GET` | `/api/polls/{id}/results/` | Any logged-in user | Vote counts and percentages |
| `POST` | `/api/polls/{id}/close/` | Creator | Set status to `closed` |

`PUT /api/polls/{id}/` updates the question the same way as `PATCH`, and it requires `question` in the body.

---

## Sample requests and responses

### List open polls

```bash
curl -H "Authorization: Token a1b2c3d4e5f6" \
  "http://127.0.0.1:8000/api/polls/?status=open"
```

`200`:

```json
{
  "count": 3,
  "next": "http://127.0.0.1:8000/api/polls/?page=2&status=open",
  "previous": null,
  "results": [
    {
      "id": 1,
      "question": "Best language for web dev?",
      "status": "open",
      "options": [
        {"id": 1, "text": "Python", "votes": 12},
        {"id": 2, "text": "JavaScript", "votes": 8}
      ],
      "creator": "jane",
      "my_vote": null,
      "created_at": "2026-11-01T10:30:00Z",
      "updated_at": "2026-11-01T10:30:00Z"
    }
  ]
}
```

### Create a poll

```bash
curl -X POST http://127.0.0.1:8000/api/polls/ \
  -H "Authorization: Token a1b2c3d4e5f6" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Favorite framework?\",\"options\":[\"Django\",\"Flask\",\"FastAPI\"]}"
```

`201`:

```json
{
  "id": 3,
  "question": "Favorite framework?",
  "status": "open",
  "options": [
    {"id": 5, "text": "Django", "votes": 0},
    {"id": 6, "text": "Flask", "votes": 0},
    {"id": 7, "text": "FastAPI", "votes": 0}
  ],
  "creator": "jane",
  "my_vote": null,
  "created_at": "2026-11-02T14:22:00Z",
  "updated_at": "2026-11-02T14:22:00Z"
}
```

`400` when fewer than 2 options are sent:

```json
{"options": ["Must provide at least 2"]}
```

### Vote

```bash
curl -X POST http://127.0.0.1:8000/api/polls/1/vote/ \
  -H "Authorization: Token a1b2c3d4e5f6" \
  -H "Content-Type: application/json" \
  -d "{\"option\":1}"
```

`201`:

```json
{"detail": "Vote successful", "poll_id": 1, "option_id": 1, "option_text": "Python"}
```

`400` when that user has already voted:

```json
{"detail": "You have already voted for this poll"}
```

### Results

```bash
curl -H "Authorization: Token a1b2c3d4e5f6" \
  "http://127.0.0.1:8000/api/polls/1/results/"
```

`200`:

```json
{
  "poll_id": 1,
  "question": "Best language for web dev?",
  "total_votes": 20,
  "results": [
    {"option_id": 1, "option_text": "Python", "votes": 12, "percentage": 60.0},
    {"option_id": 2, "option_text": "JavaScript", "votes": 8, "percentage": 40.0}
  ]
}
```

Request and error details for every route are in [API_CONTRACT.md](API_CONTRACT.md).

---

## Project Structure

```text
poll_survey/
├── manage.py
├── requirements.txt
├── README.md
├── API_CONTRACT.md
├── .gitignore
├── poll_survey/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── pollapi/
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── admin.py
    ├── tests.py
    ├── permissions.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── migrations/
```
