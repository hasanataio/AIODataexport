import os
import pandas as pd

def get_doordash(file_path):

    # Try reading the Excel file and checking the sheet names
    try:
        xl = pd.ExcelFile(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {e}")

    # Check for required sheets
    required_sheets = ['items', 'modifiers']
    if not all(sheet in xl.sheet_names for sheet in required_sheets):
        raise ValueError(f"Excel file must contain sheets: {', '.join(required_sheets)}")

    # Read the sheets
    sheet1 = xl.parse('items')
    sheet2 = xl.parse('modifiers')

    # Check for required columns in 'items' sheet
    required_columns_items = ['Item Name']
    if not all(col in sheet1.columns for col in required_columns_items):
        raise ValueError(f"Sheet 'items' must contain columns: {', '.join(required_columns_items)}")

    # Check for required columns in 'modifiers' sheet
    required_columns_modifiers = ['item_name', 'modifier_name', 'modifier_type', 'option_name']
    if not all(col in sheet2.columns for col in required_columns_modifiers):
        raise ValueError(f"Sheet 'modifiers' must contain columns: {', '.join(required_columns_modifiers)}")

    # Perform the merge operation
    doordash = pd.merge(sheet1, sheet2, left_on='Item Name', right_on='item_name', how='left')
    doordash.drop(columns=['item_name'], inplace=True)

    return doordash

def remove_recommended(dd):

    dd = dd[~dd['modifier_name'].str.contains("Recommended", na=False)]
    return dd

def get_square(file_path):


    # Try reading the Excel file and check for its sheet names
    try:
        xl = pd.ExcelFile(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {e}")

    # Required sheet names
    required_sheets = ['Item', 'Modifier', 'Modifier Option', 'Item Modifiers', 'Modifier ModifierOptions']
    if not all(sheet in xl.sheet_names for sheet in required_sheets):
        raise ValueError(f"Excel file must contain sheets: {', '.join(required_sheets)}")

    # Read the sheets
    sheet_item = xl.parse('Item')
    sheet_modifier = xl.parse('Modifier')
    sheet_modifier_option = xl.parse('Modifier Option')
    sheet_item_modifiers = xl.parse('Item Modifiers')
    sheet_modifier_modifieroptions = xl.parse('Modifier ModifierOptions')

    # Check for required columns in 'Item' sheet
    required_columns_item = ['id', 'itemName']
    if not all(col in sheet_item.columns for col in required_columns_item):
        raise ValueError(f"Sheet 'Item' must contain columns: {', '.join(required_columns_item)}")

    # Check for required columns in 'Modifier' sheet
    required_columns_modifier = ['id', 'modifierName', 'isOptional']
    if not all(col in sheet_modifier.columns for col in required_columns_modifier):
        raise ValueError(f"Sheet 'Modifier' must contain columns: {', '.join(required_columns_modifier)}")

    # Check for required columns in 'Modifier Option' sheet
    required_columns_modifier_option = ['id', 'optionName', 'price']
    if not all(col in sheet_modifier_option.columns for col in required_columns_modifier_option):
        raise ValueError(f"Sheet 'Modifier Option' must contain columns: {', '.join(required_columns_modifier_option)}")

    # Check for required columns in 'Item Modifiers' sheet
    required_columns_item_modifiers = ['itemId', 'modifierId']
    if not all(col in sheet_item_modifiers.columns for col in required_columns_item_modifiers):
        raise ValueError(f"Sheet 'Item Modifiers' must contain columns: {', '.join(required_columns_item_modifiers)}")

    # Check for required columns in 'Modifier ModifierOptions' sheet
    required_columns_modifier_modifieroptions = ['modifierId', 'modifierOptionId']
    if not all(col in sheet_modifier_modifieroptions.columns for col in required_columns_modifier_modifieroptions):
        raise ValueError(f"Sheet 'Modifier ModifierOptions' must contain columns: {', '.join(required_columns_modifier_modifieroptions)}")

    # Return the entire Excel file as a dictionary of DataFrames (sheets)
    square = {sheet: xl.parse(sheet) for sheet in xl.sheet_names}
    return square

def add_modifiers(doordash, modifiers):
    # process modifiers (id, modifierName, isOptional)
    # process and format provided data
    filtered = doordash[['modifier_name', 'modifier_type']].dropna().drop_duplicates().reset_index(drop=True)
    filtered['is_required'] = filtered['modifier_type'].apply(lambda x: "FALSE" if 'Required' in x else "TRUE")

    # assign relevant values
    modifiers['id'] = filtered.index + 1
    modifiers['modifierName'] = filtered['modifier_name']
    modifiers['isOptional'] = filtered['is_required']

    return modifiers

def add_options(doordash, modifiers_options):

    # process options (id, modifierName, isOptional)

    # process and format provided data
    filtered = doordash[['option_name', 'option_price']].dropna().drop_duplicates().reset_index(drop=True)
    filtered['option_price'] = filtered['option_price'].apply(lambda price: float(price.replace('+$', '')) if isinstance(price, str) else float(price))

    # assign relevant values
    modifiers_options['id'] = filtered.index + 1
    modifiers_options['optionName'] = filtered['option_name']
    modifiers_options['price'] = filtered['option_price']

    return modifiers_options

def map_all(doordash, modifiers_options, modifiers, items):

    # drop nans
    filtered = doordash[['Item Name', 'modifier_name', 'option_name']].dropna()

    # attach option ids
    filtered = pd.merge(filtered, modifiers_options[['id', 'optionName']], left_on='option_name', right_on='optionName', how='left')
    filtered.drop('optionName', axis=1, inplace=True)
    filtered.rename(columns={'id': 'option_id'}, inplace=True)

    # attach modifier ids
    filtered = pd.merge(filtered, modifiers[['id', 'modifierName']], left_on='modifier_name', right_on='modifierName', how='left')
    filtered.drop('modifierName', axis=1, inplace=True)
    filtered.rename(columns={'id': 'modifier_id'}, inplace=True)

    # attach item ids
    filtered = pd.merge(filtered, items[['id', 'itemName']], left_on='Item Name', right_on='itemName', how='left')
    filtered.drop('itemName', axis=1, inplace=True)
    filtered.rename(columns={'id': 'item_id'}, inplace=True)

    return filtered

def item_modifier_mapper(clean, item_modifier_map):

    im_map = clean[['item_id', 'modifier_id']].drop_duplicates().sort_values(by="item_id", ascending=True).reset_index(drop=True)
    item_modifier_map['itemId'] = im_map['item_id']
    item_modifier_map['modifierId'] = im_map['modifier_id']

def modifier_option_mapper(clean, modifier_option_map):

    mo_map = clean[['modifier_id', 'option_id']].drop_duplicates().sort_values(by="modifier_id", ascending=True).reset_index(drop=True)
    modifier_option_map['modifierId'] = mo_map['modifier_id']
    modifier_option_map['modifierOptionId'] = mo_map['option_id']

def dump_sheets_to_excel(excel_data, output_file):
    
    # Create a new ExcelWriter object to write the sheets into a new file
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for sheet_name, data in excel_data.items():
            # Write each sheet to the new Excel file with the same name
            data.to_excel(writer, sheet_name=sheet_name, index=False)

def fill_with_doordash(dd_file, s_file, output_file = "square_raw.xlsx"):

    # get data
    doordash = get_doordash(dd_file)
    square = get_square(s_file)

    # process doordash (removing recommended)
    doordash = remove_recommended(doordash)

    # assign tables and sheets
    items = square['Item']
    modifiers = square['Modifier']
    modifiers_options = square['Modifier Option']
    item_modifier_map = square['Item Modifiers']
    modifier_option_map = square['Modifier ModifierOptions']


    # add information (modifiers, options)
    square['Modifier'] = add_modifiers(doordash, modifiers)
    square['Modifier Option'] = add_options(doordash, modifiers_options)

    # map items, modifiers, options
    filtered = map_all(doordash, modifiers_options, modifiers, items)

    # remove items that are available on doordash but not on platform export file
    clean = filtered[filtered['item_id'].notna()]
    clean = clean[['Item Name', 'item_id', 'modifier_name', 'modifier_id', 'option_name', 'option_id']]
    clean['item_id'] = clean['item_id'].astype(int)

    # add mappings (items, modifiers, options)
    item_modifier_mapper(clean, item_modifier_map)
    modifier_option_mapper(clean, modifier_option_map)

    # dump data
    dump_sheets_to_excel(square, output_file)
    return output_file