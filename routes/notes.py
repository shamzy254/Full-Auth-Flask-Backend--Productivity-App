"""
Note resource routes for CRUD operations with pagination.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError, validate

from models import db, Note, User

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

# Schema for validation
class NoteSchema(Schema):
    """Schema for note validation."""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'Title is required'}
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Content is required'}
    )

note_schema = NoteSchema()

@notes_bp.route('', methods=['GET'])
@jwt_required()
def get_notes():
    """
    Get all notes for the current user with pagination.
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10, max: 50)
    
    Returns:
    - 200: Paginated list of notes
    - 401: Unauthorized
    """
    user_id = get_jwt_identity()
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 50:
        per_page = 10
    
    # Query notes for the user, ordered by most recent first
    pagination = Note.query.filter_by(user_id=user_id).order_by(
        Note.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'notes': [note.to_dict() for note in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }, 200

@notes_bp.route('', methods=['POST'])
@jwt_required()
def create_note():
    """
    Create a new note for the current user.
    
    Request body:
    {
        "title": "string",
        "content": "string"
    }
    
    Returns:
    - 201: Note created successfully
    - 400: Validation error
    - 401: Unauthorized
    """
    user_id = get_jwt_identity()
    
    try:
        data = note_schema.load(request.get_json())
    except ValidationError as err:
        return {'errors': err.messages}, 400
    
    # Create new note
    note = Note(
        title=data['title'],
        content=data['content'],
        user_id=user_id
    )
    
    try:
        db.session.add(note)
        db.session.commit()
        return {
            'message': 'Note created successfully',
            'note': note.to_dict()
        }, 201
    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to create note', 'details': str(e)}, 500

@notes_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    """
    Get a single note by ID (only if owned by current user).
    
    Returns:
    - 200: Note data
    - 401: Unauthorized
    - 403: Forbidden (note owned by another user)
    - 404: Note not found
    """
    user_id = get_jwt_identity()
    note = Note.query.get(note_id)
    
    if not note:
        return {'error': 'Note not found'}, 404
    
    # Check ownership
    if note.user_id != user_id:
        return {'error': 'Forbidden'}, 403
    
    return {'note': note.to_dict()}, 200

@notes_bp.route('/<int:note_id>', methods=['PATCH'])
@jwt_required()
def update_note(note_id):
    """
    Update a note (only if owned by current user).
    
    Request body:
    {
        "title": "string (optional)",
        "content": "string (optional)"
    }
    
    Returns:
    - 200: Note updated successfully
    - 400: Validation error
    - 401: Unauthorized
    - 403: Forbidden (note owned by another user)
    - 404: Note not found
    """
    user_id = get_jwt_identity()
    note = Note.query.get(note_id)
    
    if not note:
        return {'error': 'Note not found'}, 404
    
    # Check ownership
    if note.user_id != user_id:
        return {'error': 'Forbidden'}, 403
    
    data = request.get_json()
    
    # Validate and update fields
    if 'title' in data:
        if not isinstance(data['title'], str) or len(data['title'].strip()) == 0:
            return {'error': 'Title must be a non-empty string'}, 400
        note.title = data['title']
    
    if 'content' in data:
        if not isinstance(data['content'], str) or len(data['content'].strip()) == 0:
            return {'error': 'Content must be a non-empty string'}, 400
        note.content = data['content']
    
    try:
        db.session.commit()
        return {
            'message': 'Note updated successfully',
            'note': note.to_dict()
        }, 200
    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to update note', 'details': str(e)}, 500

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """
    Delete a note (only if owned by current user).
    
    Returns:
    - 200: Note deleted successfully
    - 401: Unauthorized
    - 403: Forbidden (note owned by another user)
    - 404: Note not found
    """
    user_id = get_jwt_identity()
    note = Note.query.get(note_id)
    
    if not note:
        return {'error': 'Note not found'}, 404
    
    # Check ownership
    if note.user_id != user_id:
        return {'error': 'Forbidden'}, 403
    
    try:
        db.session.delete(note)
        db.session.commit()
        return {'message': 'Note deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to delete note', 'details': str(e)}, 500
