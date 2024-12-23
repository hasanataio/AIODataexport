import pandas as pd
import numpy as np
import streamlit as st
import io
from screens.fixmissingfield.auto_convert import auto_fix_fields
from fuzzywuzzy import fuzz
from screens.square_file_converter.modules import doordash

def combine_names(item_name, variation_name, threshold=85):
    if variation_name is None or isinstance(variation_name, float):
        return item_name
    # split based on spaces
    item_words = item_name.split()  
    variation_words = variation_name.split()  
    
    # initializations
    combined_name = item_words.copy()  
    extra_words = [] 
    
    # iterate each variation word
    for var_word in variation_words:
        # check for similar words
        if not any(fuzz.ratio(var_word, item_word) > threshold for item_word in item_words):
            extra_words.append(var_word)  
        
    # add extra words in brackets
    if extra_words:
        combined_name.append(f"({' '.join(extra_words)})")
    
    return ' '.join(combined_name)

def clean_data(data):

    data = data[['Item Name', 'Variation Name']]
    data.loc[:, 'Item Name'] = data['Item Name'].str.strip().str.lower()
    data.loc[:, 'Variation Name'] = data['Variation Name'].str.strip().str.lower()
    return data

def preprocessor(data):

    # basic preprocessing
    data = clean_data(data)

    # keep words with no alternative names as it is
    # clean = data[data['Variation Name'].isna()]
    # clean.loc[:, 'AIO Name'] = clean['Item Name']

    # # process only where variation names exsists
    # process = data[data['Variation Name'].notna()]

    data.loc[:, 'AIO Name'] = data.apply(lambda row: combine_names(row['Item Name'], row['Variation Name']), axis=1)

    # df_combined = pd.concat([process, clean], ignore_index=True)
    data['AIO Name'] = data['AIO Name'].str.title()
    aio_names=list(data['AIO Name'])
    data.drop(columns=['AIO Name'],inplace=True)
    return aio_names

def fun_items_sheet_handler(file):
    items_sheet_df = pd.read_excel(file, sheet_name='Items')
    item_varation_names=preprocessor(items_sheet_df)
    items_sheet_df = items_sheet_df.dropna(how='all')
    items_sheet_df['id'] = range(1, len(items_sheet_df) + 1)

    final_aio_df = items_sheet_df[['id', 'Item Name', 'Price']].copy()
    new_column_names = ['id', 'itemName', 'itemPrice']

    final_aio_df = final_aio_df.rename(columns=dict(zip(final_aio_df.columns, new_column_names)))
    final_aio_df['itemPrice'] = final_aio_df['itemPrice'].replace("variable", '0')
    columns_to_add = [
        "itemDescription",
        "itemPicture",
        "onlineImage",
        "thirdPartyImage",
        "kioskItemImage",
        "calories",
        "preparationTime",
        "stockStatus",
        "showOnMenu",
        "showOnline",
        "showPOS",
        "showQR",
        "showThirdParty",
        "posDisplayName",
        "kdsName",
        "startTime",
        "endTime",
        "taxLinkedWithParentSetting",
        "stockValue",
        "calculatePricesWithTaxIncluded",
        "takeoutException",
        "orderQuantityLimit",
        "minLimit",
        "maxLimit",
        "noMaxLimit",
        "inheritTagsFromCategory",
        "inheritModifiersFromCategory",
        "settingId",
        "stationIds",
        "addonIds",
        "taxIds",
        "tagIds",
        "allergenIds"
    ]
    for column in columns_to_add:
        final_aio_df[column] = np.nan
    return final_aio_df,item_varation_names


def fun_items_sheet_handler_with_category(file):
    items_sheet_df = pd.read_excel(file, sheet_name='Items')
    items_sheet_df = items_sheet_df.dropna(how='all')
    items_sheet_df['id'] = range(1, len(items_sheet_df) + 1)

    final_aio_df = items_sheet_df[['id', 'Item Name', 'Category']].copy()
    new_column_names = ['id', 'itemName', 'itemCategory']

    final_aio_df = final_aio_df.rename(columns=dict(zip(final_aio_df.columns, new_column_names)))
    return final_aio_df


