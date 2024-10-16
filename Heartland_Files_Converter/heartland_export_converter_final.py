import pandas as pd


def fun_items_sheet_handler():
    items_sheet_df = pd.read_excel('input_files\\Heartland Template.xlsx', sheet_name='Items')
    items_sheet_df = items_sheet_df.dropna(how='all')
    items_sheet_df['id'] = range(1, len(items_sheet_df) + 1)

    final_aio_df = items_sheet_df[['id', 'name', 'description', 'price']].copy()
    new_column_names = {'name': 'itemName', 'description': 'itemDescription', 'price': 'itemPrice'}

    final_aio_df = final_aio_df.rename(columns=new_column_names)
    return final_aio_df


def fun_sections_sheet_handler():
    sections_sheet_df = pd.read_excel('input_files\\Heartland Template.xlsx', sheet_name='Sections')
    sections_sheet_df.dropna(how='all')
    sections_sheet_df['id'] = range(1, len(sections_sheet_df) + 1)
    final_aio_df = sections_sheet_df[['id', 'name']].copy()

    new_column_names = {'name': 'categoryName'}
    final_aio_df.rename(columns=new_column_names, inplace=True)
    return final_aio_df


def fun_ingredients_sheet_handler():
    sections_sheet_df = pd.read_excel('input_files\\Heartland Template.xlsx', sheet_name='Ingredients')
    sections_sheet_df.dropna(how='all')
    sections_sheet_df['id'] = range(1, len(sections_sheet_df) + 1)
    final_aio_df = sections_sheet_df[['id', 'name']].copy()

    new_column_names = {'name': 'optionName'}
    final_aio_df.rename(columns=new_column_names, inplace=True)
    return final_aio_df


def fun_groups_sheet_handler():
    groups_sheet_df = pd.read_excel('input_files\\Heartland Template.xlsx', sheet_name='Groups')
    groups_sheet_df.dropna(how='all')
    groups_sheet_df['id'] = range(1, len(groups_sheet_df) + 1)
    final_aio_df = groups_sheet_df[['id', 'name']].copy()

    new_column_names = {'name': 'menuName'}
    final_aio_df.rename(columns=new_column_names, inplace=True)
    return final_aio_df


def fun_modifiers_sheet_handler():
    groups_sheet_df = pd.read_excel('input_files\\Heartland Template.xlsx', sheet_name='Modifiers')
    groups_sheet_df.dropna(how='all')
    groups_sheet_df['id'] = range(1, len(groups_sheet_df) + 1)
    final_aio_df = groups_sheet_df[['id', 'name']].copy()

    new_column_names = {'name': 'modifierName'}
    final_aio_df.rename(columns=new_column_names, inplace=True)
    return final_aio_df


def fun_item_modifier_mapping(items_df_path, modifiers_df_path):
    old_items_df = pd.read_excel(items_df_path, sheet_name='Items')
    old_modifiers_df = pd.read_excel(modifiers_df_path, sheet_name='Modifiers')

    old_items_df['new_item_id'] = range(1, len(old_items_df) + 1)
    old_modifiers_df['new_modifier_id'] = range(1, len(old_modifiers_df) + 1)

    items_df = old_items_df[['new_item_id', 'name', 'modifiers']].copy()
    modifiers_df = old_modifiers_df[['new_modifier_id', 'name']].copy()

    new_items_df_column_names = {'new_item_id': 'item_id', 'name': 'item_name', 'modifiers':'modifiers_in_items'}
    new_modifiers_df_column_names = {'new_modifier_id': 'modifier_id', 'name': 'modifier'}

    items_df.rename(columns=new_items_df_column_names, inplace=True)
    modifiers_df.rename(columns=new_modifiers_df_column_names, inplace=True)

    item_modifier_mapping = []

    def create_item_modifier_mapping(row):
        item_id = row['item_id']
        modifiers = row['modifiers_in_items'].strip('"').split('","') if pd.notna(row['modifiers_in_items']) else []
        for modifier in modifiers:
            modifier_id = modifiers_df[modifiers_df['modifier'] == modifier]['modifier_id'].values[0]
            item_modifier_mapping.append((str(item_id), str(modifier_id)))

    items_df.apply(create_item_modifier_mapping, axis=1)
    first_elements, second_elements = zip(*item_modifier_mapping)

    df = pd.DataFrame(list(zip(first_elements, second_elements)), columns=['itemId', 'modifierId'])

    return df


