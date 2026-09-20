# Branded Short-Link & Bio-Link Hub

## Overview
A full-stack, monolithic web application designed for shortening URLs, tracking comprehensive click analytics, and creating customizable "link-in-bio" public profile pages. Built with FastAPI and vanilla JavaScript, it serves as a lightweight, performant alternative to commercial link management platforms.

## Key Features

### Authentication
- Secure **Signup**, **Login**, and **Logout** workflows.
- **JWT authentication** stored securely via **HTTP-only cookies**.
- Strong **Password hashing** using bcrypt.
- Protected API routes and dashboard views.

### Short Links
- Automatically generated 6-character short codes for URLs.
- Support for custom vanity slugs.
- Duplicate slug detection and validation.
- Centralized link management (create, view, delete).
- Fast **HTTP 302 redirects** for shortened URLs.
- Underlying click tracking on redirection.

### Analytics
- **Total clicks** aggregation per link.
- **Clicks over time** visualization (via Chart.js).
- **Device distribution** tracking (Desktop vs. Mobile).
- **Top referrers** tracking (e.g., Direct, Social Media).
- Each click logs Timestamp, Referrer, Device type, and a Hashed IP address to preserve privacy.

### QR Codes
- Dynamic **QR code generation** for every shortened link.
- Supports scanning from mobile devices via a configurable `PUBLIC_BASE_URL`.
- Facilitates seamless LAN testing during local development.

### Bio-Link
- Server-rendered public `/bio/{username}` profile pages.
- Customizable **Display name** and **Bio** text.
- Manage **Custom links** displayed on the profile.
- Built-in visual **Themes**:
  - Minimal Light
  - Dark Slate
  - Gradient

## Technology Stack

**Backend:**
- Python 3
- FastAPI
- SQLAlchemy (ORM)
- SQLite (Development Database)

**Frontend:**
- HTML5 & CSS3
- Vanilla JavaScript
- Jinja2 templates (Server-side rendering)
- Chart.js (Data Visualization)

**Other Libraries & Utilities:**
- `qrcode` & `Pillow` (QR code generation)
- `Passlib` with `bcrypt` (Password hashing)
- `python-jose` (JWT management)
- `python-dotenv` (Environment variable management)
- `slowapi` (Rate limiting)

## System Architecture
The application utilizes a monolithic MVC-style architecture served entirely from a single FastAPI instance:
- **API Layer**: `/api/...` routes handle JSON data exchange, authentication, and core business logic.
- **Frontend Layer**: `/` and `/dashboard` serve Jinja2 HTML templates hydrated dynamically by Vanilla JS fetching from the API routes.
- **Redirection Layer**: `/r/{slug}` handles rapid 302 redirections and asynchronous event logging.
- **Presentation Layer**: `/bio/{username}` serves a server-rendered public profile page based on database configurations.

## Database Design

The application utilizes SQLAlchemy ORM with the following core entities mapped to SQLite tables:

- **User**: Core authentication data including `email`, `username`, `password_hash`, and `created_at`.
- **Link**: Stores the `destination_url` and unique `short_code`, linked via `owner_id` to the User.
- **ClickEvent**: Records individual link interactions, tracking `timestamp`, `referrer`, `device_type`, and `ip_hash`, linked to the parent Link.
- **BioProfile**: Stores public profile configurations such as `display_name`, `bio`, and `theme`, linked 1:1 with the User.
- **BioLink**: Stores individual custom links (`title`, `url`) associated with a specific BioProfile.

## Project Structure

```text
backend/
├── app/
│   ├── main.py              # Application entry point & configuration
│   ├── database.py          # SQLAlchemy engine and session management
│   ├── models/              # Database schema definitions (user, link, bio)
│   ├── schemas/             # Pydantic models for data validation
│   ├── routes/              # FastAPI route controllers (auth, links, analytics, bio, redirect, pages)
│   ├── services/            # Reusable business logic (auth_service, link_service, qr_service)
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # Static assets (CSS, JS)
├── requirements.txt         # Python dependencies
└── .env.example             # Example environment configuration
```

## API Endpoints

FastAPI automatically mounts interactive API documentation at `/docs` (Swagger UI). 

**Authentication**
- `POST /api/auth/signup` - Register a new user
- `POST /api/auth/login` - Authenticate and receive an HTTP-only JWT cookie
- `POST /api/auth/logout` - Clear the authentication cookie

**Links**
- `GET /api/links/` - Retrieve all links for the authenticated user
- `POST /api/links/` - Create a new short link
- `DELETE /api/links/{link_id}` - Delete a specific link
- `GET /api/links/{link_id}/qr` - Generate and return a QR code image

**Analytics**
- `GET /api/analytics/{link_id}` - Retrieve aggregated click statistics for a link

