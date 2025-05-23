import logging
from src.database.tipos_base.database import Database, DEFAULT_DSN
import streamlit as st


def cached_login(username, password, dsn):
    """
    Função para armazenar em cache as credenciais de login.
    :param username: Nome de usuário.
    :param password: Senha.
    :param dsn: DSN do banco de dados.
    :return:
    """

    if not st.session_state.get('logged_in', False):
        Database.init_oracledb(username, password, dsn)
        logging.info("Conexão bem-sucedida ao banco de dados Oracle!")
        st.session_state.logged_in = True
        st.session_state.engine = Database.engine
        st.session_state.session = Database.session


def login_view():
    #título

    st.title("Farm Tech Solutions")

    st.subheader("Login")

    # Cria um formulário de login

    with st.form(key='login_form'):
        dsn = st.text_input("DSN", value=DEFAULT_DSN)
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button(label='Entrar')

        if submit_button:

            if not username or not password:
                st.error("Por favor, preencha todos os campos.")
                return

            try:
                cached_login(username, password, dsn)
                st.success("Conexão bem-sucedida ao banco de dados Oracle!")
                st.rerun()
            except Exception as e:
                logging.error(f"Erro ao conectar ao banco de dados: {e}")
                st.error(f"Erro ao conectar ao banco de dados: {e}")