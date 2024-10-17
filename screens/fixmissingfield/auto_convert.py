
from .MissingFieldsFix import fix_missing_fields


def auto_fix_fields(file):
    dataframes=fix_missing_fields(file)
    return dataframes