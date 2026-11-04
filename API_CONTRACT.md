# Poll / Survey API Contract

Base URL: `http://127.0.0.1:8000`

All poll endpoints require authentication. Send the token from `POST /api/token/` on every request:

```http
Authorization: Token <token>
Content-Type: application/json
```

Dates are UTC ISO-8601 strings. List results are ordered newest first.

---

## Shared types

### Poll

```json
{
  "id": 1,
  "question": "Best language for web dev?",
  "status": "open",
  "options": [
    { "id": 1, "text": "Python", "votes": 12 },
    { "id": 2, "text": "JavaScript", "votes": 8 }
  ],
  "creator": "jane",
  "my_vote": null,
  "created_at": "2026-11-01T10:30:00Z",
  "updated_at": "2026-11-01T10:30:00Z"
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Assigned by the server. |
| `question` | string | 1–200 characters. |
| `status` | string | `open` or `closed`. New polls are `open`. Clients cannot set this field. |
| `options` | array | 2–5 options. On read, each item has `id`, `text`, and `votes`. |
| `creator` | string | Username of the user who created the poll. |
| `my_vote` | integer or `null` | Option id the current user voted for, or `null`. |
| `created_at` | string | Set when the poll is created. |
| `updated_at` | string | Changes when the poll is updated or closed. |

### Error shapes

Field errors:

```json
{ "question": ["This field is required."] }
```

Single-message errors:

```json
{ "detail": "Not found." }
```

Login errors that are not tied to one field:

```json
{ "non_field_errors": ["Unable to log in with provided credentials."] }
```

### Errors on every protected route

| Status | Body | When |
|---|---|---|
| `401` | `{ "detail": "Authentication credentials were not provided." }` | No `Authorization` header. |
| `401` | `{ "detail": "Invalid token header. No credentials provided." }` | The header is `Token` with no value after it. |
| `401` | `{ "detail": "Invalid token header. Token string should not contain spaces." }` | The token value contains a space. |
| `401` | `{ "detail": "Invalid token header. Token string should not contain invalid characters." }` | The token value is not valid text. |
| `401` | `{ "detail": "Invalid token." }` | The token is unknown. |
| `401` | `{ "detail": "User inactive or deleted." }` | The token belongs to an inactive user. |
| `404` | `{ "detail": "Not found." }` | Poll id does not exist. |
| `405` | `{ "detail": "Method \"PUT\" not allowed." }` | HTTP method is not supported on that URL. The method name in the message changes. |

---

## POST `/api/token/`

Exchange a username and password for a token. This route does not require a token.

### Request

```json
{
  "username": "wisdom",
  "password": "your-password"
}
```

### Success `200`

```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }
```

### Errors

| Status | Body | When |
|---|---|---|
| `400` | `{ "username": ["This field is required."] }` | `username` is missing. `password` returns the same message when it is missing. |
| `400` | `{ "username": ["This field may not be blank."] }` | `username` or `password` is an empty string. |
| `400` | `{ "non_field_errors": ["Unable to log in with provided credentials."] }` | The username and password do not match a user, or the account is inactive. |

---

## GET `/api/`

Authenticated index of the API.

### Success `200`

```json
{
  "polls": "http://127.0.0.1:8000/api/polls/"
}
```

---

## GET `/api/polls/`

List polls. Any authenticated user can read every poll.

### Query parameters

| Name | Notes |
|---|---|
| `status` | `open` or `closed`. Other values return an empty page. |
| `page` | Page number. Defaults to `1`. |
| `page_size` | Items per page. Defaults to `10`. Values above `100` are capped at `100`. |

Example: `GET /api/polls/?status=open&page=1&page_size=10`

### Success `200`

```json
{
  "count": 3,
  "next": "http://localhost:8000/api/polls/?page=2&status=open",
  "previous": null,
  "results": [
    {
      "id": 1,
      "question": "Best language for web dev?",
      "status": "open",
      "options": [
        { "id": 1, "text": "Python", "votes": 12 },
        { "id": 2, "text": "JavaScript", "votes": 8 }
      ],
      "creator": "jane",
      "my_vote": null,
      "created_at": "2026-11-01T10:30:00Z",
      "updated_at": "2026-11-01T10:30:00Z"
    }
  ]
}
```

`next` and `previous` are absolute URLs when another page exists, otherwise `null`.

### Errors

| Status | Body | When |
|---|---|---|
| `404` | `{ "detail": "Invalid page." }` | `page` is less than 1 or past the last page. |

---

## POST `/api/polls/`

Create a poll. The authenticated user becomes `creator`. `status` is always `open`.

### Request

Options may be objects or strings. Send 2 to 5 of them.

```json
{
  "question": "Favorite framework?",
  "options": [
    { "text": "Django" },
    { "text": "Flask" },
    { "text": "FastAPI" }
  ]
}
```

```json
{
  "question": "Favorite framework?",
  "options": ["Django", "Flask", "FastAPI"]
}
```

`id`, `status`, `creator`, `my_vote`, `votes`, `created_at`, and `updated_at` are ignored if a client sends them.

### Success `201`

A Poll object. `my_vote` is `null`. Every option has `votes` set to `0`.

### Errors

| Status | Body | When |
|---|---|---|
| `400` | `{ "question": ["This field is required."] }` | `question` is missing. |
| `400` | `{ "question": ["This field may not be blank."] }` | `question` is empty. |
| `400` | `{ "question": ["Ensure this field has no more than 200 characters."] }` | `question` is longer than 200 characters. |
| `400` | `{ "options": ["Must provide at least 2"] }` | `options` is missing, not a list, or has fewer than 2 items. |
| `400` | `{ "options": ["You cannot have more than 5 options"] }` | More than 5 options. |
| `400` | `{ "options": ["Each option must be a string or an object with text."] }` | An option is not a string or an object with a string `text`. |
| `400` | `{ "options": ["Option text cannot be blank."] }` | An option is empty or only whitespace. |
| `400` | `{ "options": ["Option text cannot be longer than 200 characters."] }` | An option is longer than 200 characters. |

---

## GET `/api/polls/{id}/`

Return one poll. Any authenticated user can read it.

### Success `200`

A Poll object.

### Errors

`401` and `404` from the shared table.

---

## PUT `/api/polls/{id}/`

Replace the editable fields of a poll. Only the creator can do this.

`question` is the only writable field. Options and `status` do not change through this route. Closing a poll is `POST /api/polls/{id}/close/`.

### Request

```json
{ "question": "Best language for web dev?" }
```

### Success `200`

The updated Poll object.

### Errors

| Status | Body | When |
|---|---|---|
| `400` | `{ "question": ["This field is required."] }` | `question` is missing. |
| `400` | `{ "question": ["This field may not be blank."] }` | `question` is empty. |
| `400` | `{ "question": ["Ensure this field has no more than 200 characters."] }` | `question` is longer than 200 characters. |
| `403` | `{ "detail": "You do not have permission to perform this action." }` | The caller did not create the poll. |

---

## PATCH `/api/polls/{id}/`

Update part of a poll. Only the creator can do this. The same fields are writable as `PUT`. Omitted fields stay unchanged.

### Request

```json
{ "question": "Best language for web dev?" }
```

### Success `200`

The updated Poll object.

### Errors

Same `400` question errors as `PUT` when `question` is present and invalid. Same `403` when the caller is not the creator.

---

## DELETE `/api/polls/{id}/`

Delete a poll and its options and votes. Only the creator can do this.

### Success `200`

```json
{"detail": "Poll deleted successfully", "poll_id": 1}
```

### Errors

| Status | Body | When |
|---|---|---|
| `403` | `{ "detail": "You do not have permission to perform this action." }` | The caller did not create the poll. |
| `404` | `{ "detail": "Not found." }` | Poll id does not exist. |

---

## POST `/api/polls/{id}/vote/`

Cast one vote. Any authenticated user can vote, including someone who did not create the poll. Each user can vote once per poll, and only while the poll is `open`.

### Request

```json
{ "option": 1 }
```

`option` is the option id returned on the poll. It must belong to this poll.

### Success `201`

```json
{
  "detail": "Vote successful",
  "poll_id": 1,
  "option_id": 1,
  "option_text": "Python"
}
```

The option's `votes` count increases by 1. Later reads of the poll set `my_vote` to that option id.

### Errors

| Status | Body | When |
|---|---|---|
| `400` | `{ "detail": "Poll is not open for voting" }` | Poll `status` is `closed`. |
| `400` | `{ "detail": "Option ID is required" }` | `option` is missing, `null`, or empty. |
| `400` | `{ "detail": "You have already voted for this poll" }` | This user already has a vote on this poll. |
| `404` | `{ "detail": "Option does not exist" }` | The id is not an option on this poll, or it is not a valid id. |
| `404` | `{ "detail": "Not found." }` | Poll id does not exist. |

---

## POST `/api/polls/{id}/close/`

Close a poll. Only the creator can do this. There is no route to reopen a poll. A closed poll rejects new votes. Results remain available.

### Request

Empty body.

### Success `200`

The Poll object with `"status": "closed"`.

### Errors

| Status | Body | When |
|---|---|---|
| `400` | `{ "detail": "Poll is already closed" }` | The poll is already `closed`. |
| `403` | `{ "detail": "You do not have permission to perform this action." }` | The caller did not create the poll. |
| `404` | `{ "detail": "Not found." }` | Poll id does not exist. |

---

## GET `/api/polls/{id}/results/`

Return the current tally. Any authenticated user can read results for an open or closed poll.

### Success `200`

```json
{
  "poll_id": 1,
  "question": "Best language for web dev?",
  "total_votes": 20,
  "results": [
    {
      "option_id": 1,
      "option_text": "Python",
      "votes": 12,
      "percentage": 60.0
    },
    {
      "option_id": 2,
      "option_text": "JavaScript",
      "votes": 8,
      "percentage": 40.0
    }
  ]
}
```

`percentage` is rounded to two decimal places. When `total_votes` is `0`, every percentage is `0`.

### Errors

`401` and `404` from the shared table.

---

## GET `/api/schema/`

OpenAPI schema for this API. No token is required.

The default response is YAML (`Content-Type: application/vnd.oai.openapi`). Add `?format=json` or send `Accept: application/json` for JSON.

### Success `200`

An OpenAPI document describing `/api/token/`, `/api/polls/`, vote, close, and results. The body is the generated schema, not a poll object.

---

## GET `/api/schema/swagger-ui/`

Swagger UI for the same schema. No token is required. Open this URL in a browser:

`http://127.0.0.1:8000/api/schema/swagger-ui/`

