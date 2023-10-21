import streamlit as st


def reset_session_state():
    for key in st.session_state:
        del st.session_state[key]


def click_sector_submit():
    st.session_state.sector_submit = not st.session_state.sector_submit


def click_company_submit():
    st.session_state.company_submit = not st.session_state.company_submit

def fill_suggested_question():
    st.session_state.q = st.session_state.selected_question_sus

def fill_suggested_question_fin():
    st.session_state.q_fin = st.session_state.selected_question_fin

def fill_chosen_question():
    st.session_state.qu = st.session_state.chosen_question