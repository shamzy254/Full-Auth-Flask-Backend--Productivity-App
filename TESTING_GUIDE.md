# Testing Guide - Backend API

This guide shows you how to test the backend API and integrate it with the provided frontend.

## Testing Methods

### Method 1: Using cURL (Command Line)

**Register a new user:**
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
  }'
```

**Login to get JWT token:**
```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123"
  }'
```

Copy the `access_token` from the response.

**Get your notes (replace TOKEN with your access_token):**
```bash
curl -X GET http://127.0.0.1:5000/notes \
  -H "Authorization: Bearer TOKEN"
```

**Create a new note:**
```bash
curl -X POST http://127.0.0.1:5000/notes \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Note",
    "content": "This is my first note created through the API."
  }'
```

**Update a note (replace ID with note ID):**
```bash
curl -X PATCH http://127.0.0.1:5000/notes/ID \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title"
  }'
```

**Delete a note:**
```bash
curl -X DELETE http://127.0.0.1:5000/notes/ID \
  -H "Authorization: Bearer TOKEN"
```

### Method 2: Using Postman

#### Step 1: Setup Base URL
- Create a new workspace or collection
- Set the base URL to `http://127.0.0.1:5000`

#### Step 2: Register
1. Create new request: **POST** `/auth/register`
2. Go to **Body** → **raw** → **JSON**
3. Paste:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```
4. Click **Send**

#### Step 3: Login and Get Token
1. Create new request: **POST** `/auth/login`
2. Body → raw → JSON:
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```
3. Click **Send**
4. Copy the `access_token` value from response

#### Step 4: Set Authorization for All Requests
1. Go to **Authorization** tab
2. Type: Select **Bearer Token**
3. Token: Paste your `access_token`
4. This will apply to all requests in the collection

#### Step 5: Test Note Endpoints

**Get notes:**
- Request type: **GET**
- URL: `/notes`
- Send

**Create note:**
- Request type: **POST**
- URL: `/notes`
- Body → raw → JSON:
```json
{
  "title": "My Test Note",
  "content": "This is a test note."
}
```
- Send

**Update note:**
- Request type: **PATCH**
- URL: `/notes/1` (replace 1 with actual note ID)
- Body → raw → JSON:
```json
{
  "title": "Updated Title",
  "content": "Updated content"
}
```
- Send

**Delete note:**
- Request type: **DELETE**
- URL: `/notes/1`
- Send

### Method 3: Using the Provided Frontend

#### JWT Frontend Integration

The backend is configured to work with JWT frontend clients. Here's how to integrate:

1. **Clone the frontend repository:**
   ```bash
   git clone https://github.com/learn-co-curriculum/flask-c10-summative-lab-sessions-and-jwt-clients.git
   cd flask-c10-summative-lab-sessions-and-jwt-clients
   ```

2. **Choose the JWT client folder** (not the sessions folder)

3. **Update API endpoint in frontend:**
   Look for configuration file (usually `config.js`, `.env`, or similar) and set:
   ```
   API_URL = "http://127.0.0.1:5000"
   ```

4. **Start the frontend** (check frontend README for commands)

5. **Test the flow:**
   - Register a new account
   - Login
   - Create, read, update, delete notes
   - Try accessing notes on another logged-in session (should fail)

#### Session Frontend Integration

This backend uses JWT, not sessions. Use the **JWT client** version, not the sessions version.

## Test Scenarios

### Scenario 1: Complete User Journey

```bash
# 1. Register
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"pass123"}'

# 2. Login (copy the token)
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"pass123"}'

# 3. Get profile
curl -X GET http://127.0.0.1:5000/auth/profile \
  -H "Authorization: Bearer <TOKEN>"

# 4. Create a note
curl -X POST http://127.0.0.1:5000/notes \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Shopping List","content":"Milk, Eggs, Bread"}'

# 5. Get all notes
curl -X GET http://127.0.0.1:5000/notes \
  -H "Authorization: Bearer <TOKEN>"

# 6. Logout (just discard the token on client side)
```

### Scenario 2: Access Control

Test that users can't access other users' notes:

