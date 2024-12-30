# Bus Booking System

## Project Overview

The Bus Booking System is a web application designed to facilitate the booking of bus tickets. It provides a user-friendly interface for users to register, log in, and book tickets for various bus routes. The system also includes an admin panel for managing users, buses, and destinations. Key features include user authentication, a responsive design, form validation, and security enhancements.

### Features

1. **User Authentication and Authorization:**
   - Secure user registration, login, and logout.
   - User roles (admin and regular user) to control access to different parts of the application.

2. **Improved User Interface:**
   - Design using Bootstrap.
   - Carousel on the user and admin main pages for a visually appealing interface.

3. **Enhanced Booking System:**
   - Form for users to book bus tickets.
   - Validation for booking forms to ensure data integrity.
   - Ability for users to view and cancel their bookings.

4. **Admin Dashboard Enhancements:**
   - Central hub for managing users, buses, and destinations.
   - Buttons for viewing, creating, updating, and deleting records.

5. **Defensive Programming:**
   - Input validation and sanitization.
   - Error handling and exception management.
   - Secure coding practices to prevent SQL injection and XSS.

6. **Security Enhancements:**
   - Rate limiting to prevent brute force attacks.
   - CSRF protection for forms.
   - Secure session management.

## Installation and Setup Guide

### Steps to Set Up the Development Environment

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Devcavi19/CSEC311-FINALS-PROJECT
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. **Run the Application:**
   ```bash
   flask run
   ```

### Dependencies and Requirements

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-Bcrypt
- Flask-WTF
- Flask-Limiter
- SQLite

## Usage

### User Manual

1. **Login:**
   - Navigate to the login page and enter your username and password.
   - Click the "Login" button to access your account.

2. **Register:**
   - If you don't have an account, click the "Create new" button on the login page.
   - Fill out the registration form with your username, email, and password.
   - Click the "Create account" button to register.

3. **Book a Ticket:**
   - After logging in, navigate to the "Book Ticket" page.
   - Select a bus, destination, and travel date from the dropdown menus.
   - Click the "Book Ticket" button to confirm your booking.

4. **View and Cancel Bookings:**
   - Navigate to the "My Tickets" page to view your bookings.
   - Click the "Cancel" button next to a booking to cancel it.

5. **Admin Panel:**
   - Admin users can access the admin panel to manage users, buses, and destinations.
   - Use the buttons to view, create, update, and delete records.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## References and Resources

1. **Flask Documentation:**
   - https://flask.palletsprojects.com/

2. **SQLAlchemy Documentation:**
   - https://docs.sqlalchemy.org/

3. **WTForms Documentation:**
   - https://wtforms.readthedocs.io/

4. **Flask-Login Documentation:**
   - https://flask-login.readthedocs.io/

5. **Flask-Bcrypt Documentation:**
   - https://flask-bcrypt.readthedocs.io/

6. **Flask-Limiter Documentation:**
   - https://flask-limiter.readthedocs.io/

7. **Bootstrap Documentation:**
   - https://getbootstrap.com/docs/4.0

8. **Python Logging Documentation:**
   - https://docs.python.org/3/library/logging.html

9. **Jinja Documentation:**
   - https://jinja.palletsprojects.com/