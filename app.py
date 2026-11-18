"""Streamlit interface for the Student Management System."""

import streamlit as st

from database import (
    add_student,
    connect_to_mongodb,
    delete_student,
    get_all_students,
    get_student_by_usn,
    update_student,
)


st.set_page_config(page_title="Student Management System", page_icon="🎓", layout="wide")


@st.cache_resource
def get_students_collection():
    """Create one reusable MongoDB connection for this Streamlit session."""
    return connect_to_mongodb()


st.title("🎓 Student Management System")
st.caption("Manage student records stored in MongoDB Atlas.")

try:
    students_collection = get_students_collection()
except (ValueError, RuntimeError) as error:
    st.error(str(error))
    st.info("Set up the MongoDB Atlas connection as described in README.md, then restart the app.")
    st.stop()

page = st.sidebar.radio(
    "Choose a feature",
    ["Dashboard", "Add Student", "View All Students", "Search Student", "Update Student", "Delete Student"],
)


def show_student_table(students: list[dict]) -> None:
    """Display student records with native Streamlit components."""
    if not students:
        st.info("No student records found.")
        return

    column_widths = [1.3, 1.6, 1.5, 0.8, 0.8, 1.1]
    with st.container(border=True):
        header_columns = st.columns(column_widths)
        for column, heading in zip(
            header_columns,
            ("USN", "Name", "Branch", "Semester", "Marks", "Attendance"),
        ):
            column.markdown(f"**{heading}**")

        for student in students:
            row_columns = st.columns(column_widths)
            row_columns[0].write(student.get("usn", ""))
            row_columns[1].write(student.get("name", ""))
            row_columns[2].write(student.get("branch", ""))
            row_columns[3].write(student.get("semester", ""))
            row_columns[4].write(student.get("marks", ""))
            row_columns[5].write(
                f"{student.get('attendance', '')}%"
                if student.get("attendance") != ""
                else ""
            )


def student_form_values(
    student: dict | None = None, key_prefix: str = "student"
) -> dict:
    """Show the fields shared by the add and update forms."""
    student = student or {}
    usn_key = f"{key_prefix}_usn"
    name_key = f"{key_prefix}_name"
    branch_key = f"{key_prefix}_branch"
    semester_key = f"{key_prefix}_semester"
    marks_key = f"{key_prefix}_marks"
    attendance_key = f"{key_prefix}_attendance"

    left, right = st.columns(2)
    with left:
        usn = st.text_input(
            "USN",
            key=usn_key,
            **({"value": student.get("usn", "")} if usn_key not in st.session_state else {}),
        )
        name = st.text_input(
            "Name",
            key=name_key,
            **({"value": student.get("name", "")} if name_key not in st.session_state else {}),
        )
        branch = st.text_input(
            "Branch",
            key=branch_key,
            **(
                {"value": student.get("branch", "")}
                if branch_key not in st.session_state
                else {}
            ),
        )
    with right:
        semester = st.number_input(
            "Semester",
            min_value=1,
            step=1,
            key=semester_key,
            **(
                {"value": max(1, int(student.get("semester", 1)))}
                if semester_key not in st.session_state
                else {}
            ),
        )
        marks = st.number_input(
            "Marks (0–100)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key=marks_key,
            **(
                {"value": float(student.get("marks", 0))}
                if marks_key not in st.session_state
                else {}
            ),
        )
        attendance = st.number_input(
            "Attendance (0–100%)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key=attendance_key,
            **(
                {"value": float(student.get("attendance", 0))}
                if attendance_key not in st.session_state
                else {}
            ),
        )
    return {
        "usn": usn,
        "name": name,
        "branch": branch,
        "semester": semester,
        "marks": marks,
        "attendance": attendance,
    }


if page == "Dashboard":
    st.header("Dashboard")
    try:
        students = get_all_students(students_collection)
        total_students = len(students)
        average_marks = (
            sum(float(student.get("marks", 0)) for student in students) / total_students
            if total_students
            else 0
        )
        average_attendance = (
            sum(float(student.get("attendance", 0)) for student in students) / total_students
            if total_students
            else 0
        )
        metric_columns = st.columns(3)
        metric_columns[0].metric("Total Students", total_students)
        metric_columns[1].metric("Average Marks", f"{average_marks:.2f}")
        metric_columns[2].metric("Average Attendance", f"{average_attendance:.2f}%")
        st.subheader("Student records")
        show_student_table(students)
    except RuntimeError as error:
        st.error(str(error))

elif page == "Add Student":
    st.header("Add Student")
    with st.form("add_student_form"):
        student_values = student_form_values()
        submitted = st.form_submit_button("Add Student")
    if submitted:
        try:
            add_student(students_collection, student_values)
            st.success(f"Student {student_values['usn'].strip().upper()} was added.")
        except (ValueError, RuntimeError) as error:
            st.error(str(error))

elif page == "View All Students":
    st.header("All Students")
    try:
        show_student_table(get_all_students(students_collection))
    except RuntimeError as error:
        st.error(str(error))

