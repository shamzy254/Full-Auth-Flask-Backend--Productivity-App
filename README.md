# Full Auth Flask Backend - Notes API

A secure, production-ready Flask REST API for managing user notes with JWT authentication. Users can create, read, update, and delete their own notes with full access control and pagination support.

## Project Description

This project implements a complete authentication system and resource management backend for a notes productivity application. The API provides:

- **User Authentication**: Registration and login with JWT tokens
- **User-Owned Resources**: Notes that belong exclusively to each user
- **Full CRUD Operations**: Create, Read, Update, Delete notes with proper HTTP methods
- **Access Control**: Users can only view and modify their own notes
- **Pagination**: Efficient retrieval of notes with configurable page sizes
- **Data Validation**: Input validation using Marshmallow schemas
- **Secure Passwords**: Password hashing with Flask-Bcrypt

## Technology Stack

- **Framework**: Flask 2.2.2
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens) with Flask-JWT-Extended
- **Password Hashing**: Flask-Bcrypt
- **Validation**: Marshmallow
- **Database Migrations**: Flask-Migrate
- **Testing**: Pytest
- **Seed Data**: Faker

## Installation Instructions

### Prerequisites

- Python 3.8 or higher
- Pipenv (or pip and virtualenv)
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Full-Auth-Flask-Backend--Productivity-App
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   ```

3. **Activate the virtual environment**
   ```bash
   pipenv shell
   ```

4. **Initialize the database**
   ```bash
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Seed the database with test data** (optional)
   ```bash
   python seed.py
   ```

## Running the Application

### Development Server

```bash
pipenv run flask run
```

The server will start at `http://127.0.0.1:5000` in debug mode.

### Production Server

For production deployment, use a WSGI server like Gunicorn:

