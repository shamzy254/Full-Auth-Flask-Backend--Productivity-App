"""
Flask application factory and configuration.
"""
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from config import DevelopmentConfig, ProductionConfig, TestingConfig
from models import db, bcrypt

migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='development'):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    selected_config = config_map.get(config_name.lower(), DevelopmentConfig)
    
    # Load configuration
    app.config.from_object(selected_config)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Ensure the database exists for fresh deployments and local runs.
    with app.app_context():
        db.create_all()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.notes import notes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)

    @app.route('/', methods=['GET'])
    def index():
        """Basic API landing endpoint."""
        return {
            'service': 'Full Auth Flask Backend',
            'status': 'ok',
            'routes': ['/health', '/auth/register', '/auth/login', '/notes']
        }, 200
    
    # Register a simple health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return {'status': 'ok'}, 200
    
    return app

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return {'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        return {'error': 'Unauthorized', 'message': 'Invalid or missing token'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        return {'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return {'error': 'Not found', 'message': 'The requested resource does not exist'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
