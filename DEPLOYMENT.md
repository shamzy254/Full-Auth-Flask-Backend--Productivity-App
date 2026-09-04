# Production Deployment Guide

This guide covers deploying the Notes API to production.

## Pre-Deployment Checklist

- [ ] All tests passing locally: `pytest test_api.py -v`
- [ ] Code reviewed and committed
- [ ] Environment variables configured
- [ ] Database strategy decided (PostgreSQL recommended for production)
- [ ] SSL/HTTPS certificate ready
- [ ] CORS domains identified
- [ ] Backup strategy in place
- [ ] Monitoring/logging configured

## Environment Setup

### 1. Create Production Configuration

Create a `.env` file with production values:

```env
# Flask
FLASK_ENV=production
FLASK_APP=app.py

# Database (use PostgreSQL in production)
DATABASE_URL=postgresql://user:password@host:5432/notes_db

# JWT Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=your-secure-random-key-here

# Server
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 2. Security Hardening

Update `config.py` for production:

```python
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # Add CORS configuration
    CORS_ORIGINS = ['https://yourdomain.com']
```

## Database Migration to PostgreSQL

### 1. Install PostgreSQL

```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows - Download from postgresql.org
```

### 2. Create Production Database

```bash
# Create database and user
createuser notes_app_user
createdb notes_db -O notes_app_user

# Set password
psql -d notes_db -c "ALTER USER notes_app_user WITH PASSWORD 'secure-password';"
```

### 3. Update Connection String

```env
DATABASE_URL=postgresql://notes_app_user:secure-password@localhost:5432/notes_db
```

### 4. Run Migrations

```bash
pipenv run flask db upgrade
```

## Deployment Options

### Option 1: Heroku (Easiest)

1. **Install Heroku CLI:**
   ```bash
   brew install heroku/brew/heroku  # macOS
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create app:**
   ```bash
   heroku create your-app-name
   ```

4. **Add PostgreSQL addon:**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. **Set environment variables:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set JWT_SECRET_KEY=your-secret-key
   ```

6. **Deploy:**
   ```bash
   git push heroku main
   ```

7. **Run migrations:**
   ```bash
   heroku run flask db upgrade
   ```

### Option 2: AWS (EC2)

1. **Launch EC2 instance:**
   - Ubuntu 20.04 LTS recommended
   - t3.micro for free tier
   - Open ports: 80, 443, 22

2. **SSH into instance:**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade
   sudo apt install python3.8 python3-pip postgresql postgresql-contrib nginx
   ```

4. **Clone repository:**
   ```bash
   git clone your-repo-url
   cd Full-Auth-Flask-Backend--Productivity-App
   ```

5. **Setup Python environment:**
   ```bash
   pip install pipenv
   pipenv install
   ```

6. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/notes-api.service
   ```

   ```ini
   [Unit]
   Description=Notes API
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/Full-Auth-Flask-Backend--Productivity-App
   Environment="PATH=/home/ubuntu/.local/share/virtualenvs/..."
   ExecStart=/home/ubuntu/.local/bin/gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start service:**
   ```bash
   sudo systemctl enable notes-api
   sudo systemctl start notes-api
   ```

8. **Configure Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/default
   ```

   ```nginx
   server {
       listen 80 default_server;
       server_name _;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

9. **Enable HTTPS (Let's Encrypt):**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Option 3: Docker

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.8-slim

   WORKDIR /app

   COPY Pipfile Pipfile.lock ./
   RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

   COPY . .

   ENV FLASK_APP=app.py
   ENV FLASK_ENV=production

   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
   ```

2. **Build image:**
   ```bash
   docker build -t notes-api:latest .
   ```

3. **Run container:**
   ```bash
   docker run -p 5000:5000 \
     -e DATABASE_URL=postgresql://... \
     -e JWT_SECRET_KEY=... \
     notes-api:latest
   ```

## Production Server Setup

### Using Gunicorn

```bash
# Install Gunicorn
pipenv install gunicorn

# Run with 4 workers
pipenv run gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# With additional options
pipenv run gunicorn \
  -w 4 \
  -b 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  "app:create_app()"
```

### Using uWSGI

```bash
# Install uWSGI
pipenv install uwsgi

# Create uwsgi.ini
[uwsgi]
http = :5000
wsgi-file = app.py
callable = create_app()
master = true
processes = 4
threads = 2
stats = 127.0.0.1:9191

# Run
uwsgi --ini uwsgi.ini
```

## Monitoring & Logging

### Setup Application Logging

Add to `config.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not app.debug:
        if not app.logger.handlers:
            file_handler = RotatingFileHandler(
                'logs/app.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s'
            ))
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Notes API startup')
```

### Setup Error Tracking (Sentry)

```bash
pipenv install sentry-sdk
```

Update `app.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### Database Backups

#### PostgreSQL Automated Backups

```bash
# Create backup script
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/notes_db_$TIMESTAMP.sql"

pg_dump -U notes_app_user notes_db > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "notes_db_*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup_db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /path/to/backup_db.sh
```

## SSL/HTTPS Setup

### Using Let's Encrypt with Nginx

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d api.yourdomain.com

# Configure Nginx for HTTPS
sudo nano /etc/nginx/sites-available/default
```

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Performance Optimization

### Database Connection Pooling

Add to `config.py`:

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### Caching

```bash
pipenv install flask-caching
```

Add to `app.py`:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/notes')
@cache.cached(timeout=300, query_string=True)
def get_notes():
    ...
```

### Compression

```bash
pipenv install flask-compress
```

Add to `app.py`:

```python
from flask_compress import Compress
Compress(app)
```

## CORS Configuration

```bash
pipenv install flask-cors
```

Add to `app.py`:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com", "https://www.yourdomain.com"],
        "methods": ["GET", "POST", "PATCH", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Health Check

The API includes a `/health` endpoint for monitoring:

```bash
curl https://api.yourdomain.com/health
# Response: {"status": "ok"}
```

Configure health checks in your deployment tool:
- Heroku: Automatic
- AWS ELB: `/health` endpoint, HTTP 200
- Docker: Add HEALTHCHECK to Dockerfile

## Post-Deployment Verification

```bash
# Test API is running
curl https://api.yourdomain.com/health

# Test auth endpoint
curl -X POST https://api.yourdomain.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"password123"}'

# Test protected endpoint
curl -X GET https://api.yourdomain.com/notes \
  -H "Authorization: Bearer <token>"
```

## Rollback Strategy

1. **Keep previous version running**
2. **New release as separate service**
3. **Load balancer switches traffic**
4. **If issues, switch back immediately**

```bash
# With Heroku
heroku releases  # View history
heroku rollback  # Go to previous version
```

## Monitoring URLs

- Sentry: https://sentry.io/organizations/your-org/issues/
- Database: AWS RDS console, Heroku dashboard
- Logs: CloudWatch, Heroku logs, or local file

## Troubleshooting

### Application won't start
```bash
# Check logs
heroku logs --tail  # Heroku
sudo journalctl -u notes-api -f  # Systemd
docker logs container-id  # Docker
```

### Database connection errors
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Verify environment variable
echo $DATABASE_URL
```

### High memory usage
```bash
# Reduce worker count
gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
```

## Support Resources

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Heroku: https://devcenter.heroku.com/
- AWS: https://docs.aws.amazon.com/
- Docker: https://docs.docker.com/
