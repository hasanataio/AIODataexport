import streamlit as st
import pandas as pd
import main
import os
import zipfile

import time,random
import base64
import Clover_code
import employee
# def add_bg_from_local():
#     with open("background.jpg", "rb") as file:
#         base64_img = base64.b64encode(file.read()).decode('utf-8')
#     st.markdown(
#         f"""
#         <style>
#         .stApp {{
#             background-image: url("data:image/jpg;base64,{base64_img}");
#             background-size: cover;
#             background-position: center;
#             background-image: linear-gradient(to top, rgba(255,255,255,0), rgba(255,255,255,1)), url("data:image/jpg;base64,{base64_img}");
   
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True
#     )


# add_bg_from_local()

st.set_page_config(page_title="AIO App")

col1,col2,col3=st.columns(3)
with col2:
    st.image('logo.png',width=300)


def create_sidebar():
    
    with st.sidebar:
        
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                font-size: 26px;   /* Large font size */
                height: 3em;       /* Taller button */
                width: 10em;       /* Wider button */
                margin: 10px;      /* Space around the button */
            }
            </style>""", unsafe_allow_html=True)

        # Each button with an emoji as an icon
        home = st.button("🏠 Menu And Recipe", key="home")
        employees_btn = st.button("📝 Employees", key="reviews")
        return home, employees_btn



st.sidebar.markdown("""
    <style>
        .css-1y0tads {justify-content: center;}
    </style>
    <h1 style='text-align: center;'>Navigation</h1>
    """, unsafe_allow_html=True)

def create_zip(file1_path, file2_path, zip_filename):

  with zipfile.ZipFile(zip_filename, 'w') as zip_file:
    zip_file.write(file1_path, os.path.basename(file1_path))  # Include filename
    zip_file.write(file2_path, os.path.basename(file2_path))

# Display the selected section

home_clicked, employees_btn=create_sidebar()

if home_clicked:
    st.session_state['active_section'] = 'Home'

if employees_btn:
    st.session_state['active_section'] = 'employee'



if 'active_section' not in st.session_state:
    st.session_state['active_section'] = 'Home'


if st.session_state['active_section'] == 'Home':
    _,column2,_=st.columns([0.1,0.8,0.1])
    with column2:
        st.title('Clover to AIO Converter 📁')

    # File uploader allows user to add file

    if 'uploaded_file' not in st.session_state:
        # Use a file uploader and save the file in session state
        uploaded_file = st.file_uploader("Choose a file...", type=['xlsx'])
        if uploaded_file is not None:
            st.session_state['uploaded_file'] = uploaded_file
        
    if 'uploaded_file' in st.session_state:
        # File is in session state, process the file
        if 'final_recipes' not in st.session_state:
            with st.spinner('Converting Template...'):
                Clover_code.run_first_step(st.session_state['uploaded_file'])
            with st.spinner('Generating Recipes...'):
                st.session_state['final_recipes'] =main.run_recipes_on_clover('Mijos Menu AIO.xlsx')
            # Message and spinner will automatically disappear once the function execution completes
            st.success('Processing complete!')

        # Check if the file has been processed and exists
        if 'final_recipes' in st.session_state and os.path.exists(st.session_state['final_recipes']):
            # File exists, create a download button
            zip_filename = "Mijos Menu & Recipe.zip"
            create_zip(st.session_state['final_recipes'], "Mijos Menu AIO.xlsx", zip_filename)  # Generate the zip

            # Now use st.download_button with the zip file:
            with open(zip_filename, "rb") as zip_file:
                st.download_button(
                    label="Download Files",
                    data=zip_file,
                    file_name=zip_filename
                )
                if st.button('Upload to AIO Dashboard'):
                    # Display a progress bar
                    progress = st.progress(0)
                    current_progress = 0
                    while current_progress < 100:
                        # Calculate random increase
                        increment = random.randint(1, 10)  # Adjust the range as needed
                        current_progress += increment
                        # Ensure the progress does not exceed 100%
                        current_progress = min(current_progress, 100)
                        progress.progress(current_progress)
                        time.sleep(0.1)  # Add a small delay to make updates visible
                    
                    # Display success message once the loop is complete
                    st.success('Uploaded successfully!')
                    url = 'https://stagev2-dashboard.dev.aioapp.com/'
                    link_text = 'Go To Dashboard'

                    view_Online = 'View Online'
                    view_online_url = 'https://uatv2-portal.dev.aioapp.com/online-ordering/4'
                    # Display the link
                    st.markdown(
                        f'<a href="{url}" target="_blank">{link_text}</a>'
                        f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                        f'<a href="{view_online_url}" target="_blank">{view_Online}</a>',
                        unsafe_allow_html=True
                    )
            # with open(st.session_state['final_recipes'], "rb") as file:
                


if st.session_state['active_section'] == 'employee':
    _,column2,_=st.columns([0.1,0.8,0.1])
    with column2:
        st.title('Toast to AIO Converter 🔶')

    # File uploader allows user to add file

    if 'uploaded_file_employee' not in st.session_state:
        # Use a file uploader and save the file in session state
        uploaded_file = st.file_uploader("Choose a file...", type=['csv'])
        if uploaded_file is not None:
            st.session_state['uploaded_file_employee'] = uploaded_file

    if 'uploaded_file_employee' in st.session_state:
        # File is in session state, process the file
        if 'final_employee' not in st.session_state:
            with st.spinner('Converting File...'):
                st.session_state['final_employee']=employee.run_employee(st.session_state['uploaded_file_employee'])
                
            st.success('Conversion completed!')

        # Check if the file has been processed and exists
        if 'final_employee' in st.session_state and os.path.exists(st.session_state['final_employee']):
            # File exists, create a download button
            with open(st.session_state['final_employee'], "rb") as file:
                st.download_button(
                    label="Download Excel file",
                    data=file,
                    file_name="Employee_Campbell.xlsx",
                    mime="application/vnd.ms-excel"
                )
                





