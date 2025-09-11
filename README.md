# Online Menu Backend

**Online Menu Backend** is a Django-based API designed to help restaurants and coffee shops manage their online menus. This API allows restaurant owners to create and manage menu categories and products efficiently. Customers can browse menu categories and view product details through a well-structured interface.

## Table of Contents

-   [Features](#features)
-   [Prerequisites](#prerequisites)
-   [Installation](#installation)
-   [License](#license)

## Features

-   **Monitoring**: Track System Metrics and Logs.
-   **JWT Authentication**: Secure authentication using JSON Web Tokens (JWT).
-   **Debug Toolbar**: Optionally enable Django's Debug Toolbar for development.
-   **Rate Limiting**: Implement throttling to limit the number of API requests per user.
-   **CORS Support**: Enable integration with frontend applications hosted on different domains.
-   **Email Integration**: Send automated emails via SMTP for various activities (e.g., user actions).

## Prerequisites

-   Python 3.12.4+
-   Django 5.2+
-   PostgreSQL (or SQLite for local development)

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/pouria-drd/online-menu-backend.git
    cd online-menu-backend
    ```

2. **Create and Activate a Virtual Environment:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables:**

    Create a `.env` file in the project root and add the following:

    ```ini
    # ---------------------------------------------------------------
    # Base URL and Admin URL Configuration
    # ---------------------------------------------------------------
    BASE_URL="api/"
    ADMIN_URL="admin/"

    # ---------------------------------------------------------------
    # Debugging and Secret Key Configuration
    # ---------------------------------------------------------------
    DEBUG="True"
    ENABLE_DEBUG_TOOLBAR="True"
    SECRET_KEY="django-insecure-..."  # Replace with your own secret key

    # ---------------------------------------------------------------
    # Host and Debugging IPs Configuration
    # ---------------------------------------------------------------
    INTERNAL_IPS=localhost,127.0.0.1
    ALLOWED_HOSTS=localhost,127.0.0.1

    CORS_ALLOW_CREDENTIALS=True
    CORS_ALLOWED_ORIGINS="" # Replace with your allowed origins (separate with commas)
    CSRF_TRUSTED_ORIGINS=""# Replace with your allowed origins (separate with commas)

    # ---------------------------------------------------------------
    # Time Zone and Localization Configuration
    # ---------------------------------------------------------------
    USE_TZ="True"
    USE_I18N="True"
    TIME_ZONE="UTC"

    # ---------------------------------------------------------------
    # Static and Media File Configuration
    # ---------------------------------------------------------------
    STATIC_URL=static/
    STATIC_ROOT=static

    MEDIA_URL=/media/
    MEDIA_ROOT=media

    # ---------------------------------------------------------------
    # API Throttling Configuration
    # ---------------------------------------------------------------
    USER_THROTTLE_RATE="20/minute"
    ANON_THROTTLE_RATE="10/minute"

    # ---------------------------------------------------------------
    # Email Configuration
    # ---------------------------------------------------------------
    EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST="smtp.gmail.com"
    EMAIL_PORT="587"
    EMAIL_USE_TLS="True"
    EMAIL_HOST_USER="" # Replace with your email address
    EMAIL_HOST_PASSWORD="" # Replace with your email password
    DEFAULT_FROM_EMAIL="" # Replace with your email address
    MAX_RETRY_ATTEMPTS="3"

    # ---------------------------------------------------------------
    # JWT (JSON Web Token) Configuration
    # ---------------------------------------------------------------
    ACCESS_TOKEN_LIFETIME="15"   # expire after n minutes
    REFRESH_TOKEN_LIFETIME="24"  # expire after n hours
    ```

5. **Run Migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. **Create a Superuser:**

    ```bash
    python manage.py createsuperuser
    ```

7. **Run the Development Server:**

    ```bash
    python manage.py runserver
    ```

    Your project should now be running at `http://127.0.0.1:8000/`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries, please contact [pouriadrd@gmail.com](mailto:pouriadrd@gmail.com).
