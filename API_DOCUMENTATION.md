# Resume Parser API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000/api/v1`

## Table of Contents
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [User Management Endpoints](#user-management-endpoints)
  - [Candidate Management Endpoints](#candidate-management-endpoints)
- [Data Models](#data-models)
- [Error Responses](#error-responses)
- [Role-Based Access Control](#role-based-access-control)

---

## Authentication

This API uses **JWT (JSON Web Token)** based authentication with Bearer tokens.

### Authentication Flow
1. An admin creates your user account (or use existing credentials)
2. Login to receive `access_token` and `refresh_token`
3. Include the access token in the `Authorization` header for protected endpoints:
   ```
   Authorization: Bearer <access_token>
   ```
4. When the access token expires (30 minutes), use the refresh token to get a new access token

### Token Expiration
- **Access Token:** 30 minutes
- **Refresh Token:** 7 days

---

## Endpoints

### Authentication Endpoints

#### 1. Login
**POST** `/api/v1/auth/login`

Login and receive access and refresh tokens.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securePassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Incorrect username or password
- `400 Bad Request`: Inactive user

---

#### 2. Refresh Access Token
**POST** `/api/v1/auth/refresh`

Get a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid refresh token or user not found/inactive

---

### User Management Endpoints

#### 3. Create User (Admin Only)
**POST** `/api/v1/users/`

Create a new user account (Admin only). Unlike public registration, this endpoint allows admins to create users with specific roles and configurations.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securePassword123",
  "full_name": "John Doe",
  "role": "recruiter"
}
```

**Fields:**
- `email` (required, string): Valid email address
- `username` (required, string): Username (3-50 characters)
- `password` (required, string): Password (8-100 characters)
- `full_name` (optional, string): User's full name
- `role` (optional, string): User role. Options: `viewer`, `recruiter`, `hr_manager`, `admin`. Default: `viewer`

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "recruiter",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T10:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Email already registered or username already taken
- `403 Forbidden`: Admin privileges required

**Required Role:** `admin`

---

#### 4. Get Current User Info
**GET** `/api/v1/users/me`

Get the currently authenticated user's information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "viewer",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T10:00:00Z"
}
```

---

#### 5. Update Current User
**PUT** `/api/v1/users/me`

Update the currently authenticated user's information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** (all fields optional)
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "Jane Doe",
  "password": "newPassword123"
}
```

**Note:** Users cannot change their own role.

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "Jane Doe",
  "role": "viewer",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T10:30:00Z"
}
```

---

#### 6. List Users (Admin Only)
**GET** `/api/v1/users/`

List all users with filtering, searching, and pagination options.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (optional, integer): Number of records to skip. Default: `0`, Min: `0`
- `limit` (optional, integer): Maximum number of records to return. Default: `100`, Min: `1`, Max: `500`
- `role` (optional, string): Filter by user role. Options: `admin`, `hr_manager`, `recruiter`, `viewer`
- `is_active` (optional, boolean): Filter by active status. Options: `true`, `false`
- `search` (optional, string): Search by username or email (case-insensitive, partial match)

**Examples:**
```
GET /api/v1/users/?skip=0&limit=50
GET /api/v1/users/?role=recruiter
GET /api/v1/users/?is_active=false
GET /api/v1/users/?search=john
GET /api/v1/users/?role=admin&is_active=true
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "username": "user1",
    "full_name": "User One",
    "role": "admin",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-11-28T10:00:00Z",
    "updated_at": "2025-11-28T10:00:00Z"
  },
  {
    "id": 2,
    "email": "user2@example.com",
    "username": "user2",
    "full_name": "User Two",
    "role": "recruiter",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-11-28T11:00:00Z",
    "updated_at": "2025-11-28T11:00:00Z"
  }
]
```

**Required Role:** `admin`

---

#### 7. Get User by ID (Admin Only)
**GET** `/api/v1/users/{user_id}`

Get a specific user by their ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (required, integer): User ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "viewer",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T10:00:00Z"
}
```

**Error Responses:**
- `404 Not Found`: User not found

**Required Role:** `admin`

---

#### 8. Update User by ID (Admin Only)
**PUT** `/api/v1/users/{user_id}`

Update a specific user's information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (required, integer): User ID

**Request Body:** (all fields optional)
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "Jane Doe",
  "password": "newPassword123",
  "role": "recruiter",
  "is_active": false
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "Jane Doe",
  "role": "recruiter",
  "is_active": false,
  "is_superuser": false,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T12:00:00Z"
}
```

**Required Role:** `admin`

---

#### 9. Deactivate User (Admin Only)
**PATCH** `/api/v1/users/{user_id}/deactivate`

Deactivate a user account (soft delete). Deactivated users cannot log in but their data is preserved.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (required, integer): User ID

**Response:** `200 OK`
```json
{
  "id": 3,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "recruiter",
  "is_active": false,
  "is_superuser": false,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T12:30:00Z"
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `400 Bad Request`: User is already inactive or attempting to deactivate own account

**Required Role:** `admin`

**Note:** Admins cannot deactivate their own account.

---

#### 10. Activate User (Admin Only)
**PATCH** `/api/v1/users/{user_id}/activate`

Reactivate a previously deactivated user account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (required, integer): User ID

**Response:** `200 OK`
```json
{
  "id": 3,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "recruiter",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T13:00:00Z"
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `400 Bad Request`: User is already active

**Required Role:** `admin`

---

#### 11. Delete User Permanently (Admin Only)
**DELETE** `/api/v1/users/{user_id}`

Permanently delete a user account and all associated data. **Use with extreme caution.**

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (required, integer): User ID

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found`: User not found
- `400 Bad Request`: Attempting to delete own account

**Required Role:** `admin`

**Warning:** This operation is irreversible. Consider using the deactivate endpoint instead for most cases.

**Note:** Admins cannot delete their own account.

---

### Candidate Management Endpoints

#### 12. Upload Candidate Resume
**POST** `/api/v1/candidates/upload`

Upload a candidate's resume file for asynchronous processing. The resume will be parsed using AI to extract candidate information.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
- `file` (required, file): Resume file (PDF, DOC, DOCX)

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/candidates/upload" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/resume.pdf"
```

**Response:** `202 Accepted`
```json
{
  "message": "Candidate resume uploaded successfully and is being processed",
  "filename": "resume.pdf",
  "status": "processing"
}
```

**File Constraints:**
- Max file size: 10 MB
- Allowed formats: PDF, DOC, DOCX

**Required Role:** `recruiter`, `hr_manager`, or `admin`

**Note:** The resume is processed asynchronously. Use the list/search endpoints to check when processing is complete.

---

#### 13. List Candidates
**GET** `/api/v1/candidates/`

List all candidates with optional filtering and pagination.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (optional, integer): Number of records to skip. Default: `0`
- `limit` (optional, integer): Maximum number of records to return. Default: `100`
- `status_filter` (optional, string): Filter by status. Options: `uploaded`, `processing`, `completed`, `failed`
- `skills` (optional, string): Comma-separated list of skills to search for (e.g., `"Python,Django,FastAPI"`)

**Examples:**
```
GET /api/v1/candidates/?skip=0&limit=20
GET /api/v1/candidates/?status_filter=completed
GET /api/v1/candidates/?skills=Python,React
GET /api/v1/candidates/?status_filter=completed&skills=Python,Django
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "filename": "john_doe_resume.pdf",
    "file_path": "uploads/abc123_john_doe_resume.pdf",
    "file_size": 245678,
    "status": "completed",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567",
    "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"],
    "domain_knowledge": "Backend development with focus on RESTful APIs and microservices",
    "uploaded_by": 2,
    "error_message": null,
    "created_at": "2025-11-28T10:00:00Z",
    "updated_at": "2025-11-28T10:05:00Z",
    "processed_at": "2025-11-28T10:05:00Z"
  },
  {
    "id": 2,
    "filename": "jane_smith_resume.pdf",
    "file_path": "uploads/def456_jane_smith_resume.pdf",
    "file_size": 198234,
    "status": "completed",
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone": "+1-555-987-6543",
    "skills": ["JavaScript", "React", "Node.js", "MongoDB", "AWS"],
    "domain_knowledge": "Full-stack development with expertise in MERN stack",
    "uploaded_by": 2,
    "error_message": null,
    "created_at": "2025-11-28T11:00:00Z",
    "updated_at": "2025-11-28T11:03:00Z",
    "processed_at": "2025-11-28T11:03:00Z"
  }
]
```

**Note:** Results are ordered by creation date (newest first).

---

#### 14. Get Candidate by ID
**GET** `/api/v1/candidates/{candidate_id}`

Get detailed information about a specific candidate.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `candidate_id` (required, integer): Candidate ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "filename": "john_doe_resume.pdf",
  "file_path": "uploads/abc123_john_doe_resume.pdf",
  "file_size": 245678,
  "status": "completed",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-123-4567",
  "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"],
  "domain_knowledge": "Backend development with focus on RESTful APIs and microservices",
  "uploaded_by": 2,
  "error_message": null,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T10:05:00Z",
  "processed_at": "2025-11-28T10:05:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Candidate not found

---

#### 15. Search Candidates by Skill
**GET** `/api/v1/candidates/search/by-skill`

Search for candidates by a specific skill (case-insensitive, partial matching).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skill` (required, string): Skill to search for (e.g., `"Python"`, `"React"`)

**Example:**
```
GET /api/v1/candidates/search/by-skill?skill=Python
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "filename": "john_doe_resume.pdf",
    "file_path": "uploads/abc123_john_doe_resume.pdf",
    "file_size": 245678,
    "status": "completed",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567",
    "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"],
    "domain_knowledge": "Backend development with focus on RESTful APIs and microservices",
    "uploaded_by": 2,
    "error_message": null,
    "created_at": "2025-11-28T10:00:00Z",
    "updated_at": "2025-11-28T10:05:00Z",
    "processed_at": "2025-11-28T10:05:00Z"
  }
]
```

**Note:** Only returns candidates with status `completed`. Results are ordered by creation date (newest first).

---

#### 16. Search Candidate by Email
**GET** `/api/v1/candidates/search/by-email`

Search for a candidate by their email address.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `email` (required, string): Email address to search for

**Example:**
```
GET /api/v1/candidates/search/by-email?email=john.doe@example.com
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "filename": "john_doe_resume.pdf",
  "file_path": "uploads/abc123_john_doe_resume.pdf",
  "file_size": 245678,
  "status": "completed",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-123-4567",
  "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"],
  "domain_knowledge": "Backend development with focus on RESTful APIs and microservices",
  "uploaded_by": 2,
  "error_message": null,
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T10:05:00Z",
  "processed_at": "2025-11-28T10:05:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Candidate not found for this email

