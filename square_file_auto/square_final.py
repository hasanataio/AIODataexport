import pandas as pd
import numpy as np


def fun_items_sheet_handler(file):
    items_sheet_df = pd.read_excel(file, sheet_name='Items')
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
    return final_aio_df


def fun_items_sheet_handler_with_category(file):
    items_sheet_df = pd.read_excel(file, sheet_name='Items')
    items_sheet_df = items_sheet_df.dropna(how='all')
    items_sheet_df['id'] = range(1, len(items_sheet_df) + 1)

    final_aio_df = items_sheet_df[['id', 'Item Name', 'Category']].copy()
    new_column_names = ['id', 'itemName', 'itemCategory']

    final_aio_df = final_aio_df.rename(columns=dict(zip(final_aio_df.columns, new_column_names)))
    return final_aio_df


def fun_sections_sheet_handler(file):
    sections_sheet_df = pd.read_excel(file, sheet_name='Items')
    sections_sheet_df.dropna(how='all')
    sections_sheet_df = sections_sheet_df.drop_duplicates(subset=['Category'], keep='first')
    sections_sheet_df = sections_sheet_df.dropna(subset=['Category'])

    sections_sheet_df['id'] = range(1, len(sections_sheet_df) + 1)
    final_aio_df = sections_sheet_df[['id', 'Category']].copy()

    new_column_names = ['id', 'categoryName']
    final_aio_df.rename(columns=dict(zip(final_aio_df.columns, new_column_names)))
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
    modifiers_df = old_modifiers_df[['id', 'Category']].copy()

    new_items_df_column_names = {'id': 'item_id', 'itemName': 'item_name', 'itemCategory':'modifiers_in_items'}
    new_modifiers_df_column_names = {'id': 'modifier_id', 'Category': 'modifier'}

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


def fun_write_headers(ws, headers):
    ws.insert_rows(1)
    for col, header in zip(range(1, len(headers) + 1), headers):
        ws.cell(row=1, column=col, value=header)


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
    modifier_headers_df.to_excel(excel_writer, sheet_name="Menu", index=False)
    menu_headers_df.to_excel(excel_writer, sheet_name="items", index=False)
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


if __name__ == '__main__':
    file_to_upload = "files\\square_template.xlsx"
    final_download_file = 'square_raw.xlsx'

    items_df = fun_items_sheet_handler(file_to_upload)
    sections_df = fun_sections_sheet_handler(file_to_upload)
    item_cat_df = fun_items_sheet_handler_with_category(file_to_upload)

    item_category_df = fun_item_category_mapping(item_cat_df, sections_df)

    writer = pd.ExcelWriter(final_download_file, engine='openpyxl')

    items_df.to_excel(writer, sheet_name="items", index=False)
    sections_df.to_excel(writer, sheet_name="Category", index=False)
    item_category_df.to_excel(writer, sheet_name="Category Items", index=False)
    fun_sheet_filler(writer)
    writer._save()
    print('first part Exported Successfully..!!! ')

