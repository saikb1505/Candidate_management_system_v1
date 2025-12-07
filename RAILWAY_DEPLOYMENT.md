# Railway Deployment Guide

This guide will help you deploy the Resume Parser API to Railway.app.

## Prerequisites

1. A [Railway.app](https://railway.app) account
2. Railway CLI installed (optional): `npm i -g @railway/cli`
3. Your OpenAI API key

## Deployment Steps

### 1. Create a New Project on Railway

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository

### 2. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a PostgreSQL instance and set the `DATABASE_URL` environment variable

### 3. Configure Environment Variables

In your Railway service settings, add these environment variables:

#### Required Variables

```
SECRET_KEY=<generate-a-secure-random-key>
OPENAI_API_KEY=<your-openai-api-key>
```

#### Optional Variables (with defaults)

```
APP_NAME=Resume Parser API
APP_VERSION=1.0.0
DEBUG=False
API_V1_PREFIX=/api/v1
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,doc,docx
UPLOAD_DIR=uploads
BACKEND_CORS_ORIGINS=["https://your-frontend-domain.com"]
```

#### Auto-Configured Variables

These are automatically set by Railway:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - The port your app should listen on

**Important:** Railway provides `DATABASE_URL` in the format `postgresql://...`, but we need the async format:

Manually override `DATABASE_URL`:
```
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
```

You can reference Railway's auto-generated PostgreSQL credentials from the PostgreSQL service variables.

### 5. Generate a Secure SECRET_KEY

Run this Python command to generate a secure key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Deploy

Railway will automatically deploy your application when you push to your repository.

The deployment process includes:
1. Installing dependencies from `requirements.txt`
2. Running database migrations (`alembic upgrade head`)
3. Starting the web server (`uvicorn`)

### 7. Access Your Application

Once deployed, Railway will provide you with a URL like:
```
https://your-app-name.railway.app
```

Visit the following endpoints:
- API Root: `https://your-app-name.railway.app/`
- Health Check: `https://your-app-name.railway.app/health`
- API Docs: `https://your-app-name.railway.app/docs`
- ReDoc: `https://your-app-name.railway.app/redoc`

### 8. Create Admin User

After deployment, you need to create an admin user. You can do this by:

1. Using Railway's CLI to run a command:
```bash
railway run python scripts/create_admin.py
```

2. Or connect to your Railway shell and run:
```bash
python scripts/create_admin.py
```

Follow the prompts to create your admin account.

## Monitoring

### Check Logs

View logs in the Railway dashboard or use the CLI:
```bash
railway logs
```

### Health Check

Monitor your app's health:
```bash
curl https://your-app-name.railway.app/health
```

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Verify `DATABASE_URL` is correctly set with the `postgresql+asyncpg://` format
2. Check that the PostgreSQL service is running
3. Ensure the database URL uses the async format

### Migration Issues

If migrations fail:
1. Check the logs for specific error messages
2. You may need to manually run migrations:
```bash
railway run alembic upgrade head
```

### File Upload Issues

Railway provides ephemeral storage, meaning uploaded files will be lost on restart. Consider:
1. Using S3 or similar object storage for production
2. Implementing file storage service integration

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Async PostgreSQL connection string | Yes | Must override with asyncpg format |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `APP_NAME` | Application name | No | Resume Parser API |
| `DEBUG` | Debug mode | No | False |
| `BACKEND_CORS_ORIGINS` | CORS allowed origins | No | localhost |
| `PORT` | Server port | No | Auto-set by Railway |

## Scaling

Railway allows you to scale your application:
1. Go to your service settings
2. Adjust the "Replicas" setting
3. Configure resource limits (CPU/RAM)

## Cost Considerations

Railway offers:
- $5 free credit per month
- Pay-as-you-go pricing after free credit
- Resource usage monitoring in the dashboard

Monitor your usage to avoid unexpected charges.

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: Use your repository's issue tracker

## Security Checklist

Before going live:
- [ ] Set a strong `SECRET_KEY`
- [ ] Never commit `.env` file
- [ ] Configure `BACKEND_CORS_ORIGINS` with your actual domains
- [ ] Enable HTTPS (Railway provides this by default)
- [ ] Review and limit file upload sizes
- [ ] Set up proper logging and monitoring
- [ ] Create admin user with strong password
- [ ] Regularly update dependencies
- [ ] Set up database backups (Railway provides this)
- [ ] Review OpenAI API usage limits
