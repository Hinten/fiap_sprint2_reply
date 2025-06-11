import streamlit as st
from src.dashboard.plots.analise_exploratoria import analise_exploratoria_view


def _principal():

    analise_exploratoria_view()

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