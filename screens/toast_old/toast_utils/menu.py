# Handling Menu

import pandas as pd


def load_data(file_path):
    # Load all sheets into a dictionary of DataFrame objects
    sheets_dict = pd.read_excel(file_path, sheet_name=None)
    return sheets_dict


def fill_category_sheet(sheets_dict, parent_categories, sub_categories):
    # *****************************************************
    # **********  Filling Category Sheet ******************
    # *****************************************************

    # Drop Archived 'Yes'
    if "Archived" in parent_categories.columns:
        parent_categories = parent_categories[parent_categories["Archived"].apply(lambda x: x.lower() if isinstance(x, str) else x) != "yes"]

    if "Archived" in sub_categories.columns:
        sub_categories = sub_categories[sub_categories["Archived"].apply(lambda x: x.lower() if isinstance(x, str) else x) != "yes"]

    # Drop columns
    if not parent_categories.empty:
        parent_categories = parent_categories[["Item ID", "Name"]].copy()
        parent_categories["Parent Id"] = None
    else:
        parent_categories = pd.DataFrame(columns=["Item ID", "Name", "Parent Id"])  # Empty dataframe with needed columns

    sub_categories = sub_categories[["Item ID", "Name", "Parent Id"]].copy()

    # If the parent category sheet is empty, we work only with subcategories
    if parent_categories.empty:
        sub_categories["Parent Id"] = None  # No parent, make parentId null for all subcategories
        categories = sub_categories.copy()
    else:
        # If parent categories are present, combine both
        categories = pd.concat([parent_categories, sub_categories], ignore_index=True)

    # Remove any duplicate category names based on 'Name' and 'Parent Id'
    categories = categories.drop_duplicates(subset=["Name", "Parent Id"], keep='first', ignore_index=True)

    # Generate sequential unique IDs for categories (no overlap between parent and subcategories)
    categories['Item ID'] = range(1, len(categories) + 1)

    # Map new IDs back to subcategories' Parent Ids
    id_mapping = {row['Name']: row['Item ID'] for _, row in categories.iterrows()}
    categories["Parent Id"] = categories["Parent Id"].map(id_mapping)

    # Fill the sheets_dict["Category"]
    category_sheet = sheets_dict["Category"][0:0]  # Get an empty template of Category sheet

    category_sheet['id'] = categories["Item ID"]
    category_sheet['categoryName'] = categories['Name']
    category_sheet['posDisplayName'] = categories['Name']
    category_sheet['kdsDisplayName'] = categories['Name']
    category_sheet['parentCategoryId'] = categories['Parent Id']
    category_sheet['menuIds'] = 1  # Default menu ID for all categories

    # Handle cases where parentCategoryId is missing (None or NaN)
    category_sheet.loc[category_sheet['parentCategoryId'].isnull(), 'parentCategoryId'] = None

    # Ensure Misc category is added, if not present
    misc_row = pd.DataFrame({
        "id": [category_sheet['id'].max() + 1],
        "categoryName": ["Misc"],
        "posDisplayName": ["Misc"],
        "kdsDisplayName": ["Misc"],
        "parentCategoryId": [None],
        "menuIds": [1]
    })

    # Append "Misc" category at the end
    category_sheet = pd.concat([category_sheet, misc_row], ignore_index=True)

    # Return the updated sheets_dict with the filled Category sheet
    sheets_dict["Category"] = category_sheet

    return sheets_dict



def fill_item_sheet(sheets_dict, item_export):
    # *****************************************************
    # ************ Filling Item Sheet *********************
    # *****************************************************

    if "Archived" in item_export.columns:
        item_export = item_export[item_export["Archived"].apply(lambda x: x.lower() if isinstance(x, str) else x) != "yes"]

    # Drop duplicate items with the same name (case-insensitive)
    item_export = item_export.drop_duplicates(
        subset=["Name", "Base Price"], keep='first', ignore_index=True)

    # Create the items DataFrame
    items = sheets_dict["Item"][0:0]
    items['id'] = pd.Series(range(1, len(item_export)))
    items['itemName'] = item_export['Name']
    items['itemPrice'] = item_export["Base Price"]

    # Assign the filled DataFrame to 'sheets_dict["Item"]'
    sheets_dict["Item"] = items
    return sheets_dict