# def fun_sections_sheet_handler(file):
#     sections_sheet_df = pd.read_excel(file, sheet_name='Items')
#     sections_sheet_df.dropna(how='all')
#     sections_sheet_df = sections_sheet_df.drop_duplicates(subset=['Category'], keep='first')
#     sections_sheet_df = sections_sheet_df.dropna(subset=['Category'])
#
#     sections_sheet_df['id'] = range(1, len(sections_sheet_df) + 1)
#     final_aio_df = sections_sheet_df[['id', 'Category']].copy()
#
#     new_column_names = ['id', 'categoryName']
#     final_aio_df.rename(columns=dict(zip(final_aio_df.columns, new_column_names)))
#     final_aio_df["parentCategoryId"] = np.nan
#     final_aio_df["image (posImage)"] = np.nan
#     final_aio_df["kdsDisplayName"] = np.nan
#     final_aio_df["posDisplayName"] = np.nan
#     final_aio_df["sortOrder"] = np.nan
#     final_aio_df["kioskImage"] = np.nan
#     final_aio_df["startTime"] = np.nan
#     final_aio_df["endTime"] = np.nan
#     final_aio_df["settingId"] = np.nan
#     final_aio_df["menuIds"] = np.nan
#     final_aio_df["tagIds"] = np.nan
#     return final_aio_df

def fun_sections_sheet_handler(file):
    sections_sheet_df = pd.read_excel(file, sheet_name='Items')
    sections_sheet_df.dropna(how='all', inplace=True)
    sections_sheet_df = sections_sheet_df.drop_duplicates(subset=['Category'], keep='first')
    sections_sheet_df = sections_sheet_df.dropna(subset=['Category'])
    sections_sheet_df['id'] = range(1, len(sections_sheet_df) + 1)
    final_aio_df = sections_sheet_df[['id', 'Category']].copy()
    new_column_names = ['id', 'categoryName']
    final_aio_df.rename(columns=dict(zip(final_aio_df.columns, new_column_names)), inplace=True)
    final_aio_df["parentCategoryId"] = np.nan
    final_aio_df["image (posImage)"] = np.nan
    final_aio_df["kdsDisplayName"] = np.nan
    final_aio_df["posDisplayName"] = np.nan
    final_aio_df["sortOrder"] = np.nan
    final_aio_df["kioskImage"] = np.nan
    final_aio_df["startTime"] = np.nan
    final_aio_df["endTime"] = np.nan
    final_aio_df["settingId"] = np.nan
    final_aio_df["menuIds"] = np.nan
    final_aio_df["tagIds"] = np.nan

    return final_aio_df

def fun_item_category_mapping(old_items_df, old_modifiers_df):

    items_df = old_items_df[['id', 'itemName', 'itemCategory']].copy()
    modifiers_df = old_modifiers_df[['id', 'categoryName']].copy()

    new_items_df_column_names = {'id': 'item_id', 'itemName': 'item_name', 'itemCategory':'modifiers_in_items'}
    new_modifiers_df_column_names = {'id': 'modifier_id', 'categoryName': 'modifier'}

    items_df.rename(columns=new_items_df_column_names, inplace=True)
    modifiers_df.rename(columns=new_modifiers_df_column_names, inplace=True)

    modifier_item_mapping = []

    def create_modifier_item_mapping(row):
        modifier_id = row['modifier_id']
        modifier = row['modifier']
        # items_with_modifier = items_df[items_df['modifiers_in_items'].str.contains(modifier, na=False)]['item_id'].tolist()
        items_with_modifier = items_df[items_df['modifiers_in_items'] == modifier]['item_id'].tolist()
        for item_id in items_with_modifier:
            modifier_item_mapping.append((str(modifier_id), str(item_id)))

    modifiers_df.apply(create_modifier_item_mapping, axis=1)
    first_elements, second_elements = zip(*modifier_item_mapping)

    df = pd.DataFrame(list(zip(first_elements, second_elements)), columns=['categoryId', 'itemId'])
    df['id'] = range(1, len(df) + 1)
    df = df[['id', 'categoryId', 'itemId']]

    df['sortOrder'] = np.nan

    return df


