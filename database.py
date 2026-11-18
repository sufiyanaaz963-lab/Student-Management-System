"""MongoDB connection and student database operations."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError


def connect_to_mongodb() -> Collection:
    """Connect to Atlas and return the students collection."""
    env_file = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_file)

    connection_string = os.getenv("MONGODB_URI")
    if not connection_string:
        raise ValueError(
            "MONGODB_URI is missing. Add your Atlas connection string to the "
            "MONGODB_URI setting in the project's .env file."
        )

    client = None
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        collection = client["StudentDB"]["students"]
        collection.create_index("usn", unique=True, name="unique_usn")
        return collection
    except PyMongoError:
        if client is not None:
            client.close()
        raise RuntimeError(
            "Could not connect to or prepare the StudentDB database. Check "
            "your Atlas network access, database user permissions, and that "
            "existing student USNs are unique."
        ) from None


def validate_student(student: dict[str, Any]) -> dict[str, Any]:
    """Clean student fields and validate values before saving."""
    cleaned_student = {
        "usn": str(student.get("usn", "")).strip().upper(),
        "name": str(student.get("name", "")).strip(),
        "branch": str(student.get("branch", "")).strip(),
        "semester": student.get("semester"),
        "marks": student.get("marks"),
        "attendance": student.get("attendance"),
    }

    for field in ("usn", "name", "branch"):
        if not cleaned_student[field]:
            raise ValueError(f"{field.title()} cannot be empty.")

    try:
        cleaned_student["semester"] = int(cleaned_student["semester"])
        cleaned_student["marks"] = float(cleaned_student["marks"])
        cleaned_student["attendance"] = float(cleaned_student["attendance"])
    except (TypeError, ValueError):
        raise ValueError("Semester, marks, and attendance must be numbers.") from None

    if cleaned_student["semester"] < 1:
        raise ValueError("Semester must be at least 1.")
    for field in ("marks", "attendance"):
        if not 0 <= cleaned_student[field] <= 100:
            raise ValueError(f"{field.title()} must be between 0 and 100.")

    return cleaned_student


def add_student(collection: Collection, student: dict[str, Any]) -> None:
    """Insert one student, rejecting a USN that is already in the collection."""
    cleaned_student = validate_student(student)
    try:
        collection.insert_one(cleaned_student)
    except DuplicateKeyError:
        raise ValueError(
            f"A student with USN {cleaned_student['usn']} already exists."
        ) from None
    except PyMongoError:
        raise RuntimeError("Could not add the student. Check the database connection.") from None


def get_all_students(collection: Collection) -> list[dict[str, Any]]:
    """Return all students sorted by USN."""
    try:
        return list(collection.find({}, {"_id": 0}).sort("usn", 1))
    except PyMongoError:
        raise RuntimeError("Could not load students. Check the database connection.") from None


def get_student_by_usn(collection: Collection, usn: str) -> dict[str, Any] | None:
    """Find one student using their USN."""
    try:
        return collection.find_one({"usn": usn.strip().upper()}, {"_id": 0})
    except PyMongoError:
        raise RuntimeError("Could not search students. Check the database connection.") from None


def update_student(
    collection: Collection, current_usn: str, student: dict[str, Any]
) -> None:
    """Update a student's details, including their USN if it has changed."""
    current_usn = current_usn.strip().upper()
    if not current_usn:
        raise ValueError("Select a student by USN before updating.")

    cleaned_student = validate_student(student)
    try:
        result = collection.update_one(
            {"usn": current_usn},
            {"$set": cleaned_student},
        )
        if result.matched_count == 0:
            raise LookupError(f"No student was found with USN {current_usn}.")
    except DuplicateKeyError:
        raise ValueError(
            f"A student with USN {cleaned_student['usn']} already exists."
        ) from None
    except PyMongoError:
        raise RuntimeError(
            "Could not update the student. Check the database connection."
        ) from None


def delete_student(collection: Collection, usn: str) -> None:
    """Delete one student by USN."""
    normalized_usn = usn.strip().upper()
    if not normalized_usn:
        raise ValueError("Select a student by USN before deleting.")

    try:
        result = collection.delete_one({"usn": normalized_usn})
        if result.deleted_count == 0:
            raise LookupError(f"No student was found with USN {normalized_usn}.")
        if result.deleted_count != 1:
            raise RuntimeError(
                f"Expected to delete one student with USN {normalized_usn}, "
                f"but MongoDB reported {result.deleted_count}."
            )
    except PyMongoError:
        raise RuntimeError(
            "Could not delete the student. Check the database connection."
        ) from None


def insert_sample_students(
    collection: Collection, students: list[dict[str, Any]]
) -> int:
    """Insert sample students only when their USNs do not already exist."""
    inserted_count = 0
    try:
        for student in students:
            cleaned_student = validate_student(student)
            result = collection.update_one(
                {"usn": cleaned_student["usn"]},
                {"$setOnInsert": cleaned_student},
                upsert=True,
            )
            inserted_count += result.upserted_id is not None
    except PyMongoError:
        raise RuntimeError(
            "Could not add sample students. Check the database connection."
        ) from None
    return inserted_count