**Bio Profile**
- `GET /api/bio/me` - Retrieve the authenticated user's bio profile
- `PUT /api/bio/me` - Update the user's bio profile
- `POST /api/bio/links` - Add a custom link to the bio profile
- `DELETE /api/bio/links/{link_id}` - Remove a custom link from the bio profile

**Public Routes**
- `GET /r/{short_code}` - Redirect to destination URL and log click
- `GET /bio/{username}` - View public bio profile

## Installation

These instructions are tailored for Windows environments.

1. **Navigate to the backend directory**:
   ```cmd
   cd backend
   ```
2. **Set up a Virtual Environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

## Environment Variables

Create a `.env` file in the `backend/` directory by copying `.env.example`:

```cmd
copy .env.example .env
```

Configure your `.env` file with the following variables:
```env
DATABASE_URL=sqlite:///./shortlink.db
SECRET_KEY=super-secret-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
PUBLIC_BASE_URL=http://127.0.0.1:8000
```

## Running Locally

To run the application for local development (accessible via `localhost`):

```cmd
uvicorn app.main:app --reload
```

## LAN / Mobile QR Testing

To test QR codes by scanning them with your phone on the same Wi-Fi network, the server must be bound to all network interfaces.

1. Find your laptop's local IPv4 address (e.g., `192.168.1.62`):
   ```cmd
   ipconfig
   ```
2. Update the `PUBLIC_BASE_URL` in your `.env` file to match this IP address:
   ```env
   PUBLIC_BASE_URL=http://192.168.1.62:8000
   ```
3. Start the application bound to `0.0.0.0`:
   ```cmd
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Documentation
Once the server is running, you can access the automatically generated interactive API documentation (Swagger UI) by navigating to:
`http://127.0.0.1:8000/docs`

## Security Considerations
- **Password Hashing**: User passwords are encrypted using bcrypt before database insertion.
- **JWT Authorization**: API endpoints are secured with JSON Web Tokens.
- **HTTP-Only Cookies**: Tokens are stored in secure, HTTP-only cookies to mitigate Cross-Site Scripting (XSS) token theft.
- **Input Validation**: Strict input validation is enforced via Pydantic schemas.
- **Rate Limiting**: Implementation via `slowapi` protects critical routes from abuse.
- **Environment Management**: Secrets are managed securely via `.env` files which are excluded from source control.

## Known Limitations
- Forgot/Reset Password functionality via email delivery is currently not implemented in this assessment build.
- SQLite is utilized for development convenience; concurrent write performance is limited under heavy load.
- IP addresses are hashed without salting, which is sufficient for basic privacy but could be vulnerable to rainbow table attacks.
- Rate limiting relies on in-memory storage, meaning counters reset upon application restart.

## Future Improvements
- **PostgreSQL**: Migrate to a robust relational database for production deployments.
- **Redis**: Implement Redis for caching the `/r/{slug}` redirection endpoint to improve resolution latency.
- **Background Analytics Processing**: Utilize Celery or similar background workers to process click events asynchronously.
- **Production Email Service**: Integrate SendGrid or AWS SES for account recovery and notifications.
- **Cloud Avatar Storage**: Support user avatar uploads via AWS S3 or Google Cloud Storage.
- **Geographic Analytics**: Integrate an IP-to-location service (e.g., MaxMind) to display click origins on a map.
- **Custom Domains**: Allow users to configure DNS settings to use their own domains for short links.
- **Link Expiration**: Add optional TTL (Time to Live) configurations for temporary short links.
- **Docker & CI/CD**: Containerize the application and set up automated testing pipelines.

## Demo Flow

To evaluate the application's core feature set, follow this workflow:

1. **Signup**: Create a new account at `/signup`.
2. **Login**: Authenticate at `/login`.
3. **Dashboard**: Navigate the main interface.
4. **Create short link**: Paste a long URL and generate a shortened equivalent.
5. **Open short link**: Test the redirection.
6. **Track click**: Observe the dashboard update.
7. **View analytics**: Review the Chart.js visualizations for your link.
8. **Generate QR**: Click the QR button to view the link's QR code.
9. **Scan QR from phone**: Ensure LAN configuration is set up as detailed above, and scan to test mobile access.
10. **Configure Bio Profile**: Navigate to the Bio tab and set up a display name, theme, and custom links.
11. **Open public Bio page**: Visit `/bio/{username}` to see the final public result.



- Landing page
- Signup/Login
- Dashboard
- Link management
- Analyticsgit statu
- QR code
- Bio editor
- Public Bio page

## Repository
https://github.com/Ankit-166/Repository-name-branded-short-link-hub

## License
*(Standard MIT or applicable open-source license)*
