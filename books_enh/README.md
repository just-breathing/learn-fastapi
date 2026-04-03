# Library Management API

A FastAPI application for managing a library backed by a local SQLite database.

## Stack

- **FastAPI** — routing, validation, automatic docs
- **SQLModel** — ORM (built on SQLAlchemy + Pydantic)
- **SQLite** — local persistent storage (`library.db` created automatically)
- **Pydantic v2** — request/response schemas with validation

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Run the server
uvicorn main:app --reload
```

The SQLite database (`library.db`) is created automatically on first run.

Interactive docs: http://localhost:8000/docs

---

## Project Structure

```
books_enh/
├── main.py               # App entry point, middleware, stats endpoint
├── requirements.txt
├── database/
│   └── db.py             # SQLite engine + session dependency
├── models/
│   └── models.py         # SQLModel table definitions (Book, Member, Loan)
├── schemas/
│   └── schemas.py        # Pydantic request/response schemas
└── routers/
    └── books.py           # /books  — endpoints
```

---

## API Reference

### Books

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/books/` | Add a new book |
| `GET` | `/books/` | List books (search, genre, available_only filters) |
| `GET` | `/books/{id}` | Get a single book |
| `PATCH` | `/books/{id}` | Update book details or copy count |
| `DELETE` | `/books/{id}` | Delete a book (only if no copies are on loan) |