def create_modifier_item_mapping(items_df_path, modifiers_df_path):
    old_items_df = pd.read_excel(items_df_path, sheet_name='Ingredients')
    old_modifiers_df = pd.read_excel(modifiers_df_path, sheet_name='Modifiers')

    old_items_df['new_item_id'] = range(1, len(old_items_df) + 1)
    old_modifiers_df['new_modifier_id'] = range(1, len(old_modifiers_df) + 1)

    items_df = old_items_df[['new_item_id', 'name', 'modifiers']].copy()
    modifiers_df = old_modifiers_df[['new_modifier_id', 'name']].copy()

    new_items_df_column_names = {'new_item_id': 'item_id', 'name': 'item_name', 'modifiers':'modifiers_in_items'}
    new_modifiers_df_column_names = {'new_modifier_id': 'modifier_id', 'name': 'modifier'}

    items_df.rename(columns=new_items_df_column_names, inplace=True)
    modifiers_df.rename(columns=new_modifiers_df_column_names, inplace=True)

    modifier_item_mapping = []

    def create_modifier_item_mapping(row):
        modifier_id = row['modifier_id']
        modifier = row['modifier']
        items_with_modifier = items_df[items_df['modifiers_in_items'].str.contains(modifier, na=False)]['item_id'].tolist()
        for item_id in items_with_modifier:
            modifier_item_mapping.append((str(modifier_id), str(item_id)))

    modifiers_df.apply(create_modifier_item_mapping, axis=1)
    first_elements, second_elements = zip(*modifier_item_mapping)
    df = pd.DataFrame(list(zip(first_elements, second_elements)), columns=['modifierId', 'modifierOptionId'])
    return df


def fun_category_menu_mapping():
    old_items_df = pd.read_excel('input_files\\Heartland Template.xlsx', sheet_name='Sections')
    old_modifiers_df = pd.read_excel('input_files\\Heartland Template.xlsx', sheet_name='Groups')
    old_items_df['new_item_id'] = range(1, len(old_items_df) + 1)
    old_modifiers_df['new_modifier_id'] = range(1, len(old_modifiers_df) + 1)

    items_df = old_items_df[['new_item_id', 'name', 'groups']].copy()
    modifiers_df = old_modifiers_df[['new_modifier_id', 'name']].copy()

    new_items_df_column_names = {'new_item_id': 'item_id', 'name': 'item_name', 'groups':'modifiers_in_items'}
    new_modifiers_df_column_names = {'new_modifier_id': 'modifier_id', 'name': 'modifier'}

    items_df.rename(columns=new_items_df_column_names, inplace=True)
    modifiers_df.rename(columns=new_modifiers_df_column_names, inplace=True)
    # --------------------------------------------------------------------------

    item_modifier_mapping_dict = {}

    def create_item_modifier_mapping(row):
        item_id = row['item_id']
        modifiers = row['modifiers_in_items'].strip('"').split('","') if pd.notna(row['modifiers_in_items']) else []
        for modifier in modifiers:
            modifier_id = modifiers_df[modifiers_df['modifier'] == modifier]['modifier_id'].values[0]
            if item_id in item_modifier_mapping_dict:
                item_modifier_mapping_dict[item_id].append(modifier_id)
            else:
                item_modifier_mapping_dict[item_id] = [modifier_id]

    items_df.apply(create_item_modifier_mapping, axis=1)

    item_modifier_df = pd.DataFrame(item_modifier_mapping_dict.items(), columns=['item_id', 'modifier_id'])
    item_modifier_df['modifier_id'] = item_modifier_df['modifier_id'].apply(lambda x: ','.join(map(str, x)))
    item_modifier_df = item_modifier_df.sort_values(by='item_id').reset_index(drop=True)

    merged_df = pd.merge(item_modifier_df, items_df[['item_id', 'item_name']], on='item_id', how='left')
    merged_df = merged_df[['item_id', 'item_name', 'modifier_id']]

    new_col_names = {'item_id': 'id', 'item_name': 'categoryName', 'modifier_id': 'menuIds'}
    merged_df.rename(columns=new_col_names, inplace=True)

    return merged_df


