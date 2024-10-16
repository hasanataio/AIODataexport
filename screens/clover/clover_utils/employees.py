import pandas as pd
from typing import Tuple, List


def replace_job_descriptions(job_desc, mapping):
    if job_desc is None:
        return None
    if isinstance(job_desc, str) and job_desc.lower() == "undefined":
        return job_desc
    elif isinstance(job_desc, list):
        return [mapping.get(job.lower(), job.lower()) for job in job_desc]
    return job_desc


def fill_employee(uploaded_employee: pd.DataFrame, employee: pd.DataFrame) -> pd.DataFrame:
    """
    Process the uploaded employee data and update the existing employee DataFrame.

    Args:
        uploaded_employee (pd.DataFrame): The uploaded employee data.
        employee (pd.DataFrame): The existing employee data to be updated.

    Returns:
        pd.DataFrame: The updated employee DataFrame.
    """

    # remove any extra spaces from column names
    uploaded_employee.columns = uploaded_employee.columns.str.strip()

    uploaded_employee.rename(columns={
        'First Name': 'firstName',
        'Last Name': 'lastName',
        'Email': "email",
        "Phone": "phoneNumber",
        "Wage Rate": "wages",
        "Role Name": "jobDescription",
        "Wage Type": "payType"
    }, inplace=True)

    employee = preprocess_employee(
        uploaded_employee=uploaded_employee, employee=employee)

    return employee


# Function to replace job descriptions
def predict_roles(desc: str, roles: pd.DataFrame) -> Tuple[List[str], bool]:
    """
        Recieves Description of the Job role, checks the roles available and assigns the ones that match the description.
    """
    matching_roles = []

    if type(desc) is str:
        for role_idx, role_row in roles.iterrows():
            if role_row['name'].lower() == desc.lower():
                matching_roles.append(role_row['id'])
                break
        return matching_roles

    for job_name in desc:
        found = False
        for role_idx, role_row in roles.iterrows():

            if role_row['name'] and job_name and role_row['name'].lower() == job_name.lower():
                found = True
                matching_roles.append(role_row['id'])

        if not found:
            matching_roles.append(None)
    return matching_roles


def preprocess_employee(uploaded_employee, employee):
    # Merge emp into employee, filling missing values with empty strings
    employee = employee.merge(uploaded_employee[['lastName', 'firstName', 'email', 'phoneNumber']], how='left',
                              left_index=True, right_index=True, suffixes=('', '_emp'))

    # Sample employee DataFrame
    employee_data = {
        'id': list(employee["id"]),
        'posPin': list(employee["posPin"]),
        'employeeDisplayId': list(employee["employeeDisplayId"]),
        'createdAt': list(employee["createdAt"]),
        'updatedAt': list(employee["updatedAt"]),
        'firstName': list(employee["firstName"]),
        'lastName': list(employee["lastName"]),
        'email': list(employee["email"]),
        'phoneNumber': list(employee["phoneNumber"]),
        'restaurantId': list(employee["restaurantId"]),
        'reviewCounts': list(employee["reviewCounts"]),
        'imgUrl': list(employee["imgUrl"])
    }

    employee = pd.DataFrame(employee_data)

    # Sample emp DataFrame
    emp_data = {
        'lastName': list(uploaded_employee["lastName"]),
        'firstName': list(uploaded_employee["firstName"]),
        'email': list(uploaded_employee["email"]),
        'phoneNumber': list(uploaded_employee["phoneNumber"]),
        'jobDescription': list(uploaded_employee["jobDescription"]),
        'wages': list(uploaded_employee["wages"]),
        'payType': list(uploaded_employee["payType"])
    }

    uploaded_employee = pd.DataFrame(emp_data)

    # Add empty rows to employee DataFrame
    num_empty_rows = len(uploaded_employee)
    empty_rows = pd.DataFrame(
        {col: [None]*num_empty_rows for col in employee.columns})

    employee = pd.concat([employee, empty_rows], ignore_index=True)

    employee['jobDescription'] = None
    employee['wages'] = None
    employee['payType'] = None

    # Fill the empty rows with data from emp
    for i in range(num_empty_rows):
        cols = employee.columns

        last_name = cols.get_loc('lastName')
        first_name = cols.get_loc('firstName')
        email = cols.get_loc('email')
        phone_number = cols.get_loc('phoneNumber')
        restaurant_id = cols.get_loc('restaurantId')
        emp_id = cols.get_loc('id')
        job_desc = cols.get_loc('jobDescription')
        wage = cols.get_loc('wages')
        pay_type = cols.get_loc('payType')

        employee.iloc[-(i+1),
                      last_name] = uploaded_employee.iloc[i]['lastName']
        employee.iloc[-(i+1),
                      first_name] = uploaded_employee.iloc[i]['firstName']
        employee.iloc[-(i+1), email] = uploaded_employee.iloc[i]['email']
        employee.iloc[-(i+1),
                      phone_number] = uploaded_employee.iloc[i]['phoneNumber']
        employee.iloc[-(i+1), restaurant_id] = 1
        employee.iloc[-(i+1), emp_id] = i+1
        employee.iloc[-(i+1),
                      job_desc] = uploaded_employee.iloc[i]['jobDescription']
        employee.iloc[-(i+1),
                      wage] = uploaded_employee.iloc[i]['wages']
        employee.iloc[-(i+1),
                      pay_type] = uploaded_employee.iloc[i]['payType']

    # make job descriptions lower, handle none
    employee['jobDescription'] = employee['jobDescription'].apply(
        lambda x: x.lower() if pd.notna(x) else None
    )

    # Make wages None if they are NaN or empty string
    employee['wages'] = employee['wages'].apply(
        lambda x: None if pd.isna(x) or x == '' else x
    )

    # Create a new column in employee dataframe to store role id
    employee['roleId'] = None

    return employee


def fill_user_roles(employee, role, user_roles):
    # Iterate over each row in employee dataframe
    for idx, row in employee.iterrows():
        job_desc = row['jobDescription']
        if job_desc is None:
            matching_roles = []
        else:
            matching_roles = predict_roles(desc=job_desc, roles=role)
        employee.at[idx, 'roleId'] = matching_roles

    # Assuming 'employee' is a DataFrame containing the employee data
    new_user_roles = []

    for idx, row in employee.iterrows():
        user_id = row['id']
        wages = row['wages']
        roles = row['roleId']
        pay_type = row['payType']

        if not isinstance(wages, list):
            wages = [wages]  # Convert to list if it's not already one

        if not isinstance(roles, list):
            roles = [roles]  # Convert to list if it's not already one

        for wage, job_role in zip(wages, roles):
            if wage not in [None, '', 'nan']:
                salary = wage
            else:
                salary = None

            new_user_roles.append({
                'userId': user_id,
                'roleId': job_role,
                'salary': salary,
                'payType': pay_type,
                'fixedPeriod': "",
                'status': True
            })

    # Create a DataFrame from the new_user_roles list
    new_user_roles_df = pd.DataFrame(new_user_roles)

    # Update the user_roles DataFrame
    user_roles = pd.concat(
        [user_roles, new_user_roles_df], ignore_index=True)

    return user_roles, employee