def fun_sheet_filler(excel_writer):
    modifier_options_headers = [
        "id",
        "optionName",
        "posDisplayName",
        "kdsDisplayName",
        "price",
        "isStockAvailable",
        "isSizeModifier"
    ]
    modifier_headers = [
        "id",
        "modifierName",
        "posDisplayName",
        "limit",
        "price",
        "multiSelect",
        "parentModifierId",
        "isNested",
        "addNested",
        "isOptional",
        "stockStatus",
        "priceType",
        "canGuestSelectMoreModifiers",
        "minSelector",
        "maxSelector",
        "noMaxSelection",
        "isSizeModifier",
        "prefix",
        "pizzaSelection",
        "showOnPos",
        "showOnKiosk",
        "showOnMpos",
        "showOnQR",
        "showOnline",
        "showOnThirdParty",
        "limitIndividualModifierSelection"
    ]
    menu_headers = [
        "id",
        "menuName",
        "posDisplayName",
        "menuDescription",
        "picture",
        "startTime",
        "endTime",
        "genericModifierId",
        "restaurantId",
        "sortOrder",
        "settingId",
        "posButtonColor"
    ]
    setting_headers = [
        "id",
        "type"
    ]
    visibility_settings_headers = [
        "id",
        "isDefault",
        "channelVisibilityType",
        "device",
        "settingId"
    ]
    day_schedule_headers = [
        "id",
        "day",
        "startTime",
        "endTime",
        "visibilitySettingId"
    ]
    category_modifier_groups_headers = [
        "categoryId",
        "modifierGroupId",
        "sortOrder"
    ]
    category_modifiers_headers = [
        "categoryId",
        "modifierId",
        "sortOrder"
    ]
    category_items_headers = [
        "id",
        "categoryId",
        "itemId",
        "sortOrder"
    ]
    modifier_group_headers = [
        "id",
        "groupName",
        "posDisplayName",
        "showOnPos",
        "showOnKiosk",
        "showOnMpos",
        "showOnQR",
        "showOnline",
        "showOnThirdParty",
        "modifierIds"
    ]
    modifier_modifier_options_headers = [
        "modifierId",
        "modifierOptionId",
        "isDefaultSelected",
        "maxLimit"
    ]
    allergen_headers = [
        "id",
        "allergenName",
        "image"
    ]
    tag_headers = [
        "id",
        "tagName",
        "image"
    ]
    item_modifier_headers = [
        "itemId",
        "modifierId",
        "sortOrder"
    ]
    item_modifier_group_headers = [
        "itemId",
        "modifierGroupId",
        "sortOrder"
    ]

    modifier_options_headers_df = pd.DataFrame(columns=modifier_options_headers)
    modifier_headers_df = pd.DataFrame(columns=modifier_headers)
    menu_headers_df = pd.DataFrame(columns=menu_headers)
    setting_headers_df = pd.DataFrame(columns=setting_headers)
    visibility_settings_headers_df = pd.DataFrame(columns=visibility_settings_headers)
    day_schedule_headers_df = pd.DataFrame(columns=day_schedule_headers)
    category_modifier_groups_headers_df = pd.DataFrame(columns=category_modifier_groups_headers)
    category_modifiers_headers_df = pd.DataFrame(columns=category_modifiers_headers)
    category_items_headers_df = pd.DataFrame(columns=category_items_headers)
    modifier_group_headers_df = pd.DataFrame(columns=modifier_group_headers)
    modifier_modifier_options_headers_df = pd.DataFrame(columns=modifier_modifier_options_headers)
    allergen_headers_df = pd.DataFrame(columns=allergen_headers)
    tag_headers_df = pd.DataFrame(columns=tag_headers)
    item_modifier_headers_df = pd.DataFrame(columns=item_modifier_headers)
    item_modifier_group_headers_df = pd.DataFrame(columns=item_modifier_group_headers)

    modifier_options_headers_df.to_excel(excel_writer, sheet_name="Modifier Option", index=False)
    modifier_headers_df.to_excel(excel_writer, sheet_name="Modifier", index=False)
    menu_headers_df.to_excel(excel_writer, sheet_name="Menu", index=False)
    setting_headers_df.to_excel(excel_writer, sheet_name="Setting", index=False)
    visibility_settings_headers_df.to_excel(excel_writer, sheet_name="Visibility Setting", index=False)
    day_schedule_headers_df.to_excel(excel_writer, sheet_name="Day Schedule", index=False)
    category_modifier_groups_headers_df.to_excel(excel_writer, sheet_name="Category ModifierGroups", index=False)
    category_modifiers_headers_df.to_excel(excel_writer, sheet_name="Category Modifiers", index=False)
    category_items_headers_df.to_excel(excel_writer, sheet_name="Category Items", index=False)
    modifier_group_headers_df.to_excel(excel_writer, sheet_name="Modifier Group", index=False)
    modifier_modifier_options_headers_df.to_excel(excel_writer, sheet_name="Modifier ModifierOptions", index=False)
    allergen_headers_df.to_excel(excel_writer, sheet_name="Allergen", index=False)
    tag_headers_df.to_excel(excel_writer, sheet_name="Tag", index=False)
    item_modifier_headers_df.to_excel(excel_writer, sheet_name="Item Modifiers", index=False)
    item_modifier_group_headers_df.to_excel(excel_writer, sheet_name="Item Modifier Group", index=False)



