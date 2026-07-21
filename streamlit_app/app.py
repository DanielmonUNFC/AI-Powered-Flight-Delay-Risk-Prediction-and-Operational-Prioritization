import streamlit as st

from pages.overview import render_overview


st.set_page_config(
    page_title="AEROINTEL",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():

    render_overview()


if __name__ == "__main__":
    main()