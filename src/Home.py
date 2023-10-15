## Home page of the website 

import sys
from pathlib import Path

# Setting parent directories 
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

import streamlit as st

st.set_page_config(page_title="Sustainable Investor", 
                   page_icon="💹",
                   layout="centered")

st.title("💹 Welcome to Sustainable Investor \n\n **Empowering Sustainability Investments, One Click at a Time**")