def process_file(uploaded_file):
    # Process the uploaded file and generate the output DataFrames
    items_df,item_varation_names = fun_items_sheet_handler(uploaded_file)
    sections_df = fun_sections_sheet_handler(uploaded_file)
    item_cat_df = fun_items_sheet_handler_with_category(uploaded_file)
    item_category_df = fun_item_category_mapping(item_cat_df, sections_df)
    # Write to an Excel file using an in-memory buffer
    download_file_path = 'square_raw.xlsx'
    writer = pd.ExcelWriter(download_file_path, engine='openpyxl')

    items_df.to_excel(writer, sheet_name="Item", index=False)
    sections_df.to_excel(writer, sheet_name="Category", index=False)
    item_category_df.to_excel(writer, sheet_name="Category Items", index=False)
    fun_sheet_filler(writer)
    writer._save()

    return download_file_path,item_varation_names

def square_main():
    st.title("Square Template Processor")
    st.write("Upload an Excel file, process it, and download the result.")

    uploaded_file = st.file_uploader("Upload Square File", type="xlsx")
    doordash_file = st.file_uploader("Upload Doordash File", type="xlsx")
    dataframes=None
    if uploaded_file is not None and doordash_file is not None:
        st.write("File uploaded successfully. Click below to process.")
        # Process the file and create the download link
        download_path,item_varation_names= process_file(uploaded_file)

        download_path=doordash.fill_with_doordash(doordash_file,download_path)

        xls = pd.ExcelFile(download_path)
        df = pd.read_excel(xls, sheet_name="Item")

        # Update the column
        column_name = "itemName"  # Replace with the actual column name you want to update
        df[column_name] = item_varation_names

        # Save the updated DataFrame back to the Excel file
        with pd.ExcelWriter(download_path, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name="Item", index=False)


        with open(download_path, "rb") as file:
            file_content = io.BytesIO(file.read()) 
            dataframes=auto_fix_fields(file_content)
            st.download_button(
                label="Download Square to AIO",
                data=file,
                file_name="Square to AIO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        output = io.BytesIO()

        # Use the buffer as the Excel file
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for key in dataframes.keys():
                dataframes[key].to_excel(writer, sheet_name=key, index=False)
            
        # Seek to the beginning of the stream
        output.seek(0)

        # Provide the download link
        st.download_button(
            label="Download Final Square to AIO",
            data=output,
            file_name='Final Square to AIO.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )