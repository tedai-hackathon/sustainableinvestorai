import os

import streamlit as st
from my_main_backend import MainBackend
from sectors import Sector
from callbacks import *

import csv
import json


def main():

    with st.sidebar:
        api_key = st.text_input("API Key", key="openai_api_key_widget", type="password")

    backend = MainBackend()

    # st.info(st.session_state)
    col1, buff, col2 = st.columns([10, 0.5, 3])
    # File-upload box for a sustainability report
    col1.title("💹 Welcome to Sustainable Investor AI!")
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
                summarising_question = "Please summarize the article"
                summary_response = backend.generate_response_for_user_question(report_path, summarising_question,selected_company)
                st.write(f"#### 📝 Summarising {selected_company}'s sustainability report")
                summary_json = json.loads(summary_response.split("\n\n")[1])
                st.write(summary_json["ANSWER"])

                st.write(f"### Calculating the trustability score of {selected_company}'s sustainability report")
                trustability_score = backend.get_trustability_score(report_path)
                st.info(f"""
                        Trustability Score: {trustability_score:.2f}/5
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
                response = backend.generate_response_for_user_question(report_path, st.session_state.q)
                st.write("### ✏️ Answer")
                response_dict = json.loads(response.split("\n\n")[1])
                col1, buf, col2 = st.columns([10, 0.5, 3])
                col1.write(response_dict["ANSWER"])
                col2.info(f"""
                Trustability Score: {trustability_score:.2f}/5\n
                [Abbott Sustainability Report](about:blank)\n
                """)

                #import pdb; pdb.set_trace()
                #st.checkbox(label="Not confident of the answer? Examine the relevant excerpts from the report", on_change=click_read_excerpts)
                #if st.session_state.excerpt_visible:
                st.write("**Not confident of the answer? Examine the relevant excerpts from the report below:**")
                st.write(response_dict["EXCERPT"])


if __name__ == "__main__":
    os.environ["ANTHROPIC_API_KEY"] = "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"
    MODEL_NAME = "text-ada-001"
    main()
