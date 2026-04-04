# Internship Tracking and Management System

A full-stack web application designed for tracking and managing college internships. Built with Python Flask, MySQL, and HTML/CSS/JavaScript.

## Project Structure

- `/backend`: The core Python Flask application, routing, API endpoints, and database connection logic
- `/frontend`: The HTML, CSS, and UI JavaScript files
- `requirements.txt`: Python package dependencies

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL Server

### Local Installation Steps

1. **Navigate to the application folder:**
   ```bash
   cd "College Internship Tracking and Management System"
   ```

2. **Set up a Python Virtual Environment:**
   Run the following commands to create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   
   # On macOS and Linux:
   source venv/bin/activate
   
   # On Windows:
   # venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Configuration:**
   - Ensure your MySQL server service is running.
   - Create a database to be used by the application.
   - You will eventually place your database connection properties inside a `.env` file or within the `backend/app.py` script.

5. **Start the Applicaiton Server:**
   ```bash
   python backend/app.py
   ```

6. **View the Applicaiton:**
   Open a web browser and navigate to `http://localhost:5000/`.
