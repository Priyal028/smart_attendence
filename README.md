# Smart Attendance System

A modern, secure, and efficient attendance tracking system using QR codes, GPS validation, and feedback collection. This web application is built with Flask and provides separate interfaces for administrators and students.

## Features

### For Administrators
- Secure admin login system
- Create and manage events with location parameters
- Generate unique QR codes for each event
- View attendance analytics with visual charts
- Access student feedback and ratings
- Dashboard with comprehensive event statistics

### For Students
- Easy email-based login
- Scan QR codes to mark attendance
- Location validation using GPS coordinates
- Submit feedback and ratings for events
- User-friendly dashboard interface

## Security Features
- GPS location validation to ensure physical presence
- QR code authentication for each event
- Secure session management
- Admin authentication using Flask-Login

## Technical Stack

### Backend
- Flask (Python web framework)
- SQLAlchemy (Database ORM)
- Flask-Login (Authentication management)

### Frontend
- HTML/CSS/JavaScript
- Bootstrap (assumed from project structure)
- Charts for analytics visualization

### Database
- SQLite (attendance.db)

### Additional Libraries
- qrcode: For QR code generation
- reportlab: PDF generation
- pillow: Image processing
- geopy: GPS coordinates handling
- pandas: Data analysis
- matplotlib: Chart generation

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## Database Structure

The application uses the following database models:

- **Admin**: Stores administrator credentials
- **Student**: Manages student information
- **Event**: Stores event details including location parameters
- **Attendance**: Records attendance data
- **Feedback**: Stores student feedback and ratings

## Default Admin Credentials
- Username: admin
- Password: admin123

## Usage

### Admin Workflow
1. Login using admin credentials
2. Create new events with location parameters
3. Generate QR codes for events
4. Monitor attendance and feedback through analytics

### Student Workflow
1. Login using email
2. Access available events
3. Scan event QR code
4. Verify location
5. Mark attendance
6. Submit feedback

## Features in Detail

### Location Validation
- Uses geopy to calculate distance between student and event location
- Configurable radius for each event
- Real-time GPS validation

### Analytics
- Visual representation of attendance statistics
- Event-wise attendance percentage
- Feedback analysis and ratings visualization
- Exportable data formats

### Feedback System
- Rating-based feedback
- Dropdown options for categorized feedback
- Short answer responses
- Event-specific feedback collection

## Directory Structure
```
smart-attendance/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
├── database/          # Database directory
│   └── attendance.db
├── static/           # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   ├── attendance_chart.png
│   └── feedback_chart.png
└── templates/        # HTML templates
    ├── admin_dashboard.html
    ├── analytics.html
    ├── feedback_form.html
    ├── index.html
    └── student_dashboard.html
```

## Contributing
Feel free to contribute to this project by:
1. Forking the repository
2. Creating a feature branch
3. Committing your changes
4. Pushing to the branch
5. Creating a Pull Request