**Note:** If multiple candidates exist with the same email, returns the most recently created one.

---

#### 17. Delete Candidate
**DELETE** `/api/v1/candidates/{candidate_id}`

Delete a candidate profile and associated resume file.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `candidate_id` (required, integer): Candidate ID

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found`: Candidate not found

**Required Role:** `recruiter`, `hr_manager`, or `admin`

**Note:** This permanently deletes both the database record and the uploaded file.

---

## Data Models

### User
```typescript
{
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: "admin" | "hr_manager" | "recruiter" | "viewer";
  is_active: boolean;
  is_superuser: boolean;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}
```

### Candidate
```typescript
{
  id: number;
  filename: string;
  file_path: string;
  file_size: number; // in bytes
  status: "uploaded" | "processing" | "completed" | "failed";
  name: string | null;
  email: string | null;
  phone: string | null;
  skills: string[] | null;
  domain_knowledge: string | null;
  uploaded_by: number; // user ID
  error_message: string | null;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  processed_at: string | null; // ISO 8601 datetime
}
```

### Token
```typescript
{
  access_token: string;
  refresh_token: string;
  token_type: string; // always "bearer"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 OK | Request successful |
| 201 Created | Resource created successfully |
| 202 Accepted | Request accepted for processing |
| 204 No Content | Request successful, no content to return |
| 400 Bad Request | Invalid request data |
| 401 Unauthorized | Authentication required or failed |
| 403 Forbidden | Insufficient permissions |
| 404 Not Found | Resource not found |
| 422 Unprocessable Entity | Validation error |
| 500 Internal Server Error | Server error |

---

## Role-Based Access Control

### User Roles (Hierarchical)

1. **Admin** - Full system access
   - All permissions
   - Can manage users
   - Can manage candidates

2. **HR Manager** - HR operations
   - Can upload and manage candidates
   - Can view all candidates
   - Can view users (but not manage)

3. **Recruiter** - Recruitment operations
   - Can upload and manage candidates
   - Can view all candidates
   - Cannot manage users

4. **Viewer** - Read-only access
   - Can view candidates
   - Cannot upload or delete candidates
   - Cannot manage users

### Endpoint Access Matrix

| Endpoint | Admin | HR Manager | Recruiter | Viewer |
|----------|-------|------------|-----------|--------|
| POST /auth/login | ✅ | ✅ | ✅ | ✅ |
| POST /auth/refresh | ✅ | ✅ | ✅ | ✅ |
| POST /users/ | ✅ | ❌ | ❌ | ❌ |
| GET /users/me | ✅ | ✅ | ✅ | ✅ |
| PUT /users/me | ✅ | ✅ | ✅ | ✅ |
| GET /users/ | ✅ | ❌ | ❌ | ❌ |
| GET /users/{id} | ✅ | ❌ | ❌ | ❌ |
| PUT /users/{id} | ✅ | ❌ | ❌ | ❌ |
| PATCH /users/{id}/deactivate | ✅ | ❌ | ❌ | ❌ |
| PATCH /users/{id}/activate | ✅ | ❌ | ❌ | ❌ |
| DELETE /users/{id} | ✅ | ❌ | ❌ | ❌ |
| POST /candidates/upload | ✅ | ✅ | ✅ | ❌ |
| GET /candidates/ | ✅ | ✅ | ✅ | ✅ |
| GET /candidates/{id} | ✅ | ✅ | ✅ | ✅ |
| GET /candidates/search/* | ✅ | ✅ | ✅ | ✅ |
| DELETE /candidates/{id} | ✅ | ✅ | ✅ | ❌ |

---

## User Management Workflows

### Complete Admin User Management Flow

#### 1. Creating a New User
```bash
# Admin creates a new user
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "SecurePass123",
    "full_name": "New User",
    "role": "recruiter"
  }'
```

#### 2. Listing and Searching Users
```bash
# List all users
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer <admin_access_token>"

# Filter by role
curl -X GET "http://localhost:8000/api/v1/users/?role=recruiter" \
  -H "Authorization: Bearer <admin_access_token>"

# Filter by active status
curl -X GET "http://localhost:8000/api/v1/users/?is_active=false" \
  -H "Authorization: Bearer <admin_access_token>"

# Search by username or email
curl -X GET "http://localhost:8000/api/v1/users/?search=john" \
  -H "Authorization: Bearer <admin_access_token>"

# Combine filters
curl -X GET "http://localhost:8000/api/v1/users/?role=admin&is_active=true&search=admin" \
  -H "Authorization: Bearer <admin_access_token>"
```

#### 3. Viewing User Details
```bash
# Get specific user by ID
curl -X GET "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_access_token>"
```

#### 4. Updating User Information
```bash
# Update user role and other details
curl -X PUT "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "hr_manager",
    "full_name": "Updated Name"
  }'

# Reset user password
curl -X PUT "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "NewSecurePass456"
  }'
```

#### 5. Deactivating a User (Soft Delete)
```bash
# Deactivate user - they cannot log in but data is preserved
curl -X PATCH "http://localhost:8000/api/v1/users/5/deactivate" \
  -H "Authorization: Bearer <admin_access_token>"
```

**Use Case:** Temporarily suspend a user account, employee on leave, or security concern.

#### 6. Reactivating a User
```bash
# Reactivate a previously deactivated user
curl -X PATCH "http://localhost:8000/api/v1/users/5/activate" \
  -H "Authorization: Bearer <admin_access_token>"
```

**Use Case:** User returns from leave or security issue resolved.

#### 7. Permanently Deleting a User
```bash
# Permanently delete user (irreversible)
curl -X DELETE "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_access_token>"
```

**⚠️ Warning:** This permanently removes the user and all associated data. Use deactivate instead for most cases.

### User Self-Service Flow

#### Update Own Profile
```bash
# Users can update their own information (except role)
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <user_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "email": "newemail@example.com",
    "password": "NewPassword123"
  }'
```

#### View Own Profile
```bash
# Users can view their own profile
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <user_access_token>"
```

### Best Practices

1. **Use Soft Delete (Deactivate) by Default**
   - Preserves data integrity and audit trails
   - Allows easy reactivation if needed
   - Only use hard delete when legally required (e.g., GDPR requests)

2. **Role Management**
   - Regularly audit user roles and permissions
   - Use the search and filter features to identify users by role
   - Update roles as responsibilities change

3. **Password Management**
   - Enforce strong password requirements (8+ characters)
   - Admins can reset user passwords when needed
   - Users can update their own passwords

4. **Account Security**
   - Monitor inactive accounts with `is_active=false` filter
   - Review and deactivate unused accounts
   - Admins cannot deactivate or delete their own accounts (safety measure)

---

## Additional Information

### CORS Configuration
The API supports CORS with the following default origin:
- `http://localhost:3000`

Additional origins can be configured via environment variables.

### Interactive API Documentation
The API provides interactive documentation at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Health Check
**GET** `/health`

Check API health status (no authentication required).

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Example Frontend Integration

### Authentication Example (JavaScript/TypeScript)

```typescript
// Login
const login = async (username: string, password: string) => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  const data = await response.json();

  // Store tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);

  return data;
};

// Make authenticated request
const getCandidates = async () => {
  const accessToken = localStorage.getItem('access_token');

  const response = await fetch('http://localhost:8000/api/v1/candidates/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });

  return await response.json();
};

// Upload resume
const uploadResume = async (file: File) => {
  const accessToken = localStorage.getItem('access_token');
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/api/v1/candidates/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    body: formData,
  });

  return await response.json();
};

// Refresh token
const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');

  const response = await fetch('http://localhost:8000/api/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  const data = await response.json();

  // Update stored tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);

  return data;
};
```

---

## Support

For questions or issues, please contact the backend development team or refer to the interactive API documentation at `/docs`.
