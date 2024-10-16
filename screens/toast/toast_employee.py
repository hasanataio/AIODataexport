import streamlit as st
import pandas as pd
from screens.toast.toast_utils.employees import (
    preprocess_employee,
    fill_user_roles,
)
from screens.utils import load_sheets, save_sheets, convert_list_to_string

# Constants for file paths and salary limits
EXCEL_FILE_PATH = "employee_desired_format/Employee Campbell 7.xlsx"
SAVE_FILE_PATH = "Toast Employee.xlsx"


def fill_employee(uploaded_employee: pd.DataFrame, employee: pd.DataFrame) -> pd.DataFrame:
    """
    Process the uploaded employee data and update the existing employee DataFrame.

    Args:
        uploaded_employee (pd.DataFrame): The uploaded employee data.
        employee (pd.DataFrame): The existing employee data to be updated.

    Returns:
        pd.DataFrame: The updated employee DataFrame.
    """
    columns_to_drop = ["Location", "GUID", "Job GUIDs"]
    existing_columns_to_drop = [
        col for col in columns_to_drop if col in uploaded_employee.columns]
    if existing_columns_to_drop:
        uploaded_employee.drop(columns=existing_columns_to_drop, inplace=True)

    uploaded_employee.rename(columns={
        'First Name': "firstName",
        'Last Name': "lastName",
        'Email': "email",
        "Phone Number": "phoneNumber"
    }, inplace=True)

    employee = preprocess_employee(
        uploaded_employee=uploaded_employee, employee=employee)
    return employee


def map_roles(employee: pd.DataFrame, roles_available: list) -> pd.DataFrame:
    """
    Map user roles based on the employee job descriptions.

    Args:
        employee (pd.DataFrame): The employee data containing job descriptions.
        roles_available (list): The list of available roles to map to.

    Returns:
        pd.DataFrame: The updated employee DataFrame with mapped roles.
    """

    unique_job_descriptions = set()
    for job_desc_list in employee['jobDescription']:
        if isinstance(job_desc_list, list):
            unique_job_descriptions.update(
                [desc.lower() for desc in job_desc_list])
        else:
            unique_job_descriptions.add(job_desc_list.lower())

    assign_roles_to = list(unique_job_descriptions)

    # remove "''", 'undefined', None from assign_roles to if available
    assign_roles_to = [
        role for role in assign_roles_to if role not in ["", "''", 'undefined', None]]

    new_mapping = {}
    col1, col2 = st.columns(2)

    # Load existing mapping if available
    existing_mapping = st.session_state.get('mapping', {})

    for idx, role in enumerate(assign_roles_to):

        # Determine the default value, ensuring it is within roles_available
        default_value = existing_mapping.get(
            # if not available then make him server
            role.lower(), roles_available[7].lower())

        default_index = roles_available.index(
            default_value) if default_value in roles_available else 0

        if idx % 2 == 0:
            with col1:
                new_role = st.selectbox(
                    f"Select new role for: {role}", options=roles_available, index=default_index, key=f"{role}_new1")
        else:
            with col2:
                new_role = st.selectbox(
                    f"Select new role for: {role}", options=roles_available, index=default_index, key=f"{role}_new2")

        new_mapping[role] = new_role

    if st.button("Confirm Mapping"):
        st.session_state['mapping'] = new_mapping
        st.success("Mapping confirmed and applied!")

        # Update job descriptions in employee data
        for i, job_desc_list in enumerate(employee['jobDescription']):
            if isinstance(job_desc_list, list):

                employee.at[i, 'jobDescription'] = [st.session_state['mapping'].get(
                    desc.lower(), desc) for desc in job_desc_list]

    return employee