def fill_modifier_sheet(sheets_dict, modifier_export):
    # *****************************************************
    # ********** Filling Modifier Sheet ******************
    # *****************************************************
    if "Archived" in modifier_export.columns:
        modifier_export = modifier_export[modifier_export["Archived"].apply(lambda x: x.lower() if isinstance(x, str) else x) != "yes"]

    # Drop duplicate modifiers with the same name (case-insensitive)
    modifier_export = modifier_export.drop_duplicates(
        subset=["Name"], keep='first', ignore_index=True)

    # Create the modifier DataFrame
    modifier = sheets_dict["Modifier"][0:0]
    modifier['id'] = pd.Series(range(1, len(modifier_export) + 1))
    modifier['modifierName'] = modifier_export['Name']
    modifier['price'] = None

    # Assign the filled DataFrame to 'sheets_dict["Modifier"]'
    sheets_dict["Modifier"] = modifier
    return sheets_dict

def fill_modifier_option_sheet(sheets_dict, modifier_option_export):
    # *****************************************************
    # ********* Filling Modifier Options *****************
    # *****************************************************
    if "Archived" in modifier_option_export.columns:
        modifier_option_export = modifier_option_export[modifier_option_export["Archived"].apply(lambda x: x.lower() if isinstance(x, str) else x) != "yes"]

    # Drop duplicate modifier options with the same name (case-insensitive)
    modifier_option_export = modifier_option_export.drop_duplicates(
        subset=["Name"], keep='first', ignore_index=True)

    # Create the modifier option DataFrame
    modifier_option = sheets_dict["Modifier Option"][0:0]
    modifier_option['id'] = pd.Series(
        range(1, len(modifier_option_export) + 1))
    modifier_option['optionName'] = modifier_option_export['Name']
    modifier_option['posDisplayName'] = modifier_option_export['Name']
    modifier_option['kdsDisplayName'] = modifier_option_export['Name']
    modifier_option['price'] = modifier_option_export["Base Price"]

    # Assign the filled DataFrame to 'sheets_dict["Modifier Option"]'
    sheets_dict["Modifier Option"] = modifier_option
    return sheets_dict

def fill_category_items(sheets_dict, item_category_report):
    # *****************************************************
    # ********** Filling Category Items ********************
    # *****************************************************

    # Create a dictionary with key as Sales Category (Menu Group) and Menu Item as list of values
    item_category_report_dict = item_category_report.groupby("Menu Group")[
        "Menu Item"].apply(list).to_dict()

    # Get Category and Item IDs from sheets_dict
    category_ids = sheets_dict["Category"][["id", "categoryName"]].copy()
    item_ids = sheets_dict["Item"][["id", "itemName"]].copy()

    # Convert names to lowercase and strip spaces for case-insensitive matching
    category_ids["categoryName"] = category_ids["categoryName"].str.lower().str.strip()
    item_ids["itemName"] = item_ids["itemName"].str.lower().str.strip()

    # Create mapping dictionaries: categoryName -> id and itemName -> id
    category_id_map = dict(zip(category_ids["categoryName"], category_ids["id"]))
    item_id_map = dict(zip(item_ids["itemName"], item_ids["id"]))

    # List to store rows for the new DataFrame
    rows = []

    # Sort order initialization
    sort_order = 1

    # Iterate through the item_category_report_dict to map items to categories
    for category_name, menu_items in item_category_report_dict.items():
        # Normalize the category name (lowercase and strip spaces for matching)
        category_name_lower = category_name.lower().strip()

        # Debugging: Print the category we're trying to map
        print(f"Trying to map category: '{category_name_lower}'")

        # Check if the category exists in the category_id_map
        if category_name_lower in category_id_map:
            category_id = category_id_map[category_name_lower]
            print(f"Found matching category: {category_name_lower} -> ID {category_id}")
            
            # Iterate through each menu item under the category
            for item_name in menu_items:
                # Normalize the item name (lowercase and strip spaces for matching)
                item_name_lower = item_name.lower().strip()

                # Check if the item exists in the item_id_map
                if item_name_lower in item_id_map:
                    item_id = item_id_map[item_name_lower]

                    # Add a new row to the list (id is just the length of rows + 1)
                    rows.append({
                        "id": len(rows) + 1,
                        "categoryId": category_id,
                        "itemId": item_id,
                        "sortOrder": sort_order
                    })

                    # Increment the sort order
                    sort_order += 1
                else:
                    print(f"Warning: Menu item '{item_name}' not found in Item mapping.")
        else:
            print(f"Warning: Sales category '{category_name}' not found in Category mapping. Defaulting to Misc.")

    # Create the DataFrame from the rows list
    category_items_df = pd.DataFrame(
        rows, columns=["id", "categoryId", "itemId", "sortOrder"])
    
    #if sort order is missing then see the last one and add one to it and assign it
    if category_items_df["sortOrder"].isnull().any():
        last_sort_order = category_items_df["sortOrder"].max()
        category_items_df["sortOrder"].fillna(last_sort_order + 1, inplace=True)

    # Drop duplicates if any
    category_items_df = category_items_df.drop_duplicates(
        subset=["categoryId", "itemId"], keep='first', ignore_index=True)

    # Update the sheets_dict["Category Items"] with the new DataFrame
    sheets_dict["Category Items"] = category_items_df

    return sheets_dict


