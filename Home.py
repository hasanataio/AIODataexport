import streamlit as st
from screens.toast.toast_employee import toast_emp
from screens.toast.toast_menu import toast_menu
from screens.square.square_employee import square_emp
from screens.clover.clover_employee import clover_emp
from screens.fixmissingfield.missing_fields_steamlit import run_fix_missing_fields
from screens.aioconverter.employee_home import show_employee_screen
from screens.aioconverter.converter_home import show_home_screen
from screens.Heartland_Files_Converter.heart_land_app import heart_land_main
from screens.square_file_converter.square_app import square_main

# CSS styles
css = """
<style>
    .sidebar .sidebar-content {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
        background-color: #2c3e50;
        padding: 12px;
        border-radius: 12px;
    }

    .sidebar .sidebar-content:hover {
        background-color: #34495e;
        cursor: pointer;
    }

    .stButton button {
        font-size: 20px;
        padding: 10px 20px;
        background-color: #2c3e50;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }

    .stButton button:hover {
        background-color: #34495e;
    }
</style>
"""

# Home page function


def home():
    st.title("Data Transformation & Automation to AIO format")
    st.write("Auto-fill Employee and Menu Details in AIO's Desired Config Files")

# Function to set the page


def set_page(page):
    st.session_state.page = page


if __name__ == "__main__":
    # Add CSS styles to the Streamlit app
    st.markdown(css, unsafe_allow_html=True)

    # Initialize session state for the page
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    # Set the sidebar title
    st.sidebar.markdown(
        "<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)

    # Sidebar layout
    with st.sidebar:
        if st.button("🏠 Home", use_container_width=True):
            set_page('home')

        if st.button("🏠 Missing Fields Fix", use_container_width=True):
            set_page('missing_fields')

        employee_expander = st.expander("‍💼 Employee")
        with employee_expander:
            if st.button("‍💼 Toast Employee", use_container_width=True):
                set_page('toast_employee')
            if st.button("🔲 Square Employee", use_container_width=True):
                set_page('square_employee')
            if st.button("☘️ Clover Employee", use_container_width=True):
                set_page('clover_employee')

        menu_expander = st.expander("🍞 Menu")
        with menu_expander:
            if st.button("🍞 Toast Menu", use_container_width=True):
                set_page('toast_menu')
            if st.button("🏠 Clover Menu", use_container_width=True):
                set_page('converter_home')
            if st.button("🏠 Heartland Menu", use_container_width=True):
                set_page('heartland_home')
            if st.button("🏠 Square Menu", use_container_width=True):
                set_page('square_home')
        
        upload_to_aio_expander=st.expander("Upload to AIO")
        with upload_to_aio_expander:
            st.link_button("Stage V2", "https://stagev2-backend.dev.aioapp.com/api-docs",use_container_width=True)
            st.link_button("UAT V2", "https://uatv2-backend.dev.aioapp.com/api-docs/",use_container_width=True)
        

                

            # if st.button("📝 Employees", use_container_width=True):
            #     set_page('employee_home')

    # Render the selected page
    if st.session_state.page == 'home':
        home()
    elif st.session_state.page == 'toast_employee':
        toast_emp()
    elif st.session_state.page == 'square_employee':
        square_emp()
    elif st.session_state.page == 'clover_employee':
        clover_emp()
    elif st.session_state.page == 'missing_fields':
        run_fix_missing_fields()
    elif st.session_state.page == 'toast_menu':
        toast_menu()
    elif st.session_state.page == 'converter_home':
        show_home_screen()
    elif st.session_state.page == 'employee_home':
        show_employee_screen()
    elif st.session_state.page == 'heartland_home':
        heart_land_main()
    elif st.session_state.page == 'square_home':
        square_main()
        
    