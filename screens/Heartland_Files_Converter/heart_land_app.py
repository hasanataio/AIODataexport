import streamlit as st
import pandas as pd
from io import BytesIO

def fun_items_sheet_handler(uploaded_file):
    items_sheet_df = pd.read_excel(uploaded_file, sheet_name='Items')
    items_sheet_df = items_sheet_df.dropna(how='all')
    items_sheet_df['id'] = range(1, len(items_sheet_df) + 1)
    final_aio_df = items_sheet_df[['id', 'name', 'description', 'price']].copy()
    final_aio_df = final_aio_df.rename(columns={'name': 'itemName', 'description': 'itemDescription', 'price': 'itemPrice'})
    return final_aio_df

def fun_sections_sheet_handler(uploaded_file):
    sections_sheet_df = pd.read_excel(uploaded_file, sheet_name='Sections')
    sections_sheet_df = sections_sheet_df.dropna(how='all')
    sections_sheet_df['id'] = range(1, len(sections_sheet_df) + 1)
    final_aio_df = sections_sheet_df[['id', 'name']].copy()
    final_aio_df.rename(columns={'name': 'categoryName'}, inplace=True)
    return final_aio_df

def fun_groups_sheet_handler(uploaded_file):
    groups_sheet_df = pd.read_excel(uploaded_file, sheet_name='Groups')
    groups_sheet_df = groups_sheet_df.dropna(how='all')
    groups_sheet_df['id'] = range(1, len(groups_sheet_df) + 1)
    final_aio_df = groups_sheet_df[['id', 'name']].copy()
    final_aio_df.rename(columns={'name': 'menuName'}, inplace=True)
    return final_aio_df

def fun_modifiers_sheet_handler(uploaded_file):
    groups_sheet_df = pd.read_excel(uploaded_file, sheet_name='Modifiers')
    groups_sheet_df = groups_sheet_df.dropna(how='all')
    groups_sheet_df['id'] = range(1, len(groups_sheet_df) + 1)
    final_aio_df = groups_sheet_df[['id', 'name']].copy()
    final_aio_df.rename(columns={'name': 'modifierName'}, inplace=True)
    return final_aio_df

def fun_ingredients_sheet_handler(uploaded_file):
    ingredients_sheet_df = pd.read_excel(uploaded_file, sheet_name='Ingredients')
    ingredients_sheet_df = ingredients_sheet_df.dropna(how='all')
    ingredients_sheet_df['id'] = range(1, len(ingredients_sheet_df) + 1)
    final_aio_df = ingredients_sheet_df[['id', 'name']].copy()
    final_aio_df.rename(columns={'name': 'optionName'}, inplace=True)
    return final_aio_df

def process_file(uploaded_file):
    items_df = fun_items_sheet_handler(uploaded_file)
    sections_df = fun_sections_sheet_handler(uploaded_file)
    groups_df = fun_groups_sheet_handler(uploaded_file)
    modifiers_df = fun_modifiers_sheet_handler(uploaded_file)
    options_df = fun_ingredients_sheet_handler(uploaded_file)
    
    # Create an Excel writer for output
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        items_df.to_excel(writer, sheet_name='item', index=False)
        sections_df.to_excel(writer, sheet_name='Category', index=False)
        groups_df.to_excel(writer, sheet_name='Menu', index=False)
        modifiers_df.to_excel(writer, sheet_name='Modifier', index=False)
        options_df.to_excel(writer, sheet_name='Modifier option', index=False)

    output.seek(0)
    return output

def heart_land_main():
    st.title("Heartland Processor")
    st.write("Upload an Excel file, process the data, and download the result.")
    
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
    
    if uploaded_file:
        st.success("File uploaded successfully")
        processed_file = process_file(uploaded_file)
        
        st.download_button(
            label="Download processed file",
            data=processed_file,
            file_name="processed_heartland_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