```bash
# User 1 creates a note
TOKEN1=$(curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"password123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Get User 1's notes (returns note ID 1)
curl -X GET http://127.0.0.1:5000/notes \
  -H "Authorization: Bearer $TOKEN1"

# User 2 tries to access User 1's note
TOKEN2=$(curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user2@example.com","password":"password123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# This should return 403 Forbidden
curl -X GET http://127.0.0.1:5000/notes/1 \
  -H "Authorization: Bearer $TOKEN2"
```

### Scenario 3: Pagination

```bash
# Get first page (10 items)
curl -X GET "http://127.0.0.1:5000/notes?page=1&per_page=10" \
  -H "Authorization: Bearer <TOKEN>"

# Get second page
curl -X GET "http://127.0.0.1:5000/notes?page=2&per_page=10" \
  -H "Authorization: Bearer <TOKEN>"

# Get more items per page (max 50)
curl -X GET "http://127.0.0.1:5000/notes?page=1&per_page=25" \
  -H "Authorization: Bearer <TOKEN>"
```

## Expected HTTP Status Codes

### Success Responses
- **200 OK**: GET, PATCH, POST logout, etc.
- **201 Created**: POST register, POST notes

### Client Error Responses
- **400 Bad Request**: Validation errors, missing fields
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Accessing another user's note
- **404 Not Found**: Note or user doesn't exist

### Server Error Responses
- **500 Internal Server Error**: Server-side errors

## Common Issues & Solutions

### Issue: "Invalid token" Error
**Solution:** Make sure you're using the exact token from login response, formatted as:
```
Authorization: Bearer <your_token_here>
```

### Issue: Empty token in cURL
**Solution:** Make sure you're extracting the token correctly from the JSON response

### Issue: "Note not found" when accessing note
**Solution:** Verify the note ID is correct. Each user has their own notes.

### Issue: Pagination not working
**Solution:** Make sure the query parameters are formatted correctly:
```
?page=1&per_page=10
```

## Performance Testing

### Test with Multiple Notes

```bash
# Create 50 notes quickly
for i in {1..50}; do
  curl -X POST http://127.0.0.1:5000/notes \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d "{\"title\":\"Note $i\",\"content\":\"Content for note $i\"}"
done

# Test pagination with all 50 notes
curl -X GET "http://127.0.0.1:5000/notes?page=1&per_page=10" \
  -H "Authorization: Bearer <TOKEN>"
```

## Automated Testing

Run the built-in test suite:

```bash
# All tests
pipenv run pytest test_api.py -v

# Specific test class
pipenv run pytest test_api.py::TestAuth -v

# Specific test
pipenv run pytest test_api.py::TestAuth::test_login_success -v

# With coverage report
pipenv run pytest test_api.py --cov=. --cov-report=html
```

## Debug Mode

To enable detailed error messages:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
pipenv run flask run
```

## Checking Database State

```bash
# View all users
pipenv run python -c "
from app import create_app
from models import db, User
app = create_app()
with app.app_context():
    users = User.query.all()
    for u in users:
        print(f'{u.username} ({u.email}): {len(u.notes)} notes')
"

# View a specific user's notes
pipenv run python -c "
from app import create_app
from models import db, User
app = create_app()
with app.app_context():
    user = User.query.filter_by(username='user1').first()
    if user:
        for note in user.notes:
            print(f'Note {note.id}: {note.title}')
"
```

## Integration Checklist

- [ ] Backend running on http://127.0.0.1:5000
- [ ] Database initialized with `flask db upgrade`
- [ ] Test data seeded with `python seed.py`
- [ ] All tests passing: `pytest test_api.py -v`
- [ ] Can register new user
- [ ] Can login and get JWT token
- [ ] Can create notes
- [ ] Can read notes (with pagination)
- [ ] Can update notes
- [ ] Can delete notes
- [ ] Access control works (can't access others' notes)
- [ ] Frontend connected and working
- [ ] Error handling working correctly

## Support

For more detailed information:
- See [README.md](README.md) for complete API documentation
- See [QUICKSTART.md](QUICKSTART.md) for setup guide
- See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture details
