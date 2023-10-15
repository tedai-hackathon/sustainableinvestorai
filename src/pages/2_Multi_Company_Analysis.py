# Multiple Company Analysis
# This is the page where RAG happens 
import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))


import streamlit as st
import os 
from os.path import join
import warnings

st.set_page_config(page_title="Multi-Company Sustainability Report Comparison", 
                   page_icon=":bar_chart:", 
                   layout="centered", 
                   initial_sidebar_state="collapsed")

st.title(":chart_with_upwards_trend: Sustainability Report Comparison")
st.info("""
INSTRUCTIONS
""")


from src.my_main_backend import MainBackend
from src.sectors import Sector
from src.callbacks import *
from src.companydata import company_data

def main(): 

    backend = MainBackend()

    # st.info(st.session_state)
    col1, buff, col2 = st.columns([10, 0.5, 3])
    # File-upload box for a sustainability report
    col1.title("💹 Sustainable Investor AI!")
    col2.button(label="Reset!", on_click=reset_session_state)

    if 'sector_submit' not in st.session_state:
        st.session_state.sector_submit = False

    st.radio("### **Select sector to investigate:**", [sector.name for sector in Sector], key="selected_sector")
    st.button(label="Submit", on_click=click_sector_submit)

    if 'company_submit' not in st.session_state:
        st.session_state.company_submit = False

    if 'excerpt_visible' not in st.session_state:
        st.session_state.excerpt_visible = False

    selected_company = None
    # Select Company to Investigate
    if st.session_state.sector_submit:
        if 'selected_sector' not in st.session_state:
            st.write("Please select from above the sectors you want to explore.")
        else:
            selected_companies = st.multiselect("### **Select companies to investigate:**", [company for company in Sector[st.session_state.selected_sector].value], key="selected_companies")
            st.button(label="Investigate!", on_click=click_company_submit)

    if st.session_state.company_submit:

        if selected_company is not None:
            dir_path = "reports/"
            sh_uploaded_file_path = join(dir_path,"SHELL","shell-sr-2022.pdf")
            bp_uploaded_file_path = join(dir_path,"BP","bp-sr-2022.pdf")


