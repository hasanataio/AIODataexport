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


import pandas as pd
import chardet

def read_this(uploaded_file, ftype="csv", sheet_name=None):
    """
    Reads files and returns a pandas DataFrame.

    Parameters:
    1. uploaded_file: The file uploaded online.
    2. ftype: The file type (default is 'csv'). Supports 'csv' or 'xlsx'.
    3. sheet: The name of the sheet to load if an Excel file ('xlsx') is loaded (default is None).

    Returns:
    - DataFrame if the file is read successfully.
    - None if the file is not read successfully or the file type is unsupported.
    """
    if uploaded_file is not None:
        try:
            # Read the file contents
            file_contents = uploaded_file.getvalue()

            # Detect the encoding (useful for CSV files)
            result = chardet.detect(file_contents)
            encoding = result['encoding']

            if ftype == "csv":
                # Read the CSV file using the detected encoding
                df = pd.read_csv(uploaded_file, encoding=encoding)
            elif ftype == "xlsx":
                # Read the Excel file and optionally a specific sheet
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            else:
                print(f"Unsupported file type: {ftype}")
                return None

            return df
        except UnicodeDecodeError as e:
            print(f"Encoding error: {e}")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    else:
        print("No file uploaded")
        return None
