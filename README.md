# Booking System Backend

Django REST API for a booking system with user authentication and booking management.

## Features

### User Authentication
- User registration with email verification
- JWT-based authentication
- Login/Logout functionality
- Password reset via email
- Editable user profiles
- Secure password storage (Argon2)

### Booking System
- Create, view, update, and cancel bookings
- Resource management (rooms, equipment, facilities)
- Availability checking to prevent double-booking
- Booking status lifecycle (pending, confirmed, cancelled, completed)
- User can view their own bookings
- Admin can manage all bookings
- Business rules and validation

## Technology Stack

- **Django 6.0.2** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database
- **JWT (Simple JWT)** - Token-based authentication
- **CORS Headers** - Cross-origin resource sharing for React frontend

## Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- pip and virtualenv

### Installation

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup PostgreSQL database:**
   - Create a PostgreSQL database named `booking_system_db`
   - Or use your own database name and update the .env file

4. **Configure environment variables:**
   - Copy `.env.example` to create a `.env` file
   - Update the values in `.env` with your configuration:
     ```bash
     # Example .env content:
     SECRET_KEY=your-secret-key-here
     DEBUG=True
     DB_NAME=booking_system_db
     DB_USER=postgres
     DB_PASSWORD=your-password
     DB_HOST=localhost
     DB_PORT=5432
     EMAIL_HOST_USER=your-email@gmail.com
     EMAIL_HOST_PASSWORD=your-app-password
     ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication Endpoints

- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login user
- `POST /api/users/logout/` - Logout user
- `POST /api/users/token/refresh/` - Refresh JWT token
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/update/` - Update user profile
- `POST /api/users/password/change/` - Change password
- `POST /api/users/password/reset/` - Request password reset
- `POST /api/users/password/reset/confirm/` - Confirm password reset

### Booking Endpoints

- `GET /api/bookings/list/` - List all bookings (user's own or all for admin)
- `POST /api/bookings/list/` - Create a new booking
- `GET /api/bookings/list/{id}/` - Get booking details
- `PUT /api/bookings/list/{id}/` - Update booking
- `DELETE /api/bookings/list/{id}/` - Delete booking
- `POST /api/bookings/list/{id}/cancel/` - Cancel booking
- `GET /api/bookings/list/upcoming/` - Get upcoming bookings
- `GET /api/bookings/list/past/` - Get past bookings
- `PATCH /api/bookings/list/{id}/update_status/` - Update booking status (admin only)
- `GET /api/bookings/availability/` - Check resource availability

### Resource Endpoints

- `GET /api/bookings/resources/` - List all resources
- `POST /api/bookings/resources/` - Create resource (admin only)
- `GET /api/bookings/resources/{id}/` - Get resource details
- `PUT /api/bookings/resources/{id}/` - Update resource (admin only)
- `DELETE /api/bookings/resources/{id}/` - Delete resource (admin only)
- `GET /api/bookings/resources/available/` - Get available resources

## API Documentation

Once the server is running, you can access interactive API documentation at:

- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` with your superuser credentials.

## Testing

Run tests with:
```bash
pytest
```

## Project Structure

```
django-booking-backend/
├── booking_system/          # Main project settings
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI application
├── users/                  # User authentication app
│   ├── models.py          # User and PasswordResetToken models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   └── urls.py            # URL routing
├── bookings/              # Booking management app
│   ├── models.py          # Booking and Resource models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   └── urls.py            # URL routing
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | (required) |
| DEBUG | Debug mode | True |
| DB_NAME | Database name | booking_system_db |
| DB_USER | Database user | postgres |
| DB_PASSWORD | Database password | (required) |
| DB_HOST | Database host | localhost |
| DB_PORT | Database port | 5432 |
| EMAIL_HOST | SMTP host | smtp.gmail.com |
| EMAIL_PORT | SMTP port | 587 |
| EMAIL_HOST_USER | Email username | (required) |
| EMAIL_HOST_PASSWORD | Email password | (required) |
| FRONTEND_URL | Frontend URL | http://localhost:3000 |

## Notes

- For Gmail, use an App Password instead of your regular password
- In production, set DEBUG=False and configure proper ALLOWED_HOSTS
- Keep your SECRET_KEY secure and never commit it to version control
- The console email backend is used by default for development
