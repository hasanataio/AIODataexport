import os
import pandas as pd
import openpyxl

def print(*args,**kwargs):
    return None

def read_excel_to_dataframe(item_name, filename, sheet_name):
    try:
        start_row = 11
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook[sheet_name]

        data = []
        for row in sheet.iter_rows(min_row=start_row, values_only=True):
            data.append(row)

        item_column = [item_name] + [''] * (len(data) - 1)

        df = pd.DataFrame(data, columns=[
            'ingredient_name',
            'ingredient_category',
            'ingredient_usage',
            'ingredient_quantity',
            'ingredient_unit',
            'ingredient_inventory_name',
            'metadata_name',
            'metadata_value',
            'label'
        ])

        df.insert(0, 'item_name', item_column)

        return df

    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None


def main(item_name, db_filename, db_sheet_name, output_filename):

    file_exists = os.path.exists(output_filename)

    df = read_excel_to_dataframe(item_name, db_filename, db_sheet_name)

    if df is None:
        print("Error reading Excel file.")
        return

    selected_df = df[['item_name',
                      'ingredient_quantity',
                      'ingredient_unit',
                      'ingredient_usage',
                      'ingredient_name',
                      'ingredient_category']]

    if file_exists:
        existing_df = pd.read_excel(output_filename)
        updated_df = pd.concat([existing_df, selected_df], ignore_index=True)
    else:
        updated_df = selected_df
    # return updated_df
    updated_df.to_excel(output_filename, sheet_name="recipes", index=False)

    # print(f"Data appended to '{output_filename}' with sheet name 'recipes'.")

