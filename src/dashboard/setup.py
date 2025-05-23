import logging
from src.database.generator.criar_sensores import criar_sensores_padrao
from src.database.tipos_base.database import Database
import streamlit as st

def setup():

    Database.init_from_session(st.session_state.get('engine'), st.session_state.get('session'))

    if not st.session_state.get('init_tables', False):
        logging.info("Criando tabelas...")
        st.info("Criando tabelas...")
        Database.create_all_tables()
        st.session_state['init_tables'] = True
        logging.info("Tabelas criadas com sucesso.")
        st.success("Tabelas criadas com sucesso.")
        # criar_sensores_padrao(plantio_id=1)
