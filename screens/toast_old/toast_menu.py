import streamlit as st
import pandas as pd
from screens.utils import load_sheets, read_this
from screens.toast.toast_utils.menu import fill_menu
from screens.fixmissingfield.auto_convert import auto_fix_fields
import io

# Constants for file paths and salary limits
EXCEL_FILE_PATH = "menu_desired_format/menu_desired.xlsx"
SAVE_FILE_PATH = "Menu.xlsx"
SAVE_MISSING_PATH = "Missing_Menu.xlsx"

def process_data():
    """
    Process the uploaded menu data, and update the data in the session state.
    """
    # Read CSV files
    menu_export = st.file_uploader("Upload Menu_Export.csv", type="csv")
    if menu_export is not None:
        st.session_state['menu_export'] = read_this(menu_export)

    menugroup_export = st.file_uploader("Upload MenuGroup_Export.csv", type="csv")
    if menugroup_export is not None:
        st.session_state['menugroup_export'] = read_this(menugroup_export)

    menuitem_export = st.file_uploader("Upload MenuItem_Export.csv", type="csv")
    if menuitem_export is not None:
        st.session_state['menuitem_export'] = read_this(menuitem_export)

    menuoptiongroup_export = st.file_uploader("Upload MenuOptionGroup_Export.csv", type="csv")
    if menuoptiongroup_export is not None:
        st.session_state['menuoptiongroup_export'] = read_this(menuoptiongroup_export)

    menuoption_export = st.file_uploader("Upload MenuOption_Export.csv", type="csv")
    if menuoption_export is not None:
        st.session_state['menuoption_export'] = read_this(menuoption_export)

    itemselectiondetails_export = st.file_uploader("Upload ItemSelectionDetails.csv", type="csv")
    if itemselectiondetails_export is not None:
        st.session_state['itemselectiondetails_export'] = read_this(itemselectiondetails_export)

    itemmodifierselectiondetails_export = st.file_uploader("Upload ItemModifierSelectionDetails.csv", type="csv")
    if itemmodifierselectiondetails_export is not None:
        st.session_state['itemmodifierselectiondetails_export'] = read_this(itemmodifierselectiondetails_export)

    # Ask whether to upload the last two files or not
    upload_last_two = st.radio("Do you want to upload the last two files?", ('Yes', 'No'))

    if upload_last_two == 'Yes':
        onlineitemcategorymapping = st.file_uploader("Online Ordering Item and Category Mapping File", type="csv")
        if onlineitemcategorymapping is not None:
            st.session_state['online_item_category_mapping'] = read_this(onlineitemcategorymapping)

        onlineitemmodifiersmapping = st.file_uploader("Online Ordering Item and Modifiers Mapping File", type="csv")
        if onlineitemmodifiersmapping is not None:
            st.session_state['online_item_modifiers_mapping'] = read_this(onlineitemmodifiersmapping)
    else:
        st.session_state['online_item_category_mapping'] = None
        st.session_state['online_item_modifiers_mapping'] = None

    # Check if all necessary files have been uploaded (excluding the last two if 'No' was selected)
    required_files = [
        'menu_export', 'menugroup_export', 'menuitem_export', 'menuoptiongroup_export',
        'menuoption_export', 'itemselectiondetails_export', 'itemmodifierselectiondetails_export'
    ]

    if all(st.session_state.get(file) is not None for file in required_files):
        print("Filling Menu")
        fill_menu(
            st.session_state['sheets_dict'],
            st.session_state['menu_export'],
            st.session_state['menugroup_export'],
            st.session_state['menuitem_export'],
            st.session_state['menuoptiongroup_export'],
            st.session_state['menuoption_export'],
            st.session_state['itemselectiondetails_export'],
            st.session_state['itemmodifierselectiondetails_export'],
            st.session_state['online_item_category_mapping'],  # May be None
            st.session_state['online_item_modifiers_mapping']   # May be None
        )

        with open(SAVE_FILE_PATH, 'rb') as f:
            data = f.read()
            file_content = io.BytesIO(data)
            dataframes=auto_fix_fields(file_content)
            output = io.BytesIO()

            # Use the buffer as the Excel file
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for key in dataframes.keys():
                    dataframes[key].to_excel(writer, sheet_name=key, index=False)
                
            # Seek to the beginning of the stream
            output.seek(0)

            # Provide the download link
            st.download_button(
                label="Download Final Toast to AIO",
                data=output,
                file_name='Final Toast to AIO.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        st.download_button(
            label="Toast to AIO",
            data=data,
            file_name="Toast to AIO.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        with open(SAVE_MISSING_PATH, 'rb') as f:
            data = f.read()

        st.download_button(
            label="Download the updated Missing Data",
            data=data,
            file_name="Missing_Menu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Config File Updated")


def toast_menu():
    """
    Main function to render the Streamlit app page.
    """
    st.title("Menu Transformation")
    st.write("Upload the Menu CSVs Exported from Toast")

    # Load initial data if not already in session state
    if 'sheets_dict' not in st.session_state:
        st.session_state['sheets_dict'] = load_sheets(EXCEL_FILE_PATH)

    # Initialize CSV file uploads
    if 'menu_export' not in st.session_state:
        st.session_state['menu_export'] = None
    if 'menugroup_export' not in st.session_state:
        st.session_state['menugroup_export'] = None
    if 'menuitem_export' not in st.session_state:
        st.session_state['menuitem_export'] = None
    if 'menuoptiongroup_export' not in st.session_state:
        st.session_state['menuoptiongroup_export'] = None
    if 'menuoption_export' not in st.session_state:
        st.session_state['menuoption_export'] = None
    if 'itemselectiondetails_export' not in st.session_state:
        st.session_state['itemselectiondetails_export'] = None
    if 'itemmodifierselectiondetails_export' not in st.session_state:
        st.session_state['itemmodifierselectiondetails_export'] = None
    if 'online_item_category_mapping' not in st.session_state:
        st.session_state['online_item_category_mapping'] = None
    if 'online_item_modifiers_mapping' not in st.session_state: #this also has modifier, modifier options mapping.
        st.session_state['online_item_modifiers_mapping'] = None

    process_data()
    


# Run the Streamlit app
if __name__ == "__main__":
    toast_menu()
