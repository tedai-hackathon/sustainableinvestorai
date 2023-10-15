# Single Company Analysis File

import markdown
import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Single Company Analysis", 
                   page_icon=":bar_chart:", 
                   layout="wide", 
                   initial_sidebar_state="collapsed")

st.title(":chart_with_upwards_trend: Sustainability Report Analysis")
st.info("""
        Please select a sector down below and click the 'Submit' button. Then, choose a company you want to investigate and click 'Investigate.' Allow a few minutes while the system processes the sustainability report of the company.
        You will see a short summary of the company's sustainability report, a score that indicates the degree of greenwashing based on the industry standards, and an opportunity to analyze the sustainability report further with questions.
""")


from src.my_main_backend import MainBackend
from src.sectors import Sector
from src.callbacks import *
from src.companydata import company_data

import csv
import json
import os


def main():

    with st.sidebar:
        api_key = st.text_input("API Key", key="openai_api_key_widget", type="password")

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
            selected_company = st.radio("### **Select companies to investigate:**", [company for company in Sector[st.session_state.selected_sector].value], key="selected_company")
            st.button(label="Investigate!", on_click=click_company_submit)

    if st.session_state.company_submit:

        if not os.environ["ANTHROPIC_API_KEY"]:
            st.info("Please add your API key to continue.")
        elif selected_company is not None:
            #report_folder_path = f"./reports/{selected_company}/"
            #report_path = os.path.join(report_folder_path, os.listdir(report_folder_path)[0])
            report_path = f"./reports/{selected_company}/{selected_company}.pdf"
            with st.status("**Generating Insights...**"):
                # Company Overview
                overview = backend.pull_company_overview(selected_company)
                st.write(f"Gathering {selected_company}'s company information")
                # Report summarization 
                summarising_question = "Please summarize the article"
                response_dict = backend.generate_response_for_user_question(report_path, summarising_question,selected_company)
                st.write(f"📝 Summarising {selected_company}'s sustainability report")
            
            col1, col2 = st.columns([2,1])
            with col1:
                st.write(f"### Company Overview of {selected_company}")
                st.write(overview)
            with col2:
                st.write(f"### Breaking News About {selected_company}")
                titles, sentiments, sources, urls,times = backend.pull_company_news(selected_company)
                for i in range(0,len(titles)):
                    news_title = titles[i]
                    news_url = urls[i]
                    st.write(f"""
                            [{news_title}]({news_url})
                             """)
                    col1, col2, col3 = st.columns([1,1,1])
                    with col1:
                        st.write(sentiments[i])
                    with col2:
                        time =times[i]
                        date = time[:8]
                        date_obj = datetime.strptime(date, "%Y%m%d")
                        formatted_date = date_obj.strftime("%m/%d/%Y")
                        st.write(formatted_date) 
                    with col3:
                        st.write(sources[i])

            st.write(f"### Summary of {selected_company}'s Sustainability Report")
            st.write(response_dict["ANSWER"])

            with st.status("**Generating Insights...**"):
                # Calculate Trustability Score
                st.write(f"Calculating the trustability score of {selected_company}'s sustainability report")
                trustability_score = backend.get_trustability_score(report_path,selected_company)

            if trustability_score < 2.5:
                condition = f"Trustability Score: :red[{trustability_score:.2f}/5]"
            else:
                condition = f"Trustability Score: :green[{trustability_score:.2f}/5]"

            with st.expander(condition):
                st.write("""
                         The Trustability Score is a measure of the reliability of the sustainability reporting by a company. 
                         On a scale of 1-5, 5 indicates that the reporting is reliable & 1 indicates that the reporting is unreliable. 
                         We measure this by checking whether the sustainibility reporting adheres to International Standards like the 
                         Sustainability Disclosure Standards by SASB.
                         """)

            st.write(f"### Analyze {selected_company} further!")

            # Obtain list of suggested questions from CSV
            csv_path = "./standards/cuedquestions.csv"
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

            if st.session_state.q:
                response_dict = backend.generate_response_for_user_question(report_path, st.session_state.q,selected_company)
                st.write("### ✏️ Answer")
                col1, buf, col2 = st.columns([10, 0.5, 3])
                col1.write(response_dict["ANSWER"])
                col2.info(f"""
                Trustability Score: {trustability_score:.2f}/5\n
                [{selected_company}'s Sustainability Report](about:blank)\n
                """)

                st.write("**Not confident of the answer?**")
                if st.checkbox(label="**Examine the relevant excerpts from the report!**"):
                    quoted_excerpts = ['"' + excerpt + '"' for excerpt in response_dict["EXCERPT"]]
                    markdown_text = "\n".join(f"* {item}" for item in quoted_excerpts)
                    markdown_html = markdown.markdown(markdown_text)
                    st.markdown(f"<div style='font-family: Courier New;'>{markdown_html}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    os.environ["ANTHROPIC_API_KEY"] = "ANTHROPIC_KEY_HERE"
    MODEL_NAME = "text-ada-001"
    main()


        