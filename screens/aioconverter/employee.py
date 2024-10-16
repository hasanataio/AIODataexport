import pandas as pd
def print(*args,**kwargs):
    return None


def run_employee(file_path):

    raw_df = pd.read_csv(file_path)

    main_df = raw_df[["Last Name", "First Name", "Email", "Phone Number", "Job Descriptions", "Wages"]]

    name_df = main_df[["First Name"]].copy()
    name_df["id"] = range(1, len(name_df) + 1)

    job_df = main_df["Job Descriptions"].drop_duplicates().reset_index(drop=True).to_frame()
    job_df["id"] = range(1, len(job_df) + 1)

    employee_and_job_df = main_df[["First Name", "Job Descriptions"]]

    employee_and_job_df["First Name"] = employee_and_job_df["First Name"].map(name_df.set_index("First Name")["id"])

    employee_and_job_df["Job Descriptions"] = employee_and_job_df["Job Descriptions"].map(job_df.set_index("Job Descriptions")["id"])

    employee_and_job_df.rename(columns={"First Name": "userId", "Job Descriptions": "rollId"}, inplace=True)

    user_roll_df = employee_and_job_df.copy()
    user_roll_df["first name"] = main_df["First Name"]
    user_roll_df["last name"] = main_df["Last Name"]
    user_roll_df["salary"] = main_df["Wages"]
    user_roll_df["status"] = True
    user_roll_df["payType"] = "hourly"
    user_roll_df["fixedPeriod"] = "Week"
    user_roll_df["id"] = range(1, len(user_roll_df) + 1)

    user_roll_df = user_roll_df[["id", "userId", "rollId", "first name", "last name", "status", "salary", "payType", "fixedPeriod"]]

    user_roll_df.to_excel("Employee_Campbell.xlsx", sheet_name="user_roles", index=False)

    role_df = job_df.copy()
    role_df["status"] = True
    role_df["resturantId"] = ""
    role_df["tag"] = ""
    role_df["key"] = ""
    role_df["id"] = range(1, len(role_df) + 1)

    role_df = role_df[["id", "Job Descriptions", "status", "resturantId", "tag", "key"]]

    with pd.ExcelWriter("Employee_Campbell.xlsx", engine="openpyxl", mode="a") as writer:
        role_df.to_excel(writer, sheet_name="role", index=False)

    return "Employee_Campbell.xlsx"