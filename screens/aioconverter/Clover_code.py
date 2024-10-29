import pandas as pd
import os
import numpy as np

# def print(*args,**kwargs):
#     return None

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
            # If the file doesn't exist, create a new Excel file
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                dataframe.to_excel(writer, sheet_name=sheetname, index=False)
                # writer.close()
        else:
            with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
                workBook = writer.book
                try:
                    workBook.remove(workBook[sheetname])
                except:
    #                 print("Worksheet does not exist")
                    pass
                finally:
                    dataframe.to_excel(writer, sheet_name=sheetname, index=False)
                    # writer.close()


    def save_all_sheets(file_name, sheets_dict):
        for k in sheets_dict.keys():
            write_excel(file_name, k, sheets_dict[k])





    out_sheets = get_all_sheets(os.getcwd()+'/screens/aioconverter/AIO Template.xlsx')
    inp_sheets = get_all_sheets(input_file_path)



    inp_sheets['Categories'].columns[1:].values



    out_sheets['Category']['categoryName'] = inp_sheets['Categories'].columns[1:].values



    out_sheets['Category']['id'] = range(1, 1+len(out_sheets['Category']))



    mapping_inp = [('Modifier Groups','Modifier'),
                ('Items', 'Name'), ('Items', 'Price'),
                ('Modifier Groups', 'Modifier Group Name'),
                ('Modifier Groups', 'Price')]

    mapping_out = [('Modifier Option', 'optionName'),
                ('Item', 'itemName'),('Item', 'itemPrice'),
                ('Modifier', 'modifierName'),
                ('Modifier Option', 'price')] 



    for i, o in zip(mapping_inp, mapping_out):
        print(i, " -> ", o)



    for m_in, m_out in zip(mapping_inp, mapping_out):
        sheet_name_inp = m_in[0]
        column_name_inp = m_in[1]

        sheet_name_out = m_out[0]
        column_name_out = m_out[1]

        cleaned_values = inp_sheets[sheet_name_inp][column_name_inp].dropna() # Dropping nan values
        # Making sure both dataframs have same length
    #     if len(cleaned_values) > len(out_sheets[sheet_name_out]):
        out_sheets[sheet_name_out] = out_sheets[sheet_name_out].reindex(range(len(cleaned_values)))
    #     else:
    #         cleaned_values = cleaned_values.reindex(range(len(out_sheets[sheet_name_out])))
            

        out_sheets[sheet_name_out][column_name_out] = cleaned_values.values

    #     out_sheets[sheet_name_out]
        out_sheets[sheet_name_out]['id'] = range(1, 1+len(out_sheets[sheet_name_out])) # Setting the ids from 1 to lenght of data
        

    out_sheets['Modifier Option'].drop_duplicates('optionName', inplace=True)
    out_sheets['Modifier Option']['id'] = range(1, 1+len(out_sheets['Modifier Option']))

    save_all_sheets('Output.xlsx', out_sheets)


    # Function to generate unique IDs for Modifier Groups and Modifiers
    def generate_unique_ids(df):
        # Generate unique IDs for Modifier Groups
        modifier_group_ids = {group: i + 1 for i, group in enumerate(df['Modifier Group Name'].dropna().unique())}
        # Generate unique IDs for Modifiers
        modifier_ids = {modifier: i + 1 for i, modifier in enumerate(df['Modifier'].unique())}
        return modifier_group_ids, modifier_ids

    # Function to map Modifier Group IDs and Modifier IDs back to the DataFrame
    def map_ids_to_dataframe(df, modifier_group_ids, modifier_ids):
        current_modifier_group_id = None
        for index, row in df.iterrows():
            if pd.notna(row['Modifier Group Name']):
                current_modifier_group_id = modifier_group_ids[row['Modifier Group Name']]
            df.at[index, 'Modifier Group ID'] = current_modifier_group_id
            df.at[index, 'Modifier ID'] = modifier_ids[row['Modifier']]
        return df

    # Read the Excel file
    excel_file_path = input_file_path  # Update with the path to your Excel file
    sheet_name = 'Modifier Groups'
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')


    # Generate unique IDs
    modifier_group_ids, modifier_ids = generate_unique_ids(df)

    # Map IDs back to the DataFrame
    df = map_ids_to_dataframe(df, modifier_group_ids, modifier_ids)

    # Save the modified DataFrame back to the Excel file
    output_file_path = 'output_with_ids_1.xlsx'  # Update with the desired output file path
    df.to_excel(output_file_path, index=False)

    # Display the first few rows of the modified DataFrame
    # print(df.head())


    global_modifier_group_ids, global_modifier_ids = modifier_group_ids, modifier_ids
    global_modifier_group_ids.update({np.nan: np.nan})



    excel_file_path = 'output_with_ids_1.xlsx'
    sheet_name = 'Sheet1'
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')
    menu_df_output = pd.read_excel('Output.xlsx','Modifier ModifierOptions')
    menu_df_output = menu_df_output.reindex(df.index)
    menu_df_output["modifierId"]=df["Modifier Group ID"]
    menu_df_output["modifierOptionId"]=df["Modifier ID"]



    with pd.ExcelWriter('Output.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as w:
        menu_df_output.to_excel(w, sheet_name='Modifier ModifierOptions', index=False)


    # Define the path to your input and output Excel files

    # input_file_path = input_file_path # Update this to your input file path
    output_file_path = 'output_file_path.xlsx'  # Update this to your desired output file path

    # Load the Excel file
    items_df = pd.read_excel(input_file_path, sheet_name='Items')
    modifier_groups_df = pd.read_excel(input_file_path, sheet_name='Modifier Groups')

    # Fill down 'Name' column in 'Items' to handle empty cells under item names
    items_df['Name'].fillna(method='ffill', inplace=True)

    # Drop rows where 'Modifier Groups' column is empty in 'Items' tab
    items_df = items_df.dropna(subset=['Modifier Groups'])

    # Create unique IDs for Items
    items_df['Item Id'] = pd.factorize(items_df['Name'])[0] + 1

    # Clean the Modifier Groups DataFrame to have one row per modifier group
    modifier_groups_df['Modifier Group Name'] = modifier_groups_df['Modifier Group Name'].fillna(method='ffill')
    unique_modifier_groups = modifier_groups_df['Modifier Group Name'].unique()

    modifier_groups_id_map = {name: i + 1 for i, name in enumerate(unique_modifier_groups)}

    # Map Modifier Group IDs to the 'Items' DataFrame
    def map_modifier_ids(modifier_names, modifier_map):
        modifier_ids = []
        for name in str(modifier_names).split('; '):
            if name in modifier_map:
                modifier_ids.append(str(modifier_map[name]))
        return '; '.join(modifier_ids)

    items_df['Modifier Group Id'] = items_df['Modifier Groups'].apply(map_modifier_ids, modifier_map=modifier_groups_id_map)

    # Write the updated DataFrames to a new Excel file
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        items_df.to_excel(writer, sheet_name='Items', index=False)
        modifier_groups_df.to_excel(writer, sheet_name='Modifier Groups', index=False)

    # print(f"File has been successfully processed and saved as '{output_file_path}'.")


    excel_file_path = 'output_file_path.xlsx'
    sheet_name = 'Items'
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')
    menu_df_output = pd.read_excel('Output.xlsx','Item Modifiers')
    menu_df_output = menu_df_output.reindex(df.index)
    menu_df_output["itemId"]=df["Item Id"]
    menu_df_output["modifierId"]=df["Modifier Group Id"]



    with pd.ExcelWriter('Output.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as w:
        menu_df_output.to_excel(w, sheet_name='Item Modifiers', index=False)



    #import pandas as pd

    # Function to process the Excel file
    def process_excel(file_path, output_file_path):
        # Load the Excel file
        xls = pd.ExcelFile(file_path)

        # Load the "Items" and "Categories" sheets
        items_df = pd.read_excel(xls, 'Items')
        categories_df = pd.read_excel(xls, 'Categories')

        # Dropping empty cells in the "Name" column of the "Items" sheet
        items_df = items_df[items_df['Name'].notna()]

        # Generating item IDs
        items_df['Item ID'] = range(1, len(items_df) + 1)

        # Creating a dictionary of item names and their associated IDs
        item_dict = pd.Series(items_df['Item ID'].values, index=items_df['Name']).to_dict()

        # Processing the "Categories" sheet
        categories = categories_df.columns[1:]  # Skip first column for category names
        category_dict = {category: idx + 1 for idx, category in enumerate(categories)}

        # Mapping items under each category
        category_items_mapping = []
        for category in categories:
            category_id = category_dict[category]
            items_in_category = categories_df[category].dropna().values
            for item in items_in_category:
                if item in item_dict:
                    category_items_mapping.append({'Name': item, 'Category ID': category_id, 'Item ID': item_dict[item]})

        # Convert the mapping to a DataFrame and merge with the original items DataFrame
        mapping_df = pd.DataFrame(category_items_mapping)
        items_df_with_categories = pd.merge(items_df, mapping_df[['Name', 'Category ID']], on='Name', how='left')

        # Re-order the DataFrame
        items_df_with_categories = items_df_with_categories[['Name', 'Category ID', 'Item ID'] + [col for col in items_df_with_categories.columns if col not in ['Name', 'Category ID', 'Item ID']]]

        # Save the updated DataFrame to a new Excel file
        with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
            items_df_with_categories.to_excel(writer, sheet_name='Items', index=False)
            categories_df.to_excel(writer, sheet_name='Categories', index=False)

    # Specify the file paths
    output_file_path = 'Item_Category Mapping.xlsx'  # Update this path

    # Call the function with your file paths
    process_excel(input_file_path, output_file_path)

    def find_best_match_with_total(df1, df2):
        matches = []
        
        for index1, row1 in df1.iterrows():
            max_common_count = 0
            best_match = None
            best_match_modifier = None
            total_options_in_df2 = 0
            
            for index2, row2 in df2.iterrows():
                # Count the common options between the two lists
                common_options = set(row1['Option Name']).intersection(set(row2['Option Name']))

                common_count = len(common_options)
                
                # Get the total number of elements in the second dataframe's option list
                total_options_in_df1 = len(row1['Option Name'])
                
                if common_count > max_common_count:
                    max_common_count = common_count
                    best_match = row2['Option Name']
                    best_match_modifier = row2['Modifier Name']

            if max_common_count>=0.5*total_options_in_df1:
                # Append the results
                matches.append({
                    # 'Item Name (df1)': row1['Item Name'],
                    'Modifier Name Doordash': row1['Modifier Name'],
                    # 'Item Name (df2)': row2['Item Name'],
                    'Modifier Name aio': best_match_modifier,
                    'Common Options': max_common_count,
                    'Total Options (df2)': total_options_in_df1
                })
        
        return pd.DataFrame(matches)


    def add_required_optional(file_path):
        items_df = pd.read_excel(file_path, sheet_name='Item')
        modifiers_df = pd.read_excel(file_path, sheet_name='Modifier')
        options_df = pd.read_excel(file_path, sheet_name='Modifier Option')
        item_modifier_mapping_df = pd.read_excel(file_path, sheet_name='Item Modifiers')
        modifier_option_mapping_df = pd.read_excel(file_path, sheet_name='Modifier ModifierOptions')

        item_modifier = item_modifier_mapping_df.merge(items_df, left_on='itemId', right_on='id', how='left')

        # Step 2: Merge modifier_option_mapping_df with options_df on 'modifierOptionId' and 'id' from the Modifier Option sheet
        modifier_option = modifier_option_mapping_df.merge(options_df, left_on='modifierOptionId', right_on='id', how='left')

        # Step 3: Merge item_modifier with modifiers_df on 'modifierId' and 'id' from the Modifier sheet
        item_modifier = item_modifier.merge(modifiers_df, left_on='modifierId', right_on='id', how='left')

        # Step 4: Merge item_modifier with modifier_option on 'modifierId' to get complete mapping
        final_df = item_modifier.merge(modifier_option, on='modifierId', how='left')

        # Step 5: Rename columns as required
        platform = final_df[['itemName', 'modifierName', 'optionName']]
        platform.columns = ['Item Name', 'Modifier Name', 'Option Name']

        platform_grouped_df = platform.groupby(['Modifier Name'])['Option Name'].apply(list).reset_index()
        
        # doordash
        # 702
        doordash = pd.read_excel(os.getcwd()+"/screens/aioconverter/Mijos Taqueria_.xlsx", sheet_name="modifiers")
        doordash.rename(columns={'item_name': 'Item Name', 'modifier_name': 'Modifier Name',
                                'modifier_type': 'Modifier Type', 'option_name': 'Option Name'}, inplace=True)
        # 80
        doordash = doordash[doordash['Modifier Type'] == 'Required']
        doordash_grouped_df = doordash.groupby(['Modifier Name'])['Option Name'].unique().apply(list).reset_index()

        result_df = find_best_match_with_total(doordash_grouped_df,platform_grouped_df)
        return result_df['Modifier Name aio'].dropna().tolist()


    def migrate_category_items(input_file_path, output_file_path):
        # Load the "Items" tab from the input Excel file
        items_df = pd.read_excel(input_file_path, sheet_name='Items')
        
        # Filter out rows where "Category ID" is empty
        filtered_items_df = items_df.dropna(subset=['Category ID'])
        
        # Prepare the DataFrame for the output file
        category_items_df = filtered_items_df[['Category ID', 'Item ID']].copy()
        category_items_df.rename(columns={'Category ID': 'categoryId', 'Item ID': 'itemId'}, inplace=True)
        
        ## add that required/optitional thing

        modifier_sheet=pd.read_excel(output_file_path,sheet_name='Modifier')
        required_modifiers=add_required_optional(output_file_path)
        
        modifier_sheet.loc[modifier_sheet['modifierName'].isin(required_modifiers), 'isOptional'] = "FALSE"
        
        # Load the output Excel file
        with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Write the DataFrame to the "Category Items" tab in the output Excel file
            modifier_sheet.to_excel(writer, sheet_name='Modifier', index=False)
            category_items_df.to_excel(writer, sheet_name='Category Items', index=False)

        category_items_df = pd.read_excel(output_file_path, sheet_name='Category Items')
        items_df = pd.read_excel(output_file_path, sheet_name='Item')

        # Merge the DataFrames to keep only rows in 'Category Items' that have a match in 'Items'
        merged_df = category_items_df.merge(items_df[['id']], left_on='itemId', right_on='id', how='inner')

        # Drop the 'id' column from the merged DataFrame (since we just needed it for the merge)
        merged_df.drop(columns=['id'], inplace=True)

        # Write the updated Category Items DataFrame back to the file
        with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            merged_df.to_excel(writer, sheet_name='Category Items', index=False)
    # Specify the paths to your input and output Excel files
    input_file_path = 'Item_Category Mapping.xlsx'  # Update this to the path of your input file
    output_file_path = 'Output.xlsx'  # Update this to the path of your output file

    # Call the function with your file paths
    migrate_category_items(input_file_path, output_file_path)

    # Output message to indicate completion
    #print("Category IDs and Item IDs have been migrated to the output file.")

