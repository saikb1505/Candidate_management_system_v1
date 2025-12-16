# Fix ENUM Errors on Railway

This guide provides multiple methods to fix the CandidateStatus ENUM errors on Railway.

## Problem

Your application code defines these candidate recruitment statuses:
- reviewing
- callback_requested
- initial_screening_completed
- interview_scheduled
- selected
- rejected

But the PostgreSQL database on Railway doesn't have these ENUM values yet, causing errors like:
```
invalid input value for enum candidatestatus: "reviewing"
```

## Solution Methods

Choose **ONE** of these methods based on what works best for your Railway setup.

---

## Method 1: Using Python Script (Recommended)

This method uses a Python script that directly runs the migrations.

### Steps:

1. **Deploy your latest code to Railway** (push to GitHub if auto-deployed)

2. **Open Railway Shell**:
   - Go to your Railway project dashboard
   - Click on your service
   - Click the "..." menu → "Shell"

3. **Run the migration script**:
   ```bash
   python scripts/run_migrations.py
   ```

   Or alternatively:
   ```bash
   bash migrate.sh
   ```

4. **Verify it worked**:
   - Your application should now start without ENUM errors
   - Check the logs to confirm

---

## Method 2: Using Railway CLI

If you have Railway CLI installed locally.

### Steps:

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Link to your project**:
   ```bash
   railway link
   ```

4. **Run migrations**:
   ```bash
   railway run python scripts/run_migrations.py
   ```

   Or:
   ```bash
   railway run bash migrate.sh
   ```

---

## Method 3: Direct SQL Execution

If the above methods don't work, run SQL directly in Railway's PostgreSQL database.

### Steps:

1. **Go to Railway PostgreSQL service**:
   - In Railway dashboard, click on your PostgreSQL database service
   - Click "Query" tab

2. **Copy and paste the SQL from `fix_enum_railway.sql`**:

   The script is in your repository at [`fix_enum_railway.sql`](fix_enum_railway.sql)

3. **Execute the SQL**

4. **Verify** by running this query:
   ```sql
   SELECT e.enumlabel
   FROM pg_type t
   JOIN pg_enum e ON t.oid = e.enumtypid
   WHERE t.typname = 'candidatestatus'
   ORDER BY e.enumlabel;
   ```

   You should see all 10 values:
   - callback_requested
   - completed
   - failed
   - initial_screening_completed
   - interview_scheduled
   - processing
   - rejected
   - reviewing
   - selected
   - uploaded

---

## Method 4: Using psql Connection

If you prefer using psql directly.

### Steps:

1. **Get your PostgreSQL connection string**:
   - Go to Railway PostgreSQL service
   - Copy the "Postgres Connection URL"

2. **Connect using psql**:
   ```bash
   psql "your-connection-url-here"
   ```

3. **Run the SQL script**:
   ```bash
   \i fix_enum_railway.sql
   ```

   Or copy-paste the SQL commands from the file.

4. **Exit psql**:
   ```bash
   \q
   ```

---

## Verification

After applying the fix using any method, verify it worked:

### 1. Check Application Logs
In Railway dashboard → Your Service → Logs

Look for:
- ✓ No ENUM-related errors
- ✓ Application starts successfully

### 2. Test API Endpoints
Try creating or updating a candidate with one of the new statuses:

```bash
curl -X PATCH "https://your-app.railway.app/api/v1/candidates/1/status" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "reviewing"}'
```

Should return success (not an ENUM error).

---

## Troubleshooting

### "No such file or directory" Error

This usually means:
- The files aren't deployed to Railway yet
- **Solution**: Push your latest code to GitHub and wait for Railway to deploy

### "Permission denied" Error

- **Solution**: Use Method 3 (Direct SQL) instead

### "Type candidatestatus_new already exists"

The migration was partially run before:
- **Solution**: Run this SQL first:
  ```sql
  DROP TYPE IF EXISTS candidatestatus_new;
  ```
  Then run the migration again.

### Database Connection Refused

- Check your `DATABASE_URL` environment variable
- Ensure it uses `postgresql+asyncpg://` format for the Python app
- For direct psql connection, use `postgresql://` format

### Migration Already Applied

If you see "candidatestatus enum already has all required values":
- ✓ This is good! The migration already ran successfully
- The ENUM is already fixed

---

## Understanding the Migrations

Your project has these relevant migrations:

1. **`266ef93c09ee`** - Adds the 6 new recruitment statuses
2. **`c4bf82546c55`** - Ensures all ENUM values exist (idempotent)

The latest migration ([`c4bf82546c55_ensure_all_enums_exist.py`](alembic/versions/c4bf82546c55_ensure_all_enums_exist.py)) is smart:
- Checks if the ENUM exists
- Verifies all required values are present
- Only updates if needed
- Safe to run multiple times

---

## Prevention

To prevent this issue in the future:

1. **Always run migrations after deploying**:
   Add a build/deploy command in Railway settings:
   ```bash
   python scripts/run_migrations.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Test migrations locally first**:
   ```bash
   alembic upgrade head
   ```

3. **Check Railway logs** after each deployment

---

## Need Help?

If none of these methods work:

1. Check Railway's build logs for errors
2. Verify your PostgreSQL service is running
3. Ensure `DATABASE_URL` environment variable is set correctly
4. Try redeploying the entire service

Still stuck? Share:
- Railway logs
- Error messages
- Which method you tried