def process_data(employee, user_roles, role):
    """
    Process the uploaded employee data, map roles, and update the data in the session state.
    """

    if 'uploaded_employee_file' not in st.session_state:
        st.session_state['uploaded_employee_file'] = None

    uploaded_employee_file = st.file_uploader(
        "Upload Employee CSV", type="csv")

    if uploaded_employee_file is not None:
        st.session_state['uploaded_employee_file'] = uploaded_employee_file

    if st.session_state['uploaded_employee_file'] is not None:
        uploaded_employee = pd.read_csv(
            st.session_state['uploaded_employee_file'])
        st.write("Employee Data")
        st.write(uploaded_employee)

        employee = fill_employee(
            uploaded_employee=uploaded_employee, employee=employee)

        roles_available = list(role["name"].unique())

        st.markdown("## Mapping User Roles")

        # Mapping dictionary for roles
        st.session_state['mapping'] = {
            "admin": "Shift Or Assistant Manager",
            "busser": "Busser",
            "cook": "Cook",
            "dishwasher": "Dishwasher",
            "host": "Server",
            "manager on duty": "Manager",
            "general manager": "General Manager",
            "shift manager / assistant manager": "Shift Or Assistant Manager",
            "manager": "Manager",
            "janitorial": "Janatorial",
            "owner": "Owner",
            "retail manager": "Manager",
            "server": "Server",
            "shift supervisor": "Shift Or Assistant Manager",
            "bartender": "Bartender",
            "barback": "Barback",
            "line cook": "Line Cook"
        }
        employee = map_roles(
            employee=employee, roles_available=roles_available)

        user_roles, employee = fill_user_roles(
            employee=employee,
            role=role,
            user_roles=user_roles
        )

        # drop ids that are duplicated and drop the one that has its jobDescription == "undefined"
        # ***** Find duplicates based on 'id'
        duplicates = employee[employee.duplicated('id', keep=False)]
        # Filter out the duplicates where jobDescription is 'undefined'
        to_drop_emp = duplicates[duplicates['jobDescription'] == 'undefined']
        # Drop these rows from the original DataFrame
        employee = employee.drop(to_drop_emp.index)

        # # change job description from a list ["a", "b"] to a single string "a;b" employees
        # # Apply the function to the jobDescription column
        # employee['jobDescription'] = employee['jobDescription'].apply(
        #     convert_list_to_string)
        # employee['wages'] = employee['wages'].apply(
        #     convert_list_to_string)
        # employee['roleId'] = employee['roleId'].apply(
        #     convert_list_to_string)

        # If jobDescription, wages, roleId columns exists in employee, drop the columns
        if 'jobDescription' in employee.columns:
            employee = employee.drop(columns=['jobDescription'])
        if 'wages' in employee.columns:
            employee = employee.drop(columns=['wages'])
        if 'roleId' in employee.columns:
            employee = employee.drop(columns=['roleId'])

        # make a column in employee called reviewCounts with review counts in each row
        review_counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        # make a list of len(employee) of review counts
        review_counts_list = []
        for i in range(len(employee)):
            review_counts_list.append(review_counts)
        employee['reviewCounts'] = review_counts_list

        # ***** User Roles drop where salary is None
        user_roles = user_roles[user_roles['salary'].notna()]
        user_roles = user_roles[user_roles['roleId'].notna()]
        # user_roles to str just the whole number
        user_roles['roleId'] = user_roles['roleId'].astype(str).str.split(
            '.').str[0]

        # sort employees and user roles based on id
        employee = employee.sort_values(by=['id'])
        user_roles = user_roles.sort_values(by=['userId'])

        return employee, user_roles, role


def toast_emp():
    """
    Main function to render the Streamlit app page.
    """

    # Load initial data if not already in session state
    st.session_state['sheets_dict'] = load_sheets(EXCEL_FILE_PATH)

    sheets_dict = st.session_state['sheets_dict']
    break_df = sheets_dict['break']
    employee_documents = sheets_dict['employee_documents']
    # emptying because the config file is already filled with some dummy data
    user_roles = sheets_dict['user_roles'][0:0]
    employee = sheets_dict['employee'][0:0]
    payroll = sheets_dict['payroll']
    role = sheets_dict['role']

    st.title("Toast Employee Transformation")
    st.write("Upload the employee CSV to start mapping roles.")

    # employee, user_roles, role
    data = process_data(employee, user_roles, role)

    if data:
        dataframes_to_save = {
            'break': break_df,
            'employee_documents': employee_documents,
            'user_roles': data[1],
            'employee': data[0],
            'payroll': payroll,
            'role': data[2]
        }
        save_sheets(dataframes_to_save, SAVE_FILE_PATH)

        st.write("User Roles")
        st.write(data[1])
        st.write("Employee")
        st.write(data[0])

        with open(SAVE_FILE_PATH, 'rb') as f:
            data = f.read()

        st.download_button(
            label="Download the updated Excel file",
            data=data,
            file_name="Updated_Employee_File.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Config File Updated")


# Run the Streamlit app
if __name__ == "__main__":
    toast_emp()
