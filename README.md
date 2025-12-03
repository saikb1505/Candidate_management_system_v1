# Resume Parser API

A production-ready FastAPI application for parsing resumes using OpenAI, with JWT authentication, role-based access control, and background job processing.

## Features

- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **Role-Based Access Control (RBAC)**: Four user roles with different permissions
  - Admin: Full system access
  - HR Manager: Can manage resumes and users
  - Recruiter: Can upload and view resumes
  - Viewer: Read-only access
- **Resume Upload & Parsing**: Upload resumes (PDF, DOC, DOCX) and automatically parse with OpenAI
- **Background Job Processing**: Asynchronous resume processing with Celery
- **PostgreSQL Database**: Robust data storage with async support
- **Database Migrations**: Alembic for schema management
- **Production-Ready**:
  - Comprehensive logging
  - Error handling and validation
  - CORS support
  - Health check endpoints

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **PostgreSQL**: Primary database
- **SQLAlchemy**: ORM with async support
- **Alembic**: Database migrations
- **Celery**: Background task queue
- **Redis**: Message broker and result backend
- **OpenAI**: Resume parsing
- **JWT**: Authentication

## Project Structure

```
resume_parser_api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py          # Authentication endpoints
│   │           ├── users.py         # User management
│   │           └── resumes.py       # Resume operations
│   ├── core/
│   │   ├── config.py               # Configuration
│   │   ├── security.py             # JWT & password hashing
│   │   ├── deps.py                 # Dependencies & RBAC
│   │   ├── logging_config.py       # Logging setup
│   │   └── middleware.py           # Middleware & error handlers
│   ├── models/
│   │   ├── user.py                 # User model
│   │   └── resume.py               # Resume model
│   ├── schemas/
│   │   ├── user.py                 # User schemas
│   │   ├── auth.py                 # Auth schemas
│   │   └── resume.py               # Resume schemas
│   ├── services/
│   │   ├── celery_app.py           # Celery configuration
│   │   ├── celery_tasks.py         # Background tasks
│   │   └── openai_service.py       # OpenAI integration
│   ├── utils/
│   │   └── file_handler.py         # File operations
│   └── main.py                     # Application entry point
├── alembic/                        # Database migrations
├── uploads/                        # Uploaded files
├── logs/                           # Application logs
├── requirements.txt
└── .env.example

```

## Setup Instructions

### Prerequisites

You need to have the following installed on your system:

- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **PostgreSQL**: [Installation Guide](https://www.postgresql.org/download/)
  - Ubuntu/Debian: `sudo apt-get install postgresql postgresql-contrib`
  - macOS: `brew install postgresql`
- **Redis**: [Installation Guide](https://redis.io/download)
  - Ubuntu/Debian: `sudo apt-get install redis-server`
  - macOS: `brew install redis`

### Quick Setup

Run the automated setup script:

```bash
bash setup.sh
```

This script will:
1. Check for required dependencies
2. Create `.env` file from template
3. Install Python dependencies
4. Create the database
5. Run migrations
6. Create an admin user

### Manual Setup

If you prefer to set up manually:

#### 1. Create environment file

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-secret-key-here

# Database (adjust if using custom setup)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/resume_parser
DATABASE_URL_SYNC=postgresql://postgres:password@localhost:5432/resume_parser

# Redis
REDIS_URL=redis://localhost:6379/0
```

#### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Start PostgreSQL

Make sure PostgreSQL is running:

```bash
# Ubuntu/Debian
sudo service postgresql start

# macOS
brew services start postgresql
```

Create the database:

```bash
createdb resume_parser
```

#### 5. Start Redis

```bash
# Ubuntu/Debian
sudo service redis-server start

# macOS
brew services start redis

# Or run in foreground
redis-server
```

#### 6. Run database migrations

Make sure your virtual environment is activated (`source venv/bin/activate`)

```bash
alembic upgrade head
```

#### 7. Create required directories

```bash
mkdir -p uploads logs
```

#### 8. Create an admin user

```bash
python -m scripts.create_admin
```

#### 9. Start the API server

Make sure your virtual environment is activated:

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

#### 10. Start Celery worker (in another terminal)

Activate the virtual environment first:

```bash
source venv/bin/activate
celery -A app.services.celery_app worker --loglevel=info
```

**Note**: Always activate the virtual environment (`source venv/bin/activate`) before running any Python commands.

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token

### Users

- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/` - List all users (Admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID (Admin only)
- `PUT /api/v1/users/{user_id}` - Update user (Admin only)
- `DELETE /api/v1/users/{user_id}` - Delete user (Admin only)

### Resumes

- `POST /api/v1/resumes/upload` - Upload resume (Recruiter+)
- `GET /api/v1/resumes/` - List all resumes
- `GET /api/v1/resumes/{resume_id}` - Get resume details
- `DELETE /api/v1/resumes/{resume_id}` - Delete resume (Recruiter+)
- `GET /api/v1/resumes/search/by-skill?skill={skill}` - Search by skill
- `GET /api/v1/resumes/search/by-email?email={email}` - Search by email

### Health Check

- `GET /health` - Health check endpoint

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Example

### 1. Register a user

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "recruiter@example.com",
    "username": "recruiter1",
    "password": "securepassword123",
    "full_name": "John Doe",
    "role": "recruiter"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "recruiter1",
    "password": "securepassword123"
  }'
```

Save the `access_token` from the response.

### 3. Upload a resume

```bash
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/resume.pdf"
```

The resume will be processed in the background. Check status:

```bash
curl -X GET "http://localhost:8000/api/v1/resumes/{resume_id}" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## User Roles & Permissions

| Role | Upload Resumes | View Resumes | Delete Resumes | Manage Users |
|------|---------------|--------------|----------------|--------------|
| Viewer | ❌ | ✅ | ❌ | ❌ |
| Recruiter | ✅ | ✅ | ✅ | ❌ |
| HR Manager | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ |

## Resume Parsing

The system extracts:

- **Candidate Name**
- **Email Address**
- **Phone Number**
- **Skills** (as array)
- **Domain Knowledge** (summary)

Parsed data is automatically saved to the database.

## Monitoring

### Logs

Logs are stored in the `logs/` directory:
- `app.log` - All application logs
- `error.log` - Error logs only

### Health Check

```bash
curl http://localhost:8000/health
```

## Security Best Practices

- Change `SECRET_KEY` in production
- Use strong passwords
- Keep `OPENAI_API_KEY` secret
- Use HTTPS in production
- Regularly update dependencies
- Review and rotate JWT tokens periodically

## Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues

Check if PostgreSQL is running:
```bash
# Ubuntu/Debian
sudo service postgresql status

# macOS
brew services list | grep postgresql
```

Test connection:
```bash
psql -h localhost -U postgres -d resume_parser
```

### Celery Worker Issues

Check if Redis is running:
```bash
# Ubuntu/Debian
sudo service redis-server status

# macOS
brew services list | grep redis

# Test connection
redis-cli ping
```

View Celery logs in the terminal where you started the worker.

### OpenAI API Errors

- Verify `OPENAI_API_KEY` is set correctly in `.env`
- Check API quota and billing
- Review logs in `logs/app.log` and `logs/error.log`

## Production Deployment

1. Use environment variables for all secrets
2. Set `DEBUG=False` in production
3. Use a production WSGI server (included: uvicorn)
4. Set up proper CORS origins
5. Use managed PostgreSQL and Redis services
6. Implement backup strategy
7. Set up monitoring and alerting
8. Use HTTPS with valid certificates
9. Implement rate limiting
10. Regular security updates

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.
