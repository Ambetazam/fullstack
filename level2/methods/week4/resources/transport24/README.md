# Transport24

Small 24/7 transportation management application for people and objects.

## Stack

- FastAPI / Python
- PostgreSQL
- HTML/CSS/JavaScript
- Docker Compose
- JWT authentication
- Argon2 password hashing

## Features

- 8 employee accounts
- Employee login
- Customer records
- People transportation services
- Object transportation services
- Service records
- Face-to-face cash payment recording
- Dashboard
- No chatbot
- No GPS package tracking
- Dark gray / black / blue terminal-style UI

## Run

Requirements:

- Docker
- Docker Compose

From this directory:

```bash
docker compose up -d --build
```

Check the API:

```text
http://localhost:8000/api/health
```

API documentation:

```text
http://localhost:8000/docs
```

## Frontend

The frontend is intentionally plain HTML/CSS/JS.

For a quick local frontend server:

```bash
cd frontend
python3 -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

The frontend expects the API at:

```text
http://localhost:8000
```

## Initial accounts

For development only:

```text
employee01 / Transport24-01!
employee02 / Transport24-02!
employee03 / Transport24-03!
employee04 / Transport24-04!
employee05 / Transport24-05!
employee06 / Transport24-06!
employee07 / Transport24-07!
employee08 / Transport24-08!
```

`employee08` is the initial admin.

IMPORTANT: change these passwords and the JWT secret before production.

## Stop

```bash
docker compose down
```

To delete the database volume too:

```bash
docker compose down -v
```

That permanently deletes the PostgreSQL data volume.