def fill_online_item_category(sheets_dict, onlineItemCategoryMapping):
    # *****************************************************
    # ********** Filling Category Items ********************
    # *****************************************************

    # create a json with key as Sales Category, and Menu Item as list of values
    item_category_report_dict = onlineItemCategoryMapping.groupby("category_name")[
        "item_name"].apply(list).to_dict()

    # Compare Sales Category to categoryName, if same then get id from sheets_dict["Category"]
    category_ids = sheets_dict["Category"][["id", "categoryName"]]
    item_ids = sheets_dict["Item"][["id", "itemName"]]

    # Create the mapping dictionaries
    category_id_map = dict(
        zip(category_ids["categoryName"], category_ids["id"]))
    item_id_map = dict(zip(item_ids["itemName"], item_ids["id"]))

    # Create item_modifier_report_dict_ids with error handling
    item_modifier_report_dict_ids = {}

    for online_category, menu_items in item_category_report_dict.items():
        if online_category in category_id_map:
            category_id = category_id_map[online_category]
            item_ids_list = []
            for menu_item in menu_items:
                if menu_item in item_id_map:
                    item_ids_list.append(item_id_map[menu_item])
                else:
                    print(
                        f"Warning: Menu Item '{menu_item}' not found in item_id_map")
            item_modifier_report_dict_ids[category_id] = item_ids_list
        else:
            print(
                f"Warning: Online Category '{online_category}' not found in category_id_map")

    # Prepare the data for the new DataFrame
    rows = sheets_dict["Category Items"]
    #make it a list of rows
    rows = rows.to_dict('records')

    sort_order = None  # Starting sort order

    for category_id, item_ids in item_modifier_report_dict_ids.items():
        for item_id in item_ids:
            rows.append({"id": len(rows) + 1, "categoryId": category_id,
                         "itemId": item_id, "sortOrder": sort_order})
            sort_order = None

    # Create the DataFrame
    category_items_df = pd.DataFrame(
        rows, columns=["id", "categoryId", "itemId", "sortOrder"])

    # drop duplicates
    category_items_df = category_items_df.drop_duplicates(
        subset=["categoryId", "itemId"], keep='first', ignore_index=True)

    # Fill the sheets_dict["Category Items"] with the new data. don't remove the previous data
    sheets_dict["Category Items"] = category_items_df
    return sheets_dict


