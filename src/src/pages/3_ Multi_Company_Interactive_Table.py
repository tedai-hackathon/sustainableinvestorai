# Interactive Table Comparison

import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))


import streamlit as st
import pandas as pd 
import numpy as np 
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


st.set_page_config(page_title="Multiple Company Interactive Table", 
                   page_icon=":bar_chart:", 
                   layout="centered", 
                   initial_sidebar_state="collapsed")

st.title(":chart_with_upwards_trend: Sustainability Metrics Comparisons")
st.info(""" The table below reports the carbon footprint metrics of companies in the oil and gas industry.
Please select the companies you would like to compare from the table below.""")

data = pd.read_csv("data/GHG.csv")

mean_values = data[['Scope1','Scope2','Scope3']].mean()

# Sample data
#data = {
    #'Company': ['Company A', 'Company B', 'Company C', 'Company D'],
    #'Carbon Footprint': [50, 60, 70, 80],
    #'Gas Emission': [20, 30, 40, 50],
#}

#data = pd.DataFrame(data)

gb = GridOptionsBuilder.from_dataframe(data)
gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
gb.configure_side_bar() #Add a sidebar
gb.configure_selection('multiple', rowMultiSelectWithClick = True, 
                     use_checkbox=True, groupSelectsChildren=True) #Enable multi-row selection

gridOptions = gb.build()

grid_response = AgGrid(
    data,
    gridOptions=gridOptions,
    data_return_mode='AS_INPUT',
    update_mode='MODEL_CHANGED',
    fit_columns_on_grid_load=False,
    enable_enterprise_modules=True,
    height=250,
    width='100%')

try:
    data = grid_response['data']
    selected = grid_response['selected_rows'] 
    df = pd.DataFrame(selected)
    
    dev = df[['Scope1','Scope2','Scope3']] - mean_values
    new_df = pd.concat([df['Company'], dev], axis=1)
    # Display the table
    st.dataframe(new_df)
except KeyError:
    st.write("Please make a selection from the table above.")
