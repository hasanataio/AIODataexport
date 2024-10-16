import chardet
import pandas as pd

# *** Function to convert list to semicolon-separated string, handling None and integer values


def convert_list_to_string(job_desc):
    if job_desc is None:
        return ""
    if type(job_desc) is str:
        # turn into a list [job_desc]
        return job_desc
    # Convert all elements to strings and filter out None values
    job_desc = [str(item) for item in job_desc if item is not None]
    return "; ".join(job_desc)


def load_sheets(file_path):
    return pd.read_excel(file_path, sheet_name=None)


def save_sheets(dataframes, file_path):
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def read_this(uploaded_file):
    if uploaded_file is not None:
        try:
            # Read the file contents
            file_contents = uploaded_file.getvalue()

            # Detect the encoding
            result = chardet.detect(file_contents)
            encoding = result['encoding']

            # Read the CSV file using the detected encoding
            df = pd.read_csv(uploaded_file, encoding=encoding)
            return df
        except UnicodeDecodeError as e:
            print(e)
    else:
        return None