def fun_item_category_mapping(items_df_path, modifiers_df_path):
    old_items_df = pd.read_excel(items_df_path, sheet_name='Items')
    old_modifiers_df = pd.read_excel(modifiers_df_path, sheet_name='Sections')

    old_items_df['new_item_id'] = range(1, len(old_items_df) + 1)
    old_modifiers_df['new_modifier_id'] = range(1, len(old_modifiers_df) + 1)

    items_df = old_items_df[['new_item_id', 'name', 'sections']].copy()
    modifiers_df = old_modifiers_df[['new_modifier_id', 'name']].copy()

    new_items_df_column_names = {'new_item_id': 'item_id', 'name': 'item_name', 'sections':'modifiers_in_items'}
    new_modifiers_df_column_names = {'new_modifier_id': 'modifier_id', 'name': 'modifier'}

    items_df.rename(columns=new_items_df_column_names, inplace=True)
    modifiers_df.rename(columns=new_modifiers_df_column_names, inplace=True)

    modifier_item_mapping = []

    def create_modifier_item_mapping(row):
        modifier_id = row['modifier_id']
        modifier = row['modifier']
        items_with_modifier = items_df[items_df['modifiers_in_items'].str.contains(modifier, na=False)]['item_id'].tolist()
        for item_id in items_with_modifier:
            modifier_item_mapping.append((str(modifier_id), str(item_id)))

    modifiers_df.apply(create_modifier_item_mapping, axis=1)
    first_elements, second_elements = zip(*modifier_item_mapping)

    df = pd.DataFrame(list(zip(first_elements, second_elements)), columns=['categoryId', 'itemId'])
    df['id'] = range(1, len(df) + 1)
    df = df[['id', 'categoryId', 'itemId']]

    return df


if __name__ == '__main__':

    items_df = fun_items_sheet_handler()
    sections_df = fun_sections_sheet_handler()
    groups_df = fun_groups_sheet_handler()
    modifier_df = fun_modifiers_sheet_handler()
    options_df = fun_ingredients_sheet_handler()

    items_df_path = 'input_files\\Heartland Template.xlsx'
    modifiers_df_path = 'input_files\\Heartland Template.xlsx'
    item_modifier_mapping_df = fun_item_modifier_mapping(items_df_path, modifiers_df_path)

    items_df_path = 'input_files\\Heartland Template.xlsx'
    modifiers_df_path = 'input_files\\Heartland Template.xlsx'
    modifier_item_df2 = create_modifier_item_mapping(items_df_path, modifiers_df_path)

    category_menu_df = fun_category_menu_mapping()
    items_df_path = 'input_files\\Heartland Template.xlsx'
    modifiers_df_path = 'input_files\\Heartland Template.xlsx'
    item_category_df = fun_item_category_mapping(items_df_path, modifiers_df_path)

    writer = pd.ExcelWriter('output_files\\heartland_exported.xlsx', engine='openpyxl')

    items_df.to_excel(writer, sheet_name="item", index=False)
    # sections_df.to_excel(writer, sheet_name="Category", index=False)
    groups_df.to_excel(writer, sheet_name="Menu", index=False)
    modifier_df.to_excel(writer, sheet_name="Modifier", index=False)
    options_df.to_excel(writer, sheet_name="Modifier option", index=False)
    item_modifier_mapping_df.to_excel(writer, sheet_name="Item Modifiers", index=False)
    modifier_item_df2.to_excel(writer, sheet_name="Modifier ModifierOptions", index=False)
    category_menu_df.to_excel(writer, sheet_name="Category", index=False)
    item_category_df.to_excel(writer, sheet_name="Category Items", index=False)

    writer._save()
    print('file Exported Successfully..!!! ')