def fill_item_modifiers(sheets_dict, item_modifiers):

    # ********************************************
    # ********** Filling Item Modifiers***********
    # ********************************************

    # Group by "Parent Menu Selection" and create lists of "Option Group Name"
    item_modifier_report_dict = (
        item_modifiers.groupby("Parent Menu Selection")["Option Group Name"]
        .apply(lambda x: [item for item in x if pd.notna(item)])
        .to_dict()
    )

    # Convert to lower case for case-insensitive comparison
    item_ids = sheets_dict["Item"][["id", "itemName"]].copy()
    item_ids["itemName"] = item_ids["itemName"].str.lower()

    modifier_ids = sheets_dict["Modifier"][["id", "modifierName"]].copy()
    modifier_ids["modifierName"] = modifier_ids["modifierName"].str.lower()

    # Create the mapping dictionaries
    item_id_map = dict(zip(item_ids["itemName"], item_ids["id"]))
    modifier_id_map = dict(
        zip(modifier_ids["modifierName"], modifier_ids["id"]))

    # Create item_modifier_report_dict_ids with error handling
    item_modifier_report_dict_ids = {}

    for menu_item, modifiers in item_modifier_report_dict.items():
        menu_item_lower = menu_item.lower()
        if menu_item_lower in item_id_map:
            item_id = item_id_map[menu_item_lower]
            modifier_ids_list = []
            for modifier in modifiers:
                modifier_lower = modifier.lower()
                if modifier_lower in modifier_id_map:
                    modifier_ids_list.append(modifier_id_map[modifier_lower])
                else:
                    # Add new modifier with name "item_name Mods" if not found
                    new_modifier_name = f"{menu_item} Mods"
                    new_modifier_id = len(sheets_dict["Modifier"]) + 1
                    
                    # Use pd.concat instead of append
                    new_row = pd.DataFrame({
                        "id": [new_modifier_id], 
                        "modifierName": [new_modifier_name],
                        "price": [0]
                    })
                    sheets_dict["Modifier"] = pd.concat([sheets_dict["Modifier"], new_row], ignore_index=True)
                    
                    # Update modifier_id_map with the new modifier
                    modifier_id_map[new_modifier_name.lower()] = new_modifier_id
                    modifier_ids_list.append(new_modifier_id)

            item_modifier_report_dict_ids[item_id] = modifier_ids_list

    # Prepare the data for the new DataFrame
    rows = []
    sort_order = None  # Starting sort order

    for item_id, modifier_ids in item_modifier_report_dict_ids.items():
        for modifier_id in modifier_ids:
            rows.append({
                "id": len(rows) + 1,
                "itemId": item_id,
                "modifierId": modifier_id,
                "sortOrder": sort_order
            })
            sort_order = None

    # Create the DataFrame
    item_modifiers_df = pd.DataFrame(
        rows, columns=["id", "itemId", "modifierId", "sortOrder"]
    )

    # Drop duplicates
    item_modifiers_df = item_modifiers_df.drop_duplicates(
        subset=["itemId", "modifierId"], keep='first', ignore_index=True)

    # Fill the sheets_dict["Item Modifiers"] with the new data
    sheets_dict["Item Modifiers"] = item_modifiers_df

    return sheets_dict



def fill_modifier_groups(sheets_dict, modifier_options):
    # Drop rows with missing Modifier
    modifier_options.dropna(subset=['Modifier'], inplace=True)

    # Convert all relevant columns to lower case and strip for comparison
    sheets_dict["Modifier"]["modifierName"] = sheets_dict["Modifier"]["modifierName"].str.lower().str.strip()
    sheets_dict["Modifier Option"]["optionName"] = sheets_dict["Modifier Option"]["optionName"].str.lower().str.strip()

    # Drop rows with missing modifierName or optionName
    sheets_dict["Modifier"].dropna(subset=['modifierName'], inplace=True)
    sheets_dict["Modifier Option"].dropna(subset=['optionName'], inplace=True)

    modifier_options["Modifier"] = modifier_options["Modifier"].str.lower().str.strip()
    modifier_options["Option Group Name"] = modifier_options["Option Group Name"].str.lower().str.strip()
    modifier_options["Parent Menu Selection"] = modifier_options["Parent Menu Selection"].str.lower().str.strip()

    # Identify rows with NaN in 'Option Group Name'
    nan_rows = modifier_options[modifier_options["Option Group Name"].isna()]

    new_rows = []
    # Generate new id
    new_id = len(sheets_dict["Modifier"]) + 1
    for index, row in nan_rows.iterrows():
        # Create new row for sheets_dict["Modifier"]
        new_row = {
            'id': new_id,
            'modifierName': row["Parent Menu Selection"] + " Mods"
        }
        new_id += 1
        new_rows.append(new_row)
    
    # Append new rows to sheets_dict["Modifier"]
    if new_rows:
        new_rows_df = pd.DataFrame(new_rows)
        sheets_dict["Modifier"] = pd.concat([sheets_dict["Modifier"], new_rows_df], ignore_index=True)

    # Replace NaN in 'Option Group Name' with 'Parent Menu Selection' + " Mods"
    modifier_options.loc[modifier_options["Option Group Name"].isna(), "Option Group Name"] = (
        modifier_options["Parent Menu Selection"] + " Mods"
    )

    # Create dictionaries for quick lookups
    modifier_dict = sheets_dict["Modifier"].set_index("modifierName")["id"].to_dict()
    option_group_dict = sheets_dict["Modifier Option"].set_index("optionName")["id"].to_dict()

    rows = []

    # Iterate through the modifier options to fill in the rows
    for index, row in modifier_options.iterrows():
        modifier_name = row["Modifier"]
        option_group_name = row["Option Group Name"]

        # Get the modifier_id and option_group_id from dictionaries
        modifier_id = modifier_dict.get(option_group_name)
        option_group_id = option_group_dict.get(modifier_name)

        # Check if the modifier_id and option_group_id exist before trying to access them
        if modifier_id is not None and option_group_id is not None:
            rows.append({
                "modifierId": modifier_id,
                "modifierOptionId": option_group_id,
                "isDefaultSelected": False,
                "maxLimit": 1
            })
        else:
            # Print a warning for any missing modifiers or option groups
            if modifier_id is None:
                print(f"Warning: Option Group '{option_group_name}' not found in modifier dictionary")
            if option_group_id is None:
                print(f"Warning: Modifier '{modifier_name}' not found in option group dictionary")

    # Create the DataFrame
    modifiers_groups_df = pd.DataFrame(rows, columns=["modifierId", "modifierOptionId", "isDefaultSelected", "maxLimit"])

    # Drop duplicates
    modifiers_groups_df.drop_duplicates(subset=["modifierId", "modifierOptionId"], keep='first', inplace=True)

    # Fill the sheets_dict["Modifier ModifierOptions"] with the new data
    sheets_dict["Modifier ModifierOptions"] = modifiers_groups_df

    return sheets_dict


