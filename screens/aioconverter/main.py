import openpyxl
from .data import main
import pandas as pd
import random
import os
def print(*args,**kwargs):
    return None


def get_item_names(file_path):
    try:
        excel_data = pd.read_excel(file_path, sheet_name="Item")
        item_names = excel_data["itemName"].tolist()
        print(f"Number of item names: {len(item_names)}")
        return item_names

    except Exception as e:
        print(f"Error occurred: {e}")
        return []


def get_sheet_names(filename):
    try:
        workbook = openpyxl.load_workbook(filename)
        sheet_names = workbook.sheetnames
        print("Sheet names: ", sheet_names)
        return sheet_names

    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return []


def search_item_in_sheets(input_item, sheet_names):
    print("Item name -- : ", input_item)
    for sheet in sheet_names:
        if input_item.lower() in sheet.lower():
            print(f"Full Match found: {sheet}")
            return True, sheet

    words = input_item.split()

    first_word = words[0]
    for sheet in sheet_names:
        if first_word.lower() in sheet.lower():
            print(f"First word Match found: {sheet}")
            return True, sheet

    last_word = words[-1]
    for sheet in sheet_names:
        if last_word.lower() in sheet.lower():
            print(f"last word Match found: {sheet}")
            return True, sheet
    try:
        second_word = words[1]
        for sheet in sheet_names:
            if second_word.lower() in sheet.lower():
                print(f"Exceptional 2nd word match found: {sheet}")
                return True, sheet
    except:
        pass

    print("No match found.")
    return False, None


def run_recipes_on_clover(items_file_path):
    all_items = get_item_names(items_file_path)

    database_recipe_1_sheet_path = f'{os.getcwd()}/screens/aioconverter/mexican_dishes_DB_final.xlsx'
    database_drinks_sheet_path = f'{os.getcwd()}/screens/aioconverter/mexican_drinks_DB.xlsx'

    recipe_sheets_1 = get_sheet_names(database_recipe_1_sheet_path)
    drinks_sheets = get_sheet_names(database_drinks_sheet_path)
    if os.path.exists("Mijos Recipes.xlsx"):
        os.remove("Mijos Recipes.xlsx")
    final_recipies = "Mijos Recipes.xlsx"

    for item in all_items:
        found = False
        match, sheet = search_item_in_sheets(item, recipe_sheets_1)

        if match:
            try:
                main(item, database_recipe_1_sheet_path, sheet, final_recipies)
            except Exception as e:
                print("########----------########----------########---------")
                print("########---------Some problem in processing data: ", e)
                print("########----------########----------########---------")

            found = True
            continue

        match, sheet3 = search_item_in_sheets(item, drinks_sheets)
        if match:
            try:
                main(item, database_drinks_sheet_path, sheet3, final_recipies)
            except Exception as e:
                print("########----------########----------########---------")
                print("########---------Some problem in processing data: ", e)
                print("########----------########----------########---------")

            found = True

        if not found:
            print(f"No match found for item: {item}")

    return final_recipies
