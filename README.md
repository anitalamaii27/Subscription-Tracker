# Subscription Tracker

A secure and fully-featured Flask web application for tracking personal subscriptions and recurring expenses.

## Features

- User authentication: register, login, logout, password reset
- Add, edit, and delete subscriptions
- Monthly summary of expenses
- Visual charts for:
  - Subscription amounts per subscription
  - Monthly totals over the year
- Import/export subscriptions via CSV
- Session management and auto-logout after inactivity
- Secure password storage using hashing

## Technologies Used

- Python 3.11+
- Flask
- SQLite
- HTML / CSS / JavaScript
- Chart.js for interactive charts
- Git for version control

## Installation

1. Clone the repository:
git clone https://github.com/anitalamaii27/Subscription-Tracker.git
cd Subscription-Tracker/auth_app

2. Create a virtual environment:
bash
Copy code
python -m venv venv
source venv/Scripts/activate   # Windows
# or
source venv/bin/activate       # Mac/Linux

3. Install dependencies:
bash
Copy code
pip install flask werkzeug

4. Initialize the database:
bash
Copy code
python init_db.py
python add_session_column.py  # Adds session_token column if needed

5. Run the app:
python app.py

6. Open your browser and go to http://127.0.0.1:5000


Usage
- Register a new account
- Add subscriptions with name, amount, billing date, and recurring type
- View dashboard with charts and summaries
- Export or import CSV files for your subscriptions
- Keep track of upcoming billing dates
