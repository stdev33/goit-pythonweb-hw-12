# goit-pythonweb-hw-12

Homework 10. Fullstack Web Development with Python at GoIT Neoversity

# Contacts API

This is a RESTful API for managing contacts using FastAPI and PostgreSQL. The API allows users to create, read, update, delete, and search for contacts. It also includes features like:

## Features
- CRUD operations for contacts
- Search functionality for contacts by name, surname, or email
- Endpoint for retrieving contacts with upcoming birthdays
- JWT-based authentication and authorization
- Email verification for new users
- Avatar upload functionality using Cloudinary
- Rate limiting for the `/me` endpoint to prevent abuse
- CORS enabled for cross-origin requests
- Fully documented API using Swagger (available at `/docs`)
- Role-based access control for "user" and "admin"
- HTML-based login and dashboard for authenticated users
- Admin-only UI for changing user roles

## Prerequisites
Before running the application, ensure you have:
- **Docker** installed
- **Docker Compose** installed

## Setup Instructions

### Step 1: Create `.env` File
Ensure your `.env` file includes the following configurations:

```env
FRONTEND_URL=http://localhost:8000

POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=contacts_db
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@goit-pythonweb-hw-12-postgres:5432/${POSTGRES_DB}
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM=your-email
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=yours-api-key
CLOUDINARY_API_SECRET=yours-api-secret
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_CACHE_EXPIRATION=300
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_secure_password
```

### Step 2: Build and Run the Application Using Docker Compose
Run the following command to build the Docker images and start the containers:

```bash
docker-compose up --build
```

This command will:
- Build the API image
- Create and start the PostgreSQL database container
- Start the Contacts API container

### Step 3: Access the API Documentation
Once the containers are running, you can access the Swagger documentation at:
- [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints

### Admin Panel (HTML UI)

#### Login Form
**GET** `/auth/login-form`  
- Displays an HTML login form.

#### Login Submission
**POST** `/auth/login-html`  
- Accepts login form data and sets an access token cookie.

#### Dashboard
**GET** `/dashboard`  
- Shows a simple dashboard for authenticated users.

#### Logout
**GET** `/logout`  
- Logs the user out and clears the access token.

#### Change User Role Form
**GET** `/auth/change-role-form`  
- HTML form accessible only to admins to change user roles.

#### Change User Role Submission
**POST** `/auth/change-role`  
- Admin-only route to change a user's role via email input.

### Authentication and User Management

### 1. Register a New User
**POST** `/auth/register`
- **Request Body:**
  ```json
  {
    "username": "exampleuser",
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response:** Returns the created user with status `201 Created`.

### 2. Verify Email
**GET** `/auth/verify-email?token=<token>`
- Verifies the user's email using the verification token.
- **Response:** `200 OK` with message "Email successfully verified!"

### 3. Login to Generate Access Token
**POST** `/auth/login`
- **Request Body:** (Form Data)
  ```json
  {
    "username": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response:** Access token in JSON format for use in authenticated requests.

### 4. Access User Profile Information
**GET** `/me`
- Retrieves the profile information of the currently authenticated user.
- **Response:** Returns user data.

### 5. Upload Avatar
**POST** `/upload-avatar/`
- **Access:** Admin only
- **Request Body:** Uploads a file to Cloudinary and updates the admin's avatar URL.

---

### Contacts Management

### 6. Create Contact
**POST** `/contacts/`
- **Request Body:**
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "123456789",
    "birthday": "1990-01-01",
    "additional_info": "Friend from work"
  }
  ```

### 7. Get All Contacts
**GET** `/contacts/`

### 8. Get Contact by ID
**GET** `/contacts/{contact_id}`

### 9. Update Contact
**PUT** `/contacts/{contact_id}`
- **Request Body:** Partial or full update for contact fields.

### 10. Delete Contact
**DELETE** `/contacts/{contact_id}`

### 11. Search Contacts
**GET** `/search?query=<value>`
- Search by first name, last name, or email.

### 12. Get Upcoming Birthdays
**GET** `/birthdays`
- Retrieves contacts with birthdays in the next 7 days.

---

## Notes
- Ensure the `.env` file is correctly configured before starting the application.
- Run `docker-compose down` to stop the containers when finished.
- The `/upload-avatar` endpoint is now restricted to admin users only.
- To manage roles, login via the HTML UI and use the `/auth/change-role-form` page.
