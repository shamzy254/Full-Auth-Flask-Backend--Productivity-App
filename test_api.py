"""
Simple test suite for the Notes API.
Run with: pipenv run pytest
"""
import pytest
from app import create_app
from models import db, User, Note

@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a CLI runner."""
    return app.test_cli_runner()

class TestAuth:
    """Test authentication endpoints."""

    def test_health_route(self, client):
        """The health endpoint should return a valid JSON response."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'ok'

    def test_login_missing_user_returns_401_on_fresh_start(self):
        """A fresh app should not crash when a non-existent user attempts login."""
        app = create_app(config_name='testing')

        response = app.test_client().post('/auth/login', json={
            'email': 'missing@example.com',
            'password': 'wrongpass'
        })
        assert response.status_code == 401
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 201
        assert response.json['user']['username'] == 'testuser'
    
    def test_register_missing_email(self, client):
        """Test registration with missing email."""
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'password123'
        })
        assert response.status_code == 400
    
    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username."""
        client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'password123'
        })
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert 'already exists' in response.json['error']
    
    def test_login_success(self, client):
        """Test successful login."""
        client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 200
        assert 'access_token' in response.json
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401

class TestNotes:
    """Test notes endpoints."""
    
    def test_create_note_requires_auth(self, client):
        """Test that creating a note requires authentication."""
        response = client.post('/notes', json={
            'title': 'Test Note',
            'content': 'Test content'
        })
        assert response.status_code == 401
    
    def test_create_note_success(self, client):
        """Test successful note creation."""
        # Register and login
        client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        login_response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        token = login_response.json['access_token']
        
        # Create note
        response = client.post('/notes', 
            json={'title': 'Test Note', 'content': 'Test content'},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 201
        assert response.json['note']['title'] == 'Test Note'
    
    def test_get_notes(self, client):
        """Test retrieving notes with pagination."""
        # Register and login
        client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        login_response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        token = login_response.json['access_token']
        
        # Create a note
        client.post('/notes',
            json={'title': 'Test Note', 'content': 'Test content'},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Get notes
        response = client.get('/notes',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        assert 'notes' in response.json
        assert 'pagination' in response.json
        assert len(response.json['notes']) == 1
    
    def test_update_note(self, client):
        """Test updating a note."""
        # Setup: Register, login, create note
        client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        login_response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        token = login_response.json['access_token']
        
        create_response = client.post('/notes',
            json={'title': 'Original', 'content': 'Original content'},
            headers={'Authorization': f'Bearer {token}'}
        )
        note_id = create_response.json['note']['id']
        
        # Update note
        response = client.patch(f'/notes/{note_id}',
            json={'title': 'Updated'},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        assert response.json['note']['title'] == 'Updated'
    
    def test_delete_note(self, client):
        """Test deleting a note."""
        # Setup: Register, login, create note
        client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        login_response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        token = login_response.json['access_token']
        
        create_response = client.post('/notes',
            json={'title': 'To Delete', 'content': 'Delete me'},
            headers={'Authorization': f'Bearer {token}'}
        )
        note_id = create_response.json['note']['id']
        
        # Delete note
        response = client.delete(f'/notes/{note_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f'/notes/{note_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert get_response.status_code == 404

class TestAccessControl:
    """Test access control for notes."""
    
    def test_user_cannot_access_other_users_notes(self, client):
        """Test that users can't access other users' notes."""
        # Create two users
        client.post('/auth/register', json={
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'password123'
        })
        client.post('/auth/register', json={
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'password123'
        })
        
        # Login as user1
        login1 = client.post('/auth/login', json={
            'email': 'user1@example.com',
            'password': 'password123'
        })
        token1 = login1.json['access_token']
        
        # Login as user2
        login2 = client.post('/auth/login', json={
            'email': 'user2@example.com',
            'password': 'password123'
        })
        token2 = login2.json['access_token']
        
        # User1 creates a note
        create_response = client.post('/notes',
            json={'title': 'Private Note', 'content': 'Only for user1'},
            headers={'Authorization': f'Bearer {token1}'}
        )
        note_id = create_response.json['note']['id']
        
        # User2 tries to access user1's note
        response = client.get(f'/notes/{note_id}',
            headers={'Authorization': f'Bearer {token2}'}
        )
        assert response.status_code == 403

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
