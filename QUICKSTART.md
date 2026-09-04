# Quick Start Guide

Get the Notes API up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pipenv install
```

## Step 2: Initialize Database

```bash
pipenv run flask db upgrade
```

## Step 3: Seed Test Data (Optional)

```bash
pipenv run python seed.py
```

This creates 5 test users with 5-15 notes each. All use password: `password123`

## Step 4: Run the Server

```bash
pipenv run flask run
```

Server runs at `http://127.0.0.1:5000`

## Step 5: Test an Endpoint

### Option A: Using cURL

Register a new user:
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

Login to get a token:
```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Get your notes (replace TOKEN with the access_token from login):
```bash
curl -X GET http://127.0.0.1:5000/notes \
  -H "Authorization: Bearer TOKEN"
```

### Option B: Using Postman

1. **Create a new request** to `POST http://127.0.0.1:5000/auth/login`
2. **Set Body** to raw JSON:
   ```json
   {
     "email": "user1@example.com",
     "password": "password123"
   }
   ```
3. **Copy** the `access_token` from the response
4. **Create new request** to `GET http://127.0.0.1:5000/notes`
5. **Go to Authorization tab**, select "Bearer Token", paste your token
6. **Send** the request

## Common Commands

### Database

```bash
# Create migration after model changes
pipenv run flask db migrate -m "Description"

# Apply migrations
pipenv run flask db upgrade

# View migration history
pipenv run flask db history

# Downgrade to previous version
pipenv run flask db downgrade
```

### Testing

```bash
# Run all tests
pipenv run pytest

# Run with coverage
pipenv run pytest --cov

# Run specific test
pipenv run pytest tests/test_auth.py
```

### Database

```bash
# Reset database completely
rm app.db
pipenv run flask db upgrade
pipenv run python seed.py
```

## Useful Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/register` | Create new user |
| POST | `/auth/login` | Get JWT token |
| GET | `/auth/profile` | Get current user |
| GET | `/notes` | List your notes (paginated) |
| POST | `/notes` | Create a new note |
| GET | `/notes/<id>` | Get a note by ID |
| PATCH | `/notes/<id>` | Update a note |
| DELETE | `/notes/<id>` | Delete a note |
| GET | `/health` | Check server status |

## Troubleshooting

**Port 5000 already in use?**
```bash
pipenv run flask run --port 5001
```

**Database locked?**
```bash
rm app.db
pipenv run flask db upgrade
pipenv run python seed.py
```

**Issues with Pipenv?**
```bash
# Try reinstalling
pipenv --rm
pipenv install
```

## Next Steps

- Read the full [README.md](README.md) for complete documentation
- Integrate with the provided frontend
- Run tests to ensure everything works
- Deploy to production when ready

Enjoy! 🚀