### Success `200`

An HTML page. Swagger loads the schema from `/api/schema/`. Use the **Authorize** button and enter `Token <token>` to call the poll routes from the page.

---

## GET `/api/schema/redoc/`

ReDoc for the same schema. No token is required.

`http://127.0.0.1:8000/api/schema/redoc/`

### Success `200`

An HTML page.

---

## Sample Requests & Responses

Auth header for the poll routes: `Authorization: Token a1b2c3d4e5f6...`

`POST /api/token/`, `GET /api/schema/`, `GET /api/schema/swagger-ui/`, and `GET /api/schema/redoc/` do not use that header.

### GET `/api/polls/`

```bash
curl -H "Authorization: Token a1b2c3d4e5f6" "http://localhost:8000/api/polls/?status=open"
```

`200`:

```json
{
  "count": 3,
  "next": "http://localhost:8000/api/polls/?page=2&status=open",
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

### GET `/api/polls/{id}/`

```bash
curl -H "Authorization: Token a1b2c3d4e5f6" "http://localhost:8000/api/polls/1/"
```

`200`:

```json
{
  "id": 1,
  "question": "Best language for web dev?",
  "status": "open",
  "options": [
    {"id": 1, "text": "Python", "votes": 12},
    {"id": 2, "text": "JavaScript", "votes": 8}
  ],
  "creator": "jane",
  "my_vote": 1,
  "created_at": "2026-11-01T10:30:00Z",
  "updated_at": "2026-11-01T10:30:00Z"
}
```

`my_vote` is `null` if the user has not voted.

### POST `/api/polls/`

```bash
curl -X POST \
  -H "Authorization: Token a1b2c3d4e5f6" \
  -H "Content-Type: application/json" \
  -d '{"question": "Favorite framework?", "options": ["Django", "Flask", "FastAPI"]}' \
  "http://localhost:8000/api/polls/"
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