```bash
pipenv install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## Environment Variables

Create a `.env` file in the project root to configure:

```env
FLASK_ENV=development
FLASK_APP=app.py
DATABASE_URL=sqlite:///app.db
JWT_SECRET_KEY=your-secret-key-here
```

**Important**: In production, change the `JWT_SECRET_KEY` to a strong, random value.

## API Endpoints

All endpoints (except `/auth/register` and `/auth/login`) require a valid JWT token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

### Authentication Endpoints

#### Register a New User
- **POST** `/auth/register`
- **Request Body**:
  ```json
  {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "message": "User created successfully",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2026-01-15T10:30:00"
    }
  }
  ```
- **Error Responses**:
  - 400: Username or email already exists, or validation error
  - 500: Server error during user creation

#### Login User
- **POST** `/auth/login`
- **Request Body**:
  ```json
  {
    "email": "john@example.com",
    "password": "securepassword123"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2026-01-15T10:30:00"
    }
  }
  ```
- **Error Responses**:
  - 400: Validation error
  - 401: Invalid email or password

#### Get Current User Profile
- **GET** `/auth/profile`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (200 OK):
  ```json
  {
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2026-01-15T10:30:00"
    }
  }
  ```
- **Error Responses**:
  - 401: Unauthorized (missing or invalid token)
  - 404: User not found

#### Logout User
- **POST** `/auth/logout`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (200 OK):
  ```json
  {
    "message": "Logout successful"
  }
  ```
- **Note**: JWT tokens are stateless. Client should discard the token after logout.

### Notes Endpoints

#### Get All Notes (Paginated)
- **GET** `/notes`
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `page` (integer, default: 1): Page number for pagination
  - `per_page` (integer, default: 10, max: 50): Items per page
- **Example**: `GET /notes?page=1&per_page=10`
- **Response** (200 OK):
  ```json
  {
    "notes": [
      {
        "id": 1,
        "title": "My First Note",
        "content": "This is the content of my first note.",
        "created_at": "2026-01-15T10:30:00",
        "updated_at": "2026-01-15T10:30:00",
        "user_id": 1
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 53,
      "pages": 6,
      "has_next": true,
      "has_prev": false
    }
  }
  ```
- **Error Responses**:
  - 401: Unauthorized (missing or invalid token)

#### Create a New Note
- **POST** `/notes`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "My New Note",
    "content": "This is the content of my new note."
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "message": "Note created successfully",
    "note": {
      "id": 54,
      "title": "My New Note",
      "content": "This is the content of my new note.",
      "created_at": "2026-01-15T11:00:00",
      "updated_at": "2026-01-15T11:00:00",
      "user_id": 1
    }
  }
  ```
- **Error Responses**:
  - 400: Validation error (missing or invalid fields)
  - 401: Unauthorized (missing or invalid token)
  - 500: Server error during note creation

#### Get a Specific Note
- **GET** `/notes/<id>`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (200 OK):
  ```json
  {
    "note": {
      "id": 1,
      "title": "My First Note",
      "content": "This is the content of my first note.",
      "created_at": "2026-01-15T10:30:00",
      "updated_at": "2026-01-15T10:30:00",
      "user_id": 1
    }
  }
  ```
- **Error Responses**:
  - 401: Unauthorized (missing or invalid token)
  - 403: Forbidden (note owned by another user)
  - 404: Note not found

#### Update a Note
- **PATCH** `/notes/<id>`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body** (partial update, include only fields to update):
  ```json
  {
    "title": "Updated Title",
    "content": "Updated content"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "message": "Note updated successfully",
    "note": {
      "id": 1,
      "title": "Updated Title",
      "content": "Updated content",
      "created_at": "2026-01-15T10:30:00",
      "updated_at": "2026-01-15T11:15:00",
      "user_id": 1
    }
  }
  ```
- **Error Responses**:
  - 400: Validation error (invalid field values)
  - 401: Unauthorized (missing or invalid token)
  - 403: Forbidden (note owned by another user)
  - 404: Note not found
  - 500: Server error during update

#### Delete a Note
- **DELETE** `/notes/<id>`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (200 OK):
  ```json
  {
    "message": "Note deleted successfully"
  }
  ```
- **Error Responses**:
  - 401: Unauthorized (missing or invalid token)
  - 403: Forbidden (note owned by another user)
  - 404: Note not found
  - 500: Server error during deletion

### Health Check Endpoint

#### Health Check
- **GET** `/health`
- **Response** (200 OK):
  ```json
  {
    "status": "ok"
  }
  ```

## Testing

### Using Postman

1. **Register a user**:
   - POST to `/auth/register`
   - Save the response

2. **Login to get a token**:
   - POST to `/auth/login`
   - Copy the `access_token` from the response

3. **Set Authorization header**:
   - In Postman, go to the Authorization tab
   - Select "Bearer Token"
   - Paste your access token

4. **Test note endpoints**:
   - Create, read, update, and delete notes
   - Try accessing notes from different users to verify access control

### Using Pytest

Run the test suite:

```bash
pipenv run pytest
```

To run tests with coverage:

```bash
pipenv run pytest --cov
```

## Database Models

### User Model

| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer | Primary Key, Auto-increment |
| username | String(120) | Unique, Not Null, Indexed |
| email | String(120) | Unique, Not Null, Indexed |
| password_hash | String(255) | Not Null (hashed with bcrypt) |
| created_at | DateTime | Not Null, Default: UTC Now |

**Methods**:
- `set_password(password)`: Hash and store password
- `check_password(password)`: Verify password
- `to_dict()`: Return user data as dictionary

### Note Model

| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer | Primary Key, Auto-increment |
| title | String(255) | Not Null |
| content | Text | Not Null |
| created_at | DateTime | Not Null, Default: UTC Now, Indexed |
| updated_at | DateTime | Not Null, Default: UTC Now, Auto-update |
| user_id | Integer | Foreign Key (User), Not Null, Indexed |

**Methods**:
- `to_dict()`: Return note data as dictionary

## Project Structure

```
Full-Auth-Flask-Backend--Productivity-App/
├── app.py                    # Flask app factory and configuration
├── config.py                 # Environment-specific configurations
├── models.py                 # Database models (User, Note)
├── seed.py                   # Database seeding script with Faker
├── Pipfile                   # Python dependencies
├── .gitignore                # Git ignore file
├── README.md                 # This file
├── routes/
│   ├── __init__.py          # Routes package
│   ├── auth.py              # Authentication endpoints
│   └── notes.py             # Notes CRUD endpoints
├── migrations/               # Flask-Migrate migration files
│   ├── env.py
│   ├── script.py.mako
│   ├── alembic.ini
│   └── versions/
│       └── *.py             # Auto-generated migration files
└── app.db                    # SQLite database file (created after db upgrade)
```

## Security Considerations

1. **Password Hashing**: All passwords are hashed using bcrypt before storage
2. **JWT Tokens**: Use secure tokens that expire after 30 days
3. **Access Control**: All note endpoints check user ownership
4. **Input Validation**: Marshmallow schemas validate all inputs
5. **CORS**: Configure CORS if frontend is on a different domain

### Production Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong, random value
- [ ] Set `FLASK_ENV=production`
- [ ] Use HTTPS (set `SESSION_COOKIE_SECURE=True`)
- [ ] Use a production WSGI server (Gunicorn, uWSGI)
- [ ] Enable CORS only for trusted domains
- [ ] Set up proper logging and monitoring
- [ ] Regular database backups
- [ ] Keep dependencies updated

## Troubleshooting

### Database Issues

**Problem**: "No such table: users"
- **Solution**: Run `flask db upgrade` to create tables

**Problem**: "database is locked"
- **Solution**: Delete `app.db` and run `flask db upgrade` and `python seed.py` again

### JWT Issues

**Problem**: "Invalid token" error
- **Solution**: Ensure you're sending the token in the correct format: `Authorization: Bearer <token>`

**Problem**: "Token has expired"
- **Solution**: Login again to get a new token

### Port Issues

**Problem**: "Address already in use"
- **Solution**: Change the port: `flask run --port 5001`

## Future Enhancements

- [ ] Add email verification for registration
- [ ] Implement password reset functionality
- [ ] Add note sharing between users
- [ ] Add note categories/tags
- [ ] Implement full-text search
- [ ] Add rate limiting
- [ ] Add API documentation with Swagger/OpenAPI
- [ ] Add WebSocket support for real-time updates
- [ ] Implement note versioning/history
- [ ] Add user preferences and themes

## Contributing

When contributing to this project:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and test thoroughly
3. Commit with descriptive messages: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:

1. Check the Troubleshooting section
2. Review the API endpoint documentation
3. Check Flask and SQLAlchemy documentation
4. Open an issue with detailed information about the problem

## Test Credentials

The database comes pre-seeded with test users. Use any of these to test:

| Username | Email | Password |
|----------|-------|----------|
| user1 | user1@example.com | password123 |
| user2 | user2@example.com | password123 |
| user3 | user3@example.com | password123 |
| user4 | user4@example.com | password123 |
| user5 | user5@example.com | password123 |

Each user has 5-15 pre-created notes for testing pagination and access control.