elif page == "Search Student":
    st.header("Search Student")
    with st.form("search_student_form"):
        search_usn = st.text_input("Enter USN")
        search_submitted = st.form_submit_button("Search")
    if search_submitted:
        if not search_usn.strip():
            st.warning("Enter a USN to search.")
        else:
            try:
                student = get_student_by_usn(students_collection, search_usn)
                if student:
                    show_student_table([student])
                else:
                    st.info(f"No student was found with USN {search_usn.strip().upper()}.")
            except RuntimeError as error:
                st.error(str(error))

elif page == "Update Student":
    st.header("Update Student")
    if "_update_success_message" in st.session_state:
        st.success(st.session_state.pop("_update_success_message"))

    try:
        students = get_all_students(students_collection)
    except RuntimeError as error:
        st.error(str(error))
        students = []

    if students:
        student_usns = [student["usn"] for student in students]
        next_selection = st.session_state.pop("_update_next_selection", None)
        if next_selection in student_usns:
            st.session_state["update_selected_usn"] = next_selection

        selected_usn = st.selectbox(
            "Select a student by USN",
            student_usns,
            key="update_selected_usn",
        )
        try:
            selected_student = get_student_by_usn(students_collection, selected_usn)
        except RuntimeError as error:
            st.error(str(error))
            selected_student = None

        if selected_student is None:
            st.warning(f"No student was found with USN {selected_usn}. Refresh and select again.")
        else:
            if st.session_state.get("_update_loaded_usn") != selected_usn:
                for field in ("usn", "name", "branch", "semester", "marks", "attendance"):
                    st.session_state[f"update_{field}"] = selected_student[field]
                st.session_state["_update_loaded_usn"] = selected_usn

            with st.form(f"update_student_form_{selected_usn}"):
                student_values = student_form_values(
                    selected_student, key_prefix="update"
                )
                submitted = st.form_submit_button("Save Changes")
            if submitted:
                try:
                    update_student(students_collection, selected_usn, student_values)
                    st.session_state["_update_loaded_usn"] = student_values[
                        "usn"
                    ].strip().upper()
                    st.session_state["_update_success_message"] = (
                        f"Student {student_values['usn'].strip().upper()} was updated."
                    )
                    st.session_state["_update_next_selection"] = (
                        student_values["usn"].strip().upper()
                    )
                    st.rerun()
                except (ValueError, LookupError, RuntimeError) as error:
                    st.error(str(error))
    else:
        st.info("Add a student before using this feature.")

elif page == "Delete Student":
    st.header("Delete Student")
    deleted_usn = st.session_state.get("_delete_success_usn")
    if deleted_usn:
        st.success(f"Student deleted successfully! USN: {deleted_usn}")

    delete_widget_version = st.session_state.get("_delete_widget_version", 0)
    try:
        students = get_all_students(students_collection)
    except RuntimeError as error:
        st.error(str(error))
        students = []

    if students:
        student_usns = [student["usn"] for student in students]
        selected_usn = st.selectbox(
            "Select a student by USN",
            [""] + student_usns,
            format_func=lambda usn: usn or "Select a student",
            key=f"delete_selected_usn_{delete_widget_version}",
        )
        if st.session_state.get("_delete_loaded_usn") != selected_usn:
            st.session_state["_delete_loaded_usn"] = selected_usn
            st.session_state["_delete_selection_version"] = (
                st.session_state.get("_delete_selection_version", 0) + 1
            )
        delete_selection_version = st.session_state.get(
            "_delete_selection_version", 0
        )

        selected_student = None
        if selected_usn:
            try:
                selected_student = get_student_by_usn(
                    students_collection, selected_usn
                )
            except RuntimeError as error:
                st.error(str(error))

            if selected_student is None:
                st.error(f"No student was found with USN {selected_usn}.")
            else:
                st.write(f"**Selected student:** {selected_student['usn']} — {selected_student['name']}")
                confirmed = st.checkbox(
                    "I confirm that I want to permanently delete this student",
                    key=(
                        f"delete_confirm_{delete_widget_version}_"
                        f"{delete_selection_version}"
                    ),
                )
                if st.button(
                    "Delete Student",
                    type="primary",
                    disabled=not confirmed,
                    key=(
                        f"delete_button_{delete_widget_version}_"
                        f"{delete_selection_version}"
                    ),
                ):
                    try:
                        delete_student(students_collection, selected_usn)
                        st.session_state["_delete_success_usn"] = selected_usn
                        st.session_state["_delete_widget_version"] = (
                            delete_widget_version + 1
                        )
                        st.rerun()
                    except (LookupError, ValueError, RuntimeError) as error:
                        st.error(str(error))
        else:
            st.button(
                "Delete Student",
                type="primary",
                disabled=True,
                key=(
                    f"delete_button_{delete_widget_version}_"
                    f"{delete_selection_version}"
                ),
            )
    else:
        st.info("There are no student records to delete.")