def fill_online_item_modifiers(sheets_dict, onlineItemModifierMapping):
    # ********************************************
    # ********** Filling Item Modifiers***********
    # ********************************************

    # Group by "Parent Menu Selection" and create lists of "Option Group Name"
    item_modifier_report_dict = (
        onlineItemModifierMapping.groupby("item_name")["modifier_name"]
        .apply(lambda x: [item for item in x if pd.notna(item)])
        .to_dict()
    )

    # Convert to lower case for case-insensitive comparison
    item_ids = sheets_dict["Item"][["id", "itemName"]].copy()
    item_ids["itemName"] = item_ids["itemName"].str.lower()

    modifier_ids = sheets_dict["Modifier"][["id", "modifierName"]].copy()
    modifier_ids["modifierName"] = modifier_ids["modifierName"].str.lower()

    # Create the mapping dictionaries
    item_id_map = dict(zip(item_ids["itemName"], item_ids["id"]))
    modifier_id_map = dict(
        zip(modifier_ids["modifierName"], modifier_ids["id"]))

    # Create item_modifier_report_dict_ids with error handling
    item_modifier_report_dict_ids = {}

    for menu_item, modifiers in item_modifier_report_dict.items():
        menu_item_lower = menu_item.lower()
        if menu_item_lower in item_id_map:
            item_id = item_id_map[menu_item_lower]
            modifier_ids_list = []
            for modifier in modifiers:
                modifier_lower = modifier.lower()
                if modifier_lower in modifier_id_map:
                    modifier_ids_list.append(modifier_id_map[modifier_lower])
                else:
                    # Add new modifier with name "item_name Mods" if not found
                    new_modifier_name = f"{menu_item} Mods"
                    new_modifier_id = len(sheets_dict["Modifier"]) + 1
                    
                    # Use pd.concat instead of append
                    new_row = pd.DataFrame({
                        "id": [new_modifier_id], 
                        "modifierName": [new_modifier_name],
                        "price": [0]
                    })
                    sheets_dict["Modifier"] = pd.concat([sheets_dict["Modifier"], new_row], ignore_index=True)
                    
                    # Update modifier_id_map with the new modifier
                    modifier_id_map[new_modifier_name.lower()] = new_modifier_id
                    modifier_ids_list.append(new_modifier_id)

            item_modifier_report_dict_ids[item_id] = modifier_ids_list

    # Prepare the data for the new DataFrame
    rows = sheets_dict["Item Modifiers"]
    rows = rows.to_dict('records')  # Convert to list of dicts
    sort_order = None  # Starting sort order

    for item_id, modifier_ids in item_modifier_report_dict_ids.items():
        for modifier_id in modifier_ids:
            rows.append({
                "id": len(rows) + 1,
                "itemId": item_id,
                "modifierId": modifier_id,
                "sortOrder": sort_order
            })
            sort_order = None  # Reset sort order for next item

    # Create the DataFrame for item modifiers
    item_modifiers_df = pd.DataFrame(
        rows, columns=["id", "itemId", "modifierId", "sortOrder"]
    )

    # Drop duplicates
    item_modifiers_df = item_modifiers_df.drop_duplicates(
        subset=["itemId", "modifierId"], keep='first', ignore_index=True)

    # Update sheets_dict["Item Modifiers"] with the new data
    sheets_dict["Item Modifiers"] = item_modifiers_df

    #********************************************************************************************************
    ############################ONLINE MODIFIER OPTIONS########################################################
    #********************************************************************************************************

    # Convert all relevant columns to lower case and strip for comparison
    sheets_dict["Modifier"]["modifierName"] = sheets_dict["Modifier"]["modifierName"].str.lower().str.strip()
    sheets_dict["Modifier Option"]["optionName"] = sheets_dict["Modifier Option"]["optionName"].str.lower().str.strip()

    # Drop rows with missing modifierName or optionName
    sheets_dict["Modifier"].dropna(subset=['modifierName'], inplace=True)
    sheets_dict["Modifier Option"].dropna(subset=['optionName'], inplace=True)

    onlineItemModifierMapping["option_name"] = onlineItemModifierMapping["option_name"].str.lower().str.strip()
    onlineItemModifierMapping["modifier_name"] = onlineItemModifierMapping["modifier_name"].str.lower().str.strip()
    onlineItemModifierMapping["item_name"] = onlineItemModifierMapping["item_name"].str.lower().str.strip()

    # Identify rows with NaN in 'Option Group Name'
    nan_rows = onlineItemModifierMapping[onlineItemModifierMapping["item_name"].isna()]

    new_rows = []
    # Generate new id
    new_id = len(sheets_dict["Modifier"]) + 1
    for index, row in nan_rows.iterrows():
        # Create new row for sheets_dict["Modifier"]
        new_row = {
            'id': new_id,
            'modifierName': row["item_name"] + " Mods"
        }
        new_id += 1
        new_rows.append(new_row)
    
    # Append new rows to sheets_dict["Modifier"]
    if new_rows:
        new_rows_df = pd.DataFrame(new_rows)
        sheets_dict["Modifier"] = pd.concat([sheets_dict["Modifier"], new_rows_df], ignore_index=True)

    # Replace NaN in 'Option Group Name' with 'Parent Menu Selection' + " Mods"
    onlineItemModifierMapping.loc[onlineItemModifierMapping["modifier_name"].isna(), "modifier_name"] = (
        onlineItemModifierMapping["item_name"] + " Mods"
    )

    # Create dictionaries for quick lookups
    modifier_dict = sheets_dict["Modifier"].set_index("modifierName")["id"].to_dict()
    option_group_dict = sheets_dict["Modifier Option"].set_index("optionName")["id"].to_dict()

    rows = sheets_dict["Modifier ModifierOptions"]
    # make it a list
    rows = rows.to_dict('records')
    
    # Iterate through the modifier options to fill in the rows
    for index, row in onlineItemModifierMapping.iterrows():
        modifier_name = row["option_name"]
        option_group_name = row["modifier_name"]

        # Get the modifier_id and option_group_id from dictionaries
        modifier_id = modifier_dict.get(option_group_name)
        option_group_id = option_group_dict.get(modifier_name)

        # Check if the modifier_id and option_group_id exist before trying to access them
        if modifier_id is not None and option_group_id is not None:
            rows.append({
                "modifierId": modifier_id,
                "modifierOptionId": option_group_id,
                "isDefaultSelected": False,
                "maxLimit": 1
            })
        else:
            # Print a warning for any missing modifiers or option groups
            if modifier_id is None:
                print(f"Warning: Option Group '{option_group_name}' not found in modifier dictionary")
            if option_group_id is None:
                print(f"Warning: Modifier '{modifier_name}' not found in option group dictionary")

    # Create the DataFrame
    modifiers_groups_df = pd.DataFrame(rows, columns=["modifierId", "modifierOptionId", "isDefaultSelected", "maxLimit"])

    # Drop duplicates
    modifiers_groups_df.drop_duplicates(subset=["modifierId", "modifierOptionId"], keep='first', inplace=True)

    # Fill the sheets_dict["Modifier ModifierOptions"] with the new data
    sheets_dict["Modifier ModifierOptions"] = modifiers_groups_df

    return sheets_dict

