import logging
import os
import streamlit as st
from src.wokwi_api.api_basica import inciar_api_thread_paralelo

def iniciar_api_sensor():

    if os.environ.get("ENABLE_API", "false").lower() != "true":
        print("API Sensor não está habilitada. Verifique a variável de ambiente ENABLE_API.")
        return

    if not st.session_state.get('api_sensor', False):
        logging.info("Iniciando API Sensor em uma thread separada.")
        inciar_api_thread_paralelo()
        st.session_state['api_sensor'] = True
        logging.info("API Sensor iniciada com sucesso.")
        st.toast("API Sensor iniciada com sucesso.")
