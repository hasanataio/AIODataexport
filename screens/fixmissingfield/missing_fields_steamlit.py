import streamlit as st
import pandas as pd
from .MissingFieldsFix import fix_missing_fields
import io
import os


def run_fix_missing_fields():
    st.write()
    col1,col2,col3=st.columns(3)
    with col2:
        st.image(f'{os.getcwd()}/screens/fixmissingfield/logo.png',width=300)


    st.title("Upload a file to fix missing fields 📑")

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        try:
            dataframes=fix_missing_fields(uploaded_file)
            output = io.BytesIO()

            # Use the buffer as the Excel file
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for key in dataframes.keys():
                    dataframes[key].to_excel(writer, sheet_name=key, index=False)
                
            # Seek to the beginning of the stream
            output.seek(0)

            # Provide the download link
            st.download_button(
                label="Download Excel file",
                data=output,
                file_name='missing_fields_fix.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            st.write("Error Occured: ",e)
    