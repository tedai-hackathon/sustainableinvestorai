# Multiple Company Analysis
# This is the page where RAG happens 
import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

import streamlit as st
import os
import warnings

from langchain import OpenAI
from dotenv import load_dotenv

from src.sectors import Sector
from src.rag_backend import RAGBackend
import csv

from src.callbacks import *

## Set API Keys 

load_dotenv()

## Ignore langchain import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

openai_api_key = os.environ.get("OPENAI_API_KEY")
llm = OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=-1)

st.set_page_config(page_title="Multi-Company Sustainability Report Comparison", 
                   page_icon=":bar_chart:", 
                   layout="centered", 
                   initial_sidebar_state="collapsed")

st.title(":chart_with_upwards_trend: Sustainability Report Comparison")
st.info("""
Please select a sector down below and then select companies you want to compare from the drop-down menu. 
        Type in your question and click "Ask" button.""")


def get_rag_backend():
    return RAGBackend()

rag_backend = get_rag_backend()


st.write("##### Select the sectors across which you want to compare companies.")

columns = st.columns(len(Sector))
all_selected_companies = []
for sector, col in zip(Sector, columns):
    if col.checkbox(f"**{sector.name}**"):
        selected_companies = col.multiselect(f"**Select {sector.name.lower()} companies:**", sector.value)
        all_selected_companies.extend(selected_companies)

if len(all_selected_companies) < 2:
    st.error("Please select at least two companies to compare.")
else:
    # col1, col2 = st.columns([90, 10])
    # Obtain cued questions for multicompany analysis
    csv_path = "./standards/cuedquestionsmulticomp.csv"
    file_obj = open(csv_path, 'r')
    reader = csv.reader(file_obj)
    suggested_questions = []
    for item in reader:
        if reader.line_num == 1:  # skipping the header
            continue
        suggested_questions.append(item[0])
    st.radio(label="Suggested Questions", options=suggested_questions, key="selected_question")
    st.button(label="Use question", on_click=fill_suggested_question)
    st.text_input(label="question", label_visibility="hidden", placeholder="Ask a question...", key="q")
    #question = col1.text_input("##### What do you want to compare across these companies?")
    #col2.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.q:
        st.write("Please wait while we process your question...")
        answer = rag_backend.ask_question(st.session_state.q, all_selected_companies)
        st.write(answer)
