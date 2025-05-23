import streamlit as st

from src.dashboard.database.exportar import exportar_db_page
from src.dashboard.database.importar import importar_db_page
from src.dashboard.generic.table_view import TableView
from src.dashboard.plots.views import grafico_umidade_view, grafico_estado_do_rele, grafico_ph, grafico_fosforo, \
    grafico_potassio, grafico_tudo
from src.dashboard.principal import get_principal_page
from src.database.dynamic_import import import_models

def crud_menu():
    """
    Função para exibir o menu lateral do aplicativo.
    Cria as páginas de CRUD para os modelos do banco de dados.
    """

    # Importa os modelos do banco de dados

    models = import_models()

    #agrupa os modelos por __menu_group__ e depois ordena por __menu_order__

    groups = list(set(map(lambda x: x[1].__menu_group__, models.items())))
    groups.sort(key=lambda x: (x is None, x))

    for group in groups:
        st.sidebar.header(group or "Cadastro de Outros Modelos")
        group_items = list(filter(lambda x: x[1].__menu_group__ == group, models.items()))
        #orderna os modelos por __menu_order__ e depois por display name
        group_items.sort(key=lambda x: (x[1].__menu_order__, x[1].display_name()))

        for model_name, model in group_items:
            view = TableView(model)
            st.sidebar.page_link(view.get_table_page())

def plot_menu():
    """
    Função para exibir o menu lateral do aplicativo.
    Cria as páginas de gráficos para os modelos do banco de dados.
    """

    st.sidebar.header("Gráficos")
    st.sidebar.page_link(grafico_tudo.get_page())
    st.sidebar.page_link(grafico_umidade_view.get_page())
    st.sidebar.page_link(grafico_estado_do_rele.get_page())
    st.sidebar.page_link(grafico_ph.get_page())
    st.sidebar.page_link(grafico_fosforo.get_page())
    st.sidebar.page_link(grafico_potassio.get_page())


def export_import_menu():
    """
    Função para exibir o menu lateral do aplicativo.
    Cria as páginas de exportação e importação do banco de dados.
    """

    st.sidebar.header("Exportar/Importar")
    st.sidebar.page_link(exportar_db_page)
    st.sidebar.page_link(importar_db_page)

def menu():
    """
    Função para exibir o menu lateral do aplicativo.
    É necessário pois como temos muitas subpáginas que não vão no menu lateral,
    temos que dizer exatamente quais são as páginas que vão no menu lateral.
    """

    st.sidebar.page_link(get_principal_page())
    crud_menu()
    plot_menu()
    export_import_menu()

