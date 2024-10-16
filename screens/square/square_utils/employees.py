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

    # Split names by space into first name and last name. If no last name, set it to None
    uploaded_employee[['firstName', 'lastName']
                      ] = uploaded_employee['Name'].str.split(n=1, expand=True)

    uploaded_employee.rename(columns={
        'Job/Role': 'jobDescription',
        'Email': "email",
        "Phone": "phoneNumber",
        "Wage": "wages"
    }, inplace=True)

    employee = preprocess_employee(
        uploaded_employee=uploaded_employee, employee=employee)
    return employee


# Function to replace job descriptions
def predict_roles(desc: List[str], roles: pd.DataFrame) -> Tuple[List[str], bool]:
    """
        Recieves Description of the Job role, checks the roles available and assigns the ones that match the description.
    """
    matching_roles = []
    for job_name in desc:
        found = False
        if type(desc) is str:
            matching_roles.append(None)
            break
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
        'wages': list(uploaded_employee["wages"])
    }

    uploaded_employee = pd.DataFrame(emp_data)

    # Add empty rows to employee DataFrame
    num_empty_rows = len(uploaded_employee)
    empty_rows = pd.DataFrame(
        {col: [None]*num_empty_rows for col in employee.columns})

    employee = pd.concat([employee, empty_rows], ignore_index=True)

    employee['jobDescription'] = None
    employee['wages'] = None

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

    # make job descriptions lower, handle none
    employee['jobDescription'] = employee['jobDescription'].apply(
        lambda x: x.lower() if x is not None else None)

    print("jobs: ", employee['jobDescription'])
    # Split the job descriptions and wages in the employee dataframe, handling cases without '/'
    employee['jobDescription'] = employee['jobDescription'].apply(
        lambda x: x.split('/') if '/' in x else [x])
    employee['wages'] = employee['wages'].apply(lambda x: str(x).split(
        '/')[0] if isinstance(x, str) and '/' in x else str(x))

    # if wage is nan then make it None
    employee['wages'] = employee['wages'].apply(
        lambda x: None if x in ['nan', ''] else x)

    # fill null jobDescription with Undefined
    employee["jobDescription"].fillna("undefined", inplace=True)

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
                'payType': "",
                'fixedPeriod': "",
                'status': True
            })

    # Create a DataFrame from the new_user_roles list
    new_user_roles_df = pd.DataFrame(new_user_roles)

    # Update the user_roles DataFrame
    user_roles = pd.concat(
        [user_roles, new_user_roles_df], ignore_index=True)

    # Fill the payType column using apply
    user_roles['payType'] = "hourly"
    return user_roles, employee
