"""Add at least ten demonstration students without duplicating existing USNs."""

from database import connect_to_mongodb, insert_sample_students


SAMPLE_STUDENTS = [
    {"usn": "1MS23CS001", "name": "Aarav Sharma", "branch": "Computer Science", "semester": 3, "marks": 86, "attendance": 92},
    {"usn": "1MS23CS002", "name": "Diya Patel", "branch": "Computer Science", "semester": 3, "marks": 91, "attendance": 95},
    {"usn": "1MS23CS003", "name": "Kabir Rao", "branch": "Computer Science", "semester": 3, "marks": 78, "attendance": 88},
    {"usn": "1MS23EC004", "name": "Ananya Iyer", "branch": "Electronics", "semester": 3, "marks": 84, "attendance": 90},
    {"usn": "1MS23EC005", "name": "Vivaan Nair", "branch": "Electronics", "semester": 3, "marks": 73, "attendance": 82},
    {"usn": "1MS23ME006", "name": "Ishita Das", "branch": "Mechanical", "semester": 3, "marks": 89, "attendance": 96},
    {"usn": "1MS23ME007", "name": "Arjun Kumar", "branch": "Mechanical", "semester": 3, "marks": 68, "attendance": 79},
    {"usn": "1MS23CV008", "name": "Meera Reddy", "branch": "Civil", "semester": 3, "marks": 94, "attendance": 98},
    {"usn": "1MS23CV009", "name": "Reyansh Singh", "branch": "Civil", "semester": 3, "marks": 81, "attendance": 87},
    {"usn": "1MS23IS010", "name": "Saanvi Gupta", "branch": "Information Science", "semester": 3, "marks": 88, "attendance": 93},
]


def main() -> None:
    """Connect and seed records, then close the connection cleanly."""
    collection = connect_to_mongodb()
    try:
        inserted_count = insert_sample_students(collection, SAMPLE_STUDENTS)
        print(
            f"Sample data ready: {inserted_count} new students inserted; "
            f"{len(SAMPLE_STUDENTS) - inserted_count} existing USNs were skipped."
        )
    finally:
        collection.database.client.close()


if __name__ == "__main__":
    main()
