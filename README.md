# ET Blog -- Backend API

ET Blog is a **Django REST API** for a blogging platform, designed with
a strong focus on **backend correctness**, **data integrity**, and
**real-world API patterns**. This project is API-first and intentionally
UI-agnostic.

------------------------------------------------------------------------

## 🚀 Features

### 🔐 Authentication & Users

-   Custom User model
-   JWT authentication using **SimpleJWT**
-   Secure password hashing
-   Soft delete for users
-   Proper handling of unique constraints with soft delete
-   Admin-safe and API-safe user visibility

### 📝 Posts

-   Draft & published posts
-   Auto-generated unique slugs
-   Categories & tags (slug-based)
-   Image uploads (MEDIA handling)
-   Soft delete support
-   Author-based permissions

### 💬 Comments

-   Comment system linked to posts
-   Soft delete support
-   Request throttling for abuse prevention

### 📖 API & Documentation

-   Django REST Framework (DRF)
-   Swagger UI & ReDoc via **drf-spectacular**
-   Search, filtering, ordering & pagination
-   Clean, predictable API responses

### 🐳 Docker & Database

-   PostgreSQL
-   Dockerized setup using `docker-compose`
-   Persistent database & media volumes
-   Environment-based configuration

------------------------------------------------------------------------

## 🧱 Tech Stack

-   **Backend:** Django, Django REST Framework
-   **Auth:** SimpleJWT (JWT-based auth)
-   **Database:** PostgreSQL
-   **Docs:** drf-spectacular (Swagger / ReDoc)
-   **Containerization:** Docker, Docker Compose
-   **Language:** Python 3

------------------------------------------------------------------------

## ⚙️ Local Development Setup

``` bash
git clone https://github.com/S-308/et_blog.git
cd et_blog
pip install -r requirements.txt
Create .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

------------------------------------------------------------------------

## 🐳 Docker Setup

``` bash
docker-compose up --build
```

------------------------------------------------------------------------

## 📘 API Documentation

-   Swagger: `/api/docs/`
-   ReDoc: `/api/redoc/`

------------------------------------------------------------------------

## 👤 Author

**Soham**\

