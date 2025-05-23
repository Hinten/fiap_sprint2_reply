import streamlit as st

from src.dashboard.database.exportar import exportar_db_page
from src.dashboard.database.importar import importar_db_page
from src.dashboard.global_messages import get_global_messages
from src.dashboard.plots.views import grafico_umidade_view, grafico_estado_do_rele, grafico_ph, grafico_fosforo, \
    grafico_potassio, grafico_tudo
from src.dashboard.principal import get_principal_page
from src.dashboard.generic.table_view import TableView
from src.database.dynamic_import import import_models
from src.dashboard.menu import menu


def get_generic_pages() -> list:
    """
    Função para importar dinamicamente os módulos e retornar uma lista de páginas genéricas que fazem o CRUD.
    """

    rotas = []

    models = import_models()


    items = list(models.items())
    items.sort(key=lambda x: x[1].display_name())
    for model_name, model in items:
        view = TableView(model)
        rotas.extend(view.get_routes())
    return rotas

def navigation():
    """
    Função para exibir a página principal do aplicativo.
    :return:
    """

    #todo arrumar logo
    # st.logo("assets/logo/logo-farmtech-solutions-horizontal.png", size='large')

    get_global_messages()
    current_page = st.navigation([
        get_principal_page(),
        *get_generic_pages(),
        grafico_tudo.get_page(),
        grafico_umidade_view.get_page(),
        grafico_estado_do_rele.get_page(),
        grafico_ph.get_page(),
        grafico_fosforo.get_page(),
        grafico_potassio.get_page(),
        exportar_db_page,
        importar_db_page,
    ])

    menu()

    current_page.run()

