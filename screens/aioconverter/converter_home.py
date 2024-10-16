import streamlit as st
import os
import zipfile
from ..aioconverter import main
from ..aioconverter import Clover_code
import time,random


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
                print("HERe: ",os.path.exists(st.session_state['final_recipes']),st.session_state['final_recipes'],os.getcwd()+"/"+st.session_state['final_recipes'])
            st.success('Processing complete!')

        if 'final_recipes' in st.session_state and os.path.exists(os.getcwd()+"/"+st.session_state['final_recipes']):
            zip_filename = "Mijos Menu & Recipe.zip"
            create_zip(st.session_state['final_recipes'], f"{os.getcwd()}/Mijos Menu AIO.xlsx", zip_filename)

            with open(zip_filename, "rb") as zip_file:
                st.download_button(
                    label="Download Files",
                    data=zip_file,
                    file_name=zip_filename
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

def create_zip(file1_path, file2_path, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        zip_file.write(file1_path, os.path.basename(file1_path))
        zip_file.write(file2_path, os.path.basename(file2_path))
