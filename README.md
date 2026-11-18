# Student Management System

A beginner-friendly student records application built with Python, Streamlit, PyMongo, and MongoDB Atlas. Student records are stored in the `students` collection in the `StudentDB` database.

## Requirements

- Python 3.10 or newer
- A MongoDB Atlas account and an Atlas cluster
- Visual Studio Code (recommended)

## Installation

Open the project folder in VS Code. In the VS Code terminal, create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents environment activation, you can run commands using the virtual environment directly, for example `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

Install the required libraries:

```powershell
python -m pip install -r requirements.txt
```

## MongoDB Atlas connection

1. In MongoDB Atlas, create a database user and allow your computer's IP address in Network Access.
2. In your existing project `.env` file, add a setting named `MONGODB_URI`. Use the connection string provided by Atlas as its value. Do not share or commit this value.
3. Ensure `.env` is listed in `.gitignore`.

The application loads the URI from `.env` and does not display it. It creates the `StudentDB` database and `students` collection when needed, and creates a unique index on USN. If a URI is missing or the database cannot be reached, the app displays a setup message without printing credentials.

## Add sample students

After setting up the Atlas connection, run this once from the project folder:

```powershell
python sample_data.py
```

The script adds ten sample records and skips any USN that already exists, so it is safe to run again.

## Run the application

```powershell
python -m streamlit run app.py
```

Streamlit opens the application in your browser. If it does not open automatically, follow the local URL printed in the terminal.

## Features

- Dashboard with the total number of students and average marks and attendance
- Add, view, and search student records by USN
- Update all student details, including USN
- Delete a student only after confirming the action
- USN uniqueness enforced by MongoDB; marks and attendance are validated from 0 to 100

## College demonstration checklist

1. Start the app and show the dashboard with the sample records.
2. Add a student with a new USN; try that same USN again to demonstrate duplicate prevention.
3. Search for a student using their USN and show all students.
4. Update a student's name, marks, or attendance and verify the saved value.
5. Try a marks or attendance value outside 0–100 (the form prevents it).
6. Select a student for deletion, show that confirmation is required, then confirm and verify that the record is gone.

All records are stored in MongoDB Atlas; the app is not a mock interface.
