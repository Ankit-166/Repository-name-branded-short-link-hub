# Branded Short-Link & Bio-Link Hub

## Overview
A full-stack web application designed for shortening URLs, tracking click analytics, and creating customizable "link-in-bio" public profile pages. 

## Features
- **Authentication**: JWT based auth (signup, login, logout) with bcrypt password hashing. Stored in HTTP-only cookies.
- **Short Links**: Create 6-character random slugs or custom slugs. Checks for duplicates. 
- **QR Codes**: Automatically generates a downloadable QR code for every shortened link.
- **Analytics**: Tracks total clicks, clicks over time (Chart.js), device types, and top referrers.
- **Link-in-Bio**: Create a public `/bio/{username}` profile with custom links, display name, bio, and themes (Minimal Light, Dark Slate, Gradient).
- **Security**: Rate limiting on application layer, HTTP-only secure cookie strategies for auth.

## Technology Stack
- **Backend**: Python 3, FastAPI
- **Database**: SQLite, SQLAlchemy ORM
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 (Jinja2 Templates)
- **Data Vis**: Chart.js
- **Auth**: Passlib (bcrypt), python-jose

## Architecture
The application uses a monolithic MVC-style architecture served entirely from FastAPI.
- `/api/...` routes handle JSON data exchange and backend logic.
- `/` and `/dashboard` serve HTML templates hydrated by Vanilla JS fetching from the `/api/...` routes.
- `/r/{slug}` handles the quick 302 redirection and event logging.
- `/bio/{username}` serves a server-rendered public profile page based on DB data.

## Database Design
- **User**: Core authentication data.
- **Link**: Stores `destination_url` and `short_code`.
- **ClickEvent**: Tracks `timestamp`, `referrer`, `device_type`, and `ip_hash` for each click.
- **BioProfile**: Stores bio information and theme preference.
- **BioLink**: Links associated with a specific BioProfile.

## Project Structure
```
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/ (user, link, bio)
│   ├── schemas/ (user, link, bio)
│   ├── routes/ (auth, links, analytics, bio, redirect, pages)
│   ├── services/ (auth_service, link_service, qr_service)
│   ├── templates/ (HTML files)
│   └── static/ (CSS, JS)
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation & Running Locally

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```
2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env and update SECRET_KEY
   ```
5. **Run the Application Locally (localhost)**:
   ```bash
   uvicorn app.main:app --reload
   ```
   
6. **Run the Application for LAN Access (Testing from Phone)**:
   To test QR codes and access the app from your phone on the same Wi-Fi network:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *Make sure to set `PUBLIC_BASE_URL=http://<your-laptop-ip>:8000` in your `.env` file before starting, so the QR codes point to your laptop's IP instead of localhost.*

## Demo Credentials
To create demo data:
1. Go to `http://127.0.0.1:8000/signup` and create an account (e.g., `username: demo`, `password: password123`).
2. Log in at `http://127.0.0.1:8000/login`.
3. Start creating links and bio profiles from the dashboard!

## Known Limitations
- The "Forgot/Reset Password" functionality is not fully implemented with email sending in this assessment build.
- SQLite is used for development/assessment purposes; PostgreSQL is recommended for production.
- IP addresses are currently hashed without salting, which is fine for basic privacy but could be improved.
- Rate limiting uses a basic in-memory setup with `slowapi` which resets on server restart.

## Future Improvements
- Add Redis for caching the `redirect` endpoint to speed up link resolution.
- Set up a background worker (e.g., Celery) to process click analytics asynchronously so the redirect isn't blocked by DB writes.
- Support file uploads for custom Avatars on Bio profiles.
- Add geographic (Country/City) lookup based on IP.
