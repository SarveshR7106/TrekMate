# Trekking Booking System

A Flask-based web application for managing trek bookings, with separate dashboards for **Admin**, **Staff**, and **Users (Trekkers)**.

## Features

**Admin**
- View total treks, bookings, users, and staff at a glance
- Approve/reject pending staff signup requests
- Search treks, staff, or users by ID
- View, create, and manage all treks
- Reassign staff to treks
- Blacklist staff or users

**Staff**
- View assigned treks
- Open/close treks
- Update available slots
- Remove participants from a trek

**User (Trekker)**
- Sign up and log in
- Browse all treks with filters (difficulty, location)
- Search a trek by ID
- Book or cancel a trek slot

**Auth**
- Role-based login/signup for Admin, Staff, and Users
- Session-based access control on all protected routes

## Tech Stack

- **Backend:** Python, Flask
- **ORM:** Flask-SQLAlchemy
- **Database:** SQLite
- **Templating:** Jinja2
- **Frontend:** HTML5, Bootstrap

## Database Schema

| Table | Description |
|---|---|
| `admin` | Admin login credentials |
| `staff` | Staff details, status, and trek assignment |
| `user` | Trekker details and status |
| `trek` | Trek details, slots, and assigned staff |
| `booking` | Junction table linking users to treks |

## Project Structure

```
├── app.py                  # Main Flask app, routes, and models
├── templates/
│   ├── base.html
│   ├── admin.html
│   ├── user.html
│   ├── staff.html
│   └── ...
├── Trekking.db              # SQLite database
└── README.md
```

## Setup & Installation

1. Clone the repository
   ```bash
   git clone <repo-url>
   cd trekking-booking-system
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install flask flask_sqlalchemy
   ```

3. Run the application
   ```bash
   python app.py
   ```

4. Open in browser
   ```
   http://127.0.0.1:5000/
   ```

## Routes Overview

| Route | Description |
|---|---|
| `/` | Home / login redirect |
| `/signup` | User/Staff signup |
| `/login` | Login for all roles |
| `/logout` | Logout |
| `/admin` | Admin dashboard |
| `/admin/trek-management` | Create/manage treks |
| `/admin/search` | Search treks/staff/users |
| `/admin/staff-approval/<staff_id>` | Approve/reject staff |
| `/admin/staff-blacklist/<staff_id>` | Blacklist staff |
| `/admin/user-blacklist/<user_id>` | Blacklist user |
| `/user` | User dashboard |
| `/user/search` | Search trek by ID |
| `/user/trek_booking/<trek_id>` | Book a trek |
| `/user/trek_cancelling/<trek_id>` | Cancel a booking |
| `/staff` | Staff dashboard |
| `/staff/trek-open/<trek_id>` | Open a trek |
| `/staff/trek-close/<trek_id>` | Close a trek |
| `/staff/update-slots/<trek_id>` | Update available slots |
| `/staff/remove-participant/<booking_id>` | Remove a booking participant |

## Admin Credentials

Username: admin
Password: admin123
