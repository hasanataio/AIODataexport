import streamlit as st
import os
import zipfile
from ..aioconverter import main
from ..aioconverter import Clover_code
import time,random,io
from screens.fixmissingfield.auto_convert import auto_fix_fields
import pandas as pd

def show_home_screen():
    _, column2, _ = st.columns([0.1, 0.8, 0.1])
    with column2:
        st.title('Clover to AIO Converter 📁')

    if 'uploaded_file' not in st.session_state:
        uploaded_file = st.file_uploader("Choose a file...", type=['xlsx'])
        if uploaded_file is not None:
            st.session_state['uploaded_file'] = uploaded_file

    if 'uploaded_file' in st.session_state:
        if 'final_recipes' not in st.session_state:
            with st.spinner('Converting Template...'):
                Clover_code.run_first_step(st.session_state['uploaded_file'])
            with st.spinner('Generating Recipes...'):
                st.session_state['final_recipes'] = main.run_recipes_on_clover('Mijos Menu AIO.xlsx')
                print("HERe: ", os.path.exists(st.session_state['final_recipes']),
                      st.session_state['final_recipes'], os.getcwd() + "/" + st.session_state['final_recipes'])
            st.success('Processing complete!')

        if 'final_recipes' in st.session_state and os.path.exists(os.getcwd() + "/" + st.session_state['final_recipes']):
            # Define the paths to the generated files
            final_recipes_path = os.path.join(os.getcwd(), st.session_state['final_recipes'])
            aio_template_path = os.path.join(os.getcwd(), "Mijos Menu AIO.xlsx")

            # Create a download button for the first file (Recipes)
            with open(final_recipes_path, "rb") as file1:
                st.download_button(
                    label="Download Recipes",
                    data=file1,
                    file_name=os.path.basename(final_recipes_path)
                )

            # Create a download button for the second file (AIO Template)
            dataframes=None
            with open(aio_template_path, "rb") as file2:
                file_content = io.BytesIO(file2.read()) 
                dataframes=auto_fix_fields(file_content)


                st.download_button(
                    label="Download AIO Template",
                    data=file2,
                    file_name=os.path.basename(aio_template_path)
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
                label="Download Missing Fields Fixed File",
                data=output,
                file_name='missing_fields_fix.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            if st.button('Upload to AIO Dashboard'):
                progress = st.progress(0)
                current_progress = 0
                while current_progress < 100:
                    increment = random.randint(1, 10)
                    current_progress += increment
                    current_progress = min(current_progress, 100)
                    progress.progress(current_progress)
                    time.sleep(0.1)
                
                st.success('Uploaded successfully!')
                st.markdown(
                    '<a href="https://stagev2-dashboard.dev.aioapp.com/" target="_blank">Go To Dashboard</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                    '<a href="https://uatv2-portal.dev.aioapp.com/online-ordering/4" target="_blank">View Online</a>',
                    unsafe_allow_html=True
                )