# Poll / Survey API

A robust, production-ready JSON REST API built with Django and Django REST Framework (DRF) that allows users to create polls, cast secure votes with duplicate-prevention constraints, and view live results with automated percentage calculations.

---

## Features

- **Poll Management**: Create polls with 2 to 5 multiple-choice options. Creators can update poll status (`open`/`closed`) or delete their polls.
- **Secure Voting**: Authenticated users can vote exactly once per poll. The system enforces this constraint both at the application logic layer and via database-level unique constraints.
- **Live Results & Percentages**: Dedicated results endpoint computing vote counts and percentage shares per option dynamically.
- **Filtering & Pagination**: Filter polls by status (`?status=open` or `?status=closed`) backed by standard DRF PageNumberPagination (10 items per page).
- **Custom Permissions**: Built-in `IsPollCreator` permission ensuring only poll creators can modify or delete their respective polls.

---

## Project Structure

```text
poll_survey/
├── manage.py
├── README.md
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
