# University Mess Management System

A comprehensive web-based mess management system for university hostels built with Flask, HTML/CSS, and MySQL.

## Features

### Admin Features
- **Dashboard**: Real-time statistics and overview
- **Student Management**: Add, edit, and delete students
- **Menu Management**: Create and manage weekly menus
- **Expense Tracking**: Monitor and categorize mess expenses
- **Complaint Management**: View and resolve student complaints
- **Notice Board**: Post important announcements
- **Reports**: View meal counts, expenses, and statistics

### Student Features
- **Dashboard**: Personalized overview with today's menu and meal status
- **View Menu**: Check daily and weekly meal plans
- **Meal Confirmation**: Confirm attendance for meals to reduce food waste
- **Complaint System**: Submit feedback and complaints
- **Food Rating**: Rate meal quality and provide feedback

## Technology Stack

- **Backend**: Python with Flask framework
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: MySQL
- **Authentication**: bcrypt for password hashing

## Installation

### Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd messProject
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL Database**
   - Start MySQL server
   - Run the database setup script:
   ```bash
   python database_setup.py
   ```
   This will create the `mess_management` database and all required tables.

4. **Configure Database Connection**
   - Edit the MySQL configuration in `app.py`:
   ```python
   app.config['MYSQL_HOST'] = 'localhost'
   app.config['MYSQL_USER'] = 'your_mysql_username'
   app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
   app.config['MYSQL_DB'] = 'mess_management'
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the Application**
   - Open your browser and go to `http://localhost:5000`

## Default Credentials

### Admin Login
- **Username**: admin
- **Password**: admin123

### Student Login
- Students must be added by the admin before they can log in
- Use the Student ID and password set by the admin

## Project Structure

```
messProject/
├── app.py                 # Main Flask application
├── database_setup.py      # Database initialization script
├── requirements.txt        # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── admin/            # Admin templates
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── students.html
│   │   ├── add_student.html
│   │   ├── edit_student.html
│   │   ├── menu.html
│   │   ├── add_menu.html
│   │   ├── edit_menu.html
│   │   ├── expenses.html
│   │   ├── add_expense.html
│   │   ├── complaints.html
│   │   ├── notices.html
│   │   └── add_notice.html
│   └── student/          # Student templates
│       ├── login.html
│       ├── dashboard.html
│       ├── menu.html
│       ├── meal_confirmation.html
│       ├── complaints.html
│       └── food_rating.html
└── static/
    └── css/
        └── style.css     # Main stylesheet
```

## Database Schema

The system uses the following tables:

- **admin**: Admin user accounts
- **students**: Student information and credentials
- **menu**: Daily meal menus
- **meal_confirmation**: Student meal attendance records
- **complaints**: Student complaints and feedback
- **expenses**: Mess expense tracking
- **notices**: Administrative notices
- **food_ratings**: Student meal ratings and feedback

## Key Features Explained

### Food Waste Reduction
- Students confirm meals in advance
- Kitchen prepares food based on confirmed numbers
- Reduces over-preparation and waste

### Expense Management
- Categorized expense tracking
- Monthly expense summaries
- Budget monitoring and reporting

### Communication System
- Notice board for important announcements
- Complaint system for student feedback
- Food rating system for quality control

### Security Features
- Password hashing with bcrypt
- Session-based authentication
- Role-based access control
- No public registration (admin-only student creation)

## Usage Guidelines

### For Administrators
1. Log in with admin credentials
2. Add students to the system
3. Create weekly menus
4. Monitor meal confirmations
5. Track expenses and generate reports
6. Address student complaints promptly

### For Students
1. Log in with provided credentials
2. View daily and weekly menus
3. Confirm meals in advance
4. Submit complaints for issues
5. Rate food quality for feedback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository or contact the development team.

---

**Note**: Make sure to change the default admin password in a production environment for security reasons.
