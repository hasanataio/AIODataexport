import pandas as pd
import os
import numpy as np

def print(*args,**kwargs):
    return None

def run_first_step(input_file_path):
    def get_all_sheets(file_name):
        df_dict = dict()
        # file_name = 'New_Menu_Structure (2).xlsx'
        sheet_names = pd.ExcelFile(file_name).sheet_names
        for s in sheet_names:
            df_dict[s] = pd.read_excel(file_name, s)
        return df_dict


    def write_excel(filename, sheetname, dataframe):
        if not os.path.exists(filename):
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                dataframe.to_excel(writer, sheet_name=sheetname, index=False)
        else:
            with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
                workBook = writer.book
                try:
                    workBook.remove(workBook[sheetname])
                except:
                    pass
                finally:
                    dataframe.to_excel(writer, sheet_name=sheetname, index=False)


    def save_all_sheets(file_name, sheets_dict):
        for k in sheets_dict.keys():
            write_excel(file_name, k, sheets_dict[k])


    out_sheets = get_all_sheets(f'{os.getcwd()}/screens/aioconverter/AIO Template.xlsx')
    inp_sheets = get_all_sheets(f'{os.getcwd()}/screens/aioconverter/Clover Template.xlsx')

    inp_sheets['Categories'].columns[1:].values
    out_sheets['Category']['categoryName'] = inp_sheets['Categories'].columns[1:].values
    out_sheets['Category']['id'] = range(1, 1+len(out_sheets['Category']))
    inp_sheets.keys()
    out_sheets.keys()
    mapping_inp = [('Modifier Groups','Modifier'),
                ('Items', 'Name'), ('Items', 'Price'),
                ('Modifier Groups', 'Modifier Group Name'),
                ('Modifier Groups', 'Price')]

    mapping_out = [('Modifier Option', 'optionName'),
                ('Item', 'itemName'),('Item', 'itemPrice'),
                ('Modifier', 'modifierName'),
                ('Modifier Option', 'price')] 

    for m_in, m_out in zip(mapping_inp, mapping_out):
        sheet_name_inp = m_in[0]
        column_name_inp = m_in[1]

        sheet_name_out = m_out[0]
        column_name_out = m_out[1]

        cleaned_values = inp_sheets[sheet_name_inp][column_name_inp].dropna()
        out_sheets[sheet_name_out] = out_sheets[sheet_name_out].reindex(range(len(cleaned_values)))
        out_sheets[sheet_name_out][column_name_out] = cleaned_values.values
        out_sheets[sheet_name_out]['id'] = range(1, 1+len(out_sheets[sheet_name_out]))

    out_sheets['Modifier Option'].drop_duplicates('optionName', inplace=True)
    out_sheets['Modifier Option']['id'] = range(1, 1+len(out_sheets['Modifier Option']))

    save_all_sheets('Mijos Menu AIO.xlsx', out_sheets)


    def generate_unique_ids(df):
        modifier_group_ids = {group: i + 1 for i, group in enumerate(df['Modifier Group Name'].dropna().unique())}
        modifier_ids = {modifier: i + 1 for i, modifier in enumerate(df['Modifier'].unique())}
        return modifier_group_ids, modifier_ids


    def map_ids_to_dataframe(df, modifier_group_ids, modifier_ids):
        current_modifier_group_id = None
        for index, row in df.iterrows():
            if pd.notna(row['Modifier Group Name']):
                current_modifier_group_id = modifier_group_ids[row['Modifier Group Name']]
            df.at[index, 'Modifier Group ID'] = current_modifier_group_id
            df.at[index, 'Modifier ID'] = modifier_ids[row['Modifier']]
        return df


    excel_file_path = f'{os.getcwd()}/screens/aioconverter/Clover Template.xlsx'  # Update with the path to your Excel file
    sheet_name = 'Modifier Groups'
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')

    modifier_group_ids, modifier_ids = generate_unique_ids(df)

    df = map_ids_to_dataframe(df, modifier_group_ids, modifier_ids)

    output_file_path = 'output_with_ids_1.xlsx'  # Update with the desired output file path
    df.to_excel(output_file_path, index=False)

    global_modifier_group_ids, global_modifier_ids = modifier_group_ids, modifier_ids
    global_modifier_group_ids.update({np.nan: np.nan})

    excel_file_path = 'output_with_ids_1.xlsx'
    sheet_name = 'Sheet1'
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')
    menu_df_output = pd.read_excel('Mijos Menu AIO.xlsx','Modifier ModifierOptions')
    menu_df_output = menu_df_output.reindex(df.index)
    menu_df_output["modifierId"]=df["Modifier Group ID"]
    menu_df_output["modifierOptionId"]=df["Modifier ID"]

    with pd.ExcelWriter('Mijos Menu AIO.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as w:
        menu_df_output.to_excel(w, sheet_name='Modifier ModifierOptions', index=False)


    # input_file_path = 'Clover Template.xlsx'  # Update this to your input file path
    output_file_path = 'output_file_path.xlsx'  # Update this to your desired output file path

    items_df = pd.read_excel(input_file_path, sheet_name='Items')
    modifier_groups_df = pd.read_excel(input_file_path, sheet_name='Modifier Groups')

    items_df['Name'].fillna(method='ffill', inplace=True)

    items_df = items_df.dropna(subset=['Modifier Groups'])

    items_df['Item Id'] = pd.factorize(items_df['Name'])[0] + 1

    modifier_groups_df['Modifier Group Name'] = modifier_groups_df['Modifier Group Name'].fillna(method='ffill')
    unique_modifier_groups = modifier_groups_df['Modifier Group Name'].unique()
    modifier_groups_id_map = {name: i + 1 for i, name in enumerate(unique_modifier_groups)}


    def map_modifier_ids(modifier_names, modifier_map):
        modifier_ids = []
        for name in str(modifier_names).split('; '):
            if name in modifier_map:
                modifier_ids.append(str(modifier_map[name]))
        return '; '.join(modifier_ids)


    items_df['Modifier Group Id'] = items_df['Modifier Groups'].apply(map_modifier_ids, modifier_map=modifier_groups_id_map)

    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        items_df.to_excel(writer, sheet_name='Items', index=False)
        modifier_groups_df.to_excel(writer, sheet_name='Modifier Groups', index=False)


    excel_file_path = 'output_file_path.xlsx'
    sheet_name = 'Items'
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')
    menu_df_output = pd.read_excel('Mijos Menu AIO.xlsx','Item Modifiers')
    menu_df_output = menu_df_output.reindex(df.index)
    menu_df_output["itemId"]=df["Item Id"]
    menu_df_output["modifierId"]=df["Modifier Group Id"]


    with pd.ExcelWriter(f'{os.getcwd()}/screens/aioconverter/Output.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as w:
        menu_df_output.to_excel(w, sheet_name='Item Modifiers', index=False)


    def delete_files():
        file_paths = [
            "output_file_path.xlsx",
            "output_with_ids_1.xlsx"
        ]

        for file_path in file_paths:
            try:
                os.remove(file_path)
                print(f"File '{file_path}' deleted successfully.")
            except OSError as e:
                print(f"Error deleting file '{file_path}': {e}")


    delete_files()