def save_sheets_to_excel(sheets_dict, output_file):
    with pd.ExcelWriter(output_file) as writer:
        for sheet_name, df in sheets_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def fill_menu(sheets_dict, menu_export, menugroup_export, menuitem_export, menuoptiongroup_export, menuoption_export, itemselectiondetails_export, itemmodifierselectiondetails_export,  onlineItemCategoryMapping, onlineItemModifierMapping):
    if sheets_dict is None:
        file_path = "menu_desired_format/menu_desired.xlsx"
        sheets_dict = load_data(file_path)

    sheets_dict = fill_category_sheet(sheets_dict, parent_categories=menu_export, sub_categories=menugroup_export)
    sheets_dict = fill_item_sheet(sheets_dict, item_export=menuitem_export)
    sheets_dict = fill_modifier_sheet(sheets_dict, modifier_export=menuoptiongroup_export)
    sheets_dict = fill_modifier_option_sheet(sheets_dict, modifier_option_export=menuoption_export)
    sheets_dict = fill_category_items(sheets_dict, item_category_report=itemselectiondetails_export)
    sheets_dict = fill_item_modifiers(sheets_dict, item_modifiers=itemmodifierselectiondetails_export)
    sheets_dict = fill_modifier_groups(sheets_dict, modifier_options=itemmodifierselectiondetails_export)

    # fill data from online.
    if onlineItemCategoryMapping and onlineItemModifierMapping:
        print("filling from online")
        sheets_dict = fill_online_item_category(sheets_dict, onlineItemCategoryMapping=onlineItemCategoryMapping)
        sheets_dict = fill_online_item_modifiers(sheets_dict, onlineItemModifierMapping=onlineItemModifierMapping)
        print("online filled")

    # Create a dictionary of sheets for missing data
    missing_data = {
        "Items With No Categories": None,
        "Modifiers Not in Sales": None,
        "Options Not in Sales": None
    }

    # Find items with no categories
    item_ids_with_categories = set(sheets_dict["Category Items"]["itemId"])
    all_item_ids = set(sheets_dict["Item"]["id"])
    items_with_no_categories = all_item_ids - item_ids_with_categories
    items_with_no_categories_df = sheets_dict["Item"][sheets_dict["Item"]["id"].isin(items_with_no_categories)][["id", "itemName"]]
    missing_data["Items With No Categories"] = items_with_no_categories_df
    # map all the items to category 0 sheets_dict["Category Items"]
    for item_id in items_with_no_categories:
        new_row = pd.DataFrame({
        "id": [len(sheets_dict["Category Items"]) + 1],
        "categoryId": [len(sheets_dict["Category"])],
        "itemId": [item_id],
        "sortOrder": [len(sheets_dict["Category Items"]) + 1]
        })
        sheets_dict["Category Items"] = pd.concat([sheets_dict["Category Items"], new_row], ignore_index=True)
    # Find modifiers not in sales
    modifier_names_in_sales = set(itemmodifierselectiondetails_export["Option Group Name"].str.lower().dropna())
    all_modifier_names = set(sheets_dict["Modifier"]["modifierName"].str.lower().dropna())
    modifiers_not_in_sales = all_modifier_names - modifier_names_in_sales
    modifiers_not_in_sales_df = sheets_dict["Modifier"][sheets_dict["Modifier"]["modifierName"].str.lower().isin(modifiers_not_in_sales)][["id", "modifierName"]]
    missing_data["Modifiers Not in Sales"] = modifiers_not_in_sales_df

    # Find options not in sales
    option_names_in_sales = set(itemmodifierselectiondetails_export["Modifier"].str.lower().dropna())
    all_option_names = set(sheets_dict["Modifier Option"]["optionName"].str.lower().dropna())
    options_not_in_sales = all_option_names - option_names_in_sales
    options_not_in_sales_df = sheets_dict["Modifier Option"][sheets_dict["Modifier Option"]["optionName"].str.lower().isin(options_not_in_sales)][["id", "optionName"]]
    missing_data["Options Not in Sales"] = options_not_in_sales_df

    save_sheets_to_excel(sheets_dict, "Menu.xlsx")
    save_sheets_to_excel(missing_data, "Missing_Menu.xlsx")


