import streamlit as st
import os
from ..aioconverter import employee

def show_employee_screen():
    _, column2, _ = st.columns([0.1, 0.8, 0.1])
    with column2:
        st.title('Toast to AIO Converter 🔶')

    if 'uploaded_file_employee' not in st.session_state:
        uploaded_file = st.file_uploader("Choose a file...", type=['csv'])
        if uploaded_file is not None:
            st.session_state['uploaded_file_employee'] = uploaded_file

    if 'uploaded_file_employee' in st.session_state:
        if 'final_employee' not in st.session_state:
            with st.spinner('Converting File...'):
                st.session_state['final_employee'] = employee.run_employee(st.session_state['uploaded_file_employee'])
            st.success('Conversion completed!')

        if 'final_employee' in st.session_state and os.path.exists(st.session_state['final_employee']):
            with open(st.session_state['final_employee'], "rb") as file:
                st.download_button(
                    label="Download Excel file",
                    data=file,
                    file_name="Employee_Campbell.xlsx",
                    mime="application/vnd.ms-excel"
                )