`400` (too few options):

```json
{"options": ["Must provide at least 2"]}
```

### PATCH `/api/polls/{id}/`

`status` is read-only on this route. Send a new question. Only the creator receives `200`.

```bash
curl -X PATCH \
  -H "Authorization: Token a1b2c3d4e5f6" \
  -H "Content-Type: application/json" \
  -d '{"question": "Best language for web dev?"}' \
  "http://localhost:8000/api/polls/1/"
```

`200`:

```json
{
  "id": 1,
  "question": "Best language for web dev?",
  "status": "open",
  "options": [
    {"id": 1, "text": "Python", "votes": 12},
    {"id": 2, "text": "JavaScript", "votes": 8}
  ],
  "creator": "jane",
  "my_vote": 1,
  "created_at": "2026-11-01T10:30:00Z",
  "updated_at": "2026-11-02T15:00:00Z"
}
```

`403` (not the creator):

```json
{"detail": "You do not have permission to perform this action."}
```

### POST `/api/polls/{id}/close/`

```bash
curl -X POST \
  -H "Authorization: Token a1b2c3d4e5f6" \
  "http://localhost:8000/api/polls/1/close/"
```

`200`:

```json
{
  "id": 1,
  "question": "Best language for web dev?",
  "status": "closed",
  "options": [
    {"id": 1, "text": "Python", "votes": 12},
    {"id": 2, "text": "JavaScript", "votes": 8}
  ],
  "creator": "jane",
  "my_vote": 1,
  "created_at": "2026-11-01T10:30:00Z",
  "updated_at": "2026-11-02T16:00:00Z"
}
```

`403` (not the creator):

```json
{"detail": "You do not have permission to perform this action."}
```

`400` (already closed):

```json
{"detail": "Poll is already closed"}
```

### DELETE `/api/polls/{id}/`

```bash
curl -X DELETE -H "Authorization: Token a1b2c3d4e5f6" "http://localhost:8000/api/polls/1/"
```

`200`:

```json
{"detail": "Poll deleted successfully", "poll_id": 1}
```

`403` (not the creator):

```json
{"detail": "You do not have permission to perform this action."}
```

### POST `/api/polls/{id}/vote/`

```bash
curl -X POST \
  -H "Authorization: Token a1b2c3d4e5f6" \
  -H "Content-Type: application/json" \
  -d '{"option": 1}' \
  "http://localhost:8000/api/polls/1/vote/"
```

`201`:

```json
{"detail": "Vote successful", "poll_id": 1, "option_id": 1, "option_text": "Python"}
```

`400` (already voted):

```json
{"detail": "You have already voted for this poll"}
```

`400` (poll is closed):

```json
{"detail": "Poll is not open for voting"}
```

### GET `/api/polls/{id}/results/`

```bash
curl -H "Authorization: Token a1b2c3d4e5f6" "http://localhost:8000/api/polls/1/results/"
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

