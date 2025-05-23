import streamlit as st

def _principal():

    st.title("Saudações!")

    # todo arrumar logo principal
    # st.image("assets/logo/logo-farmtech-solutions.png", width=600)

def get_principal_page() -> st.Page:
    """
    Função para retornar a página principal.
    :return: st.Page - A página principal do aplicativo.
    """
    return st.Page(
        _principal,
        title="Principal",
        url_path="/"
    )