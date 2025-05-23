import streamlit as st

@st.fragment
def get_global_messages():
    """
    Função para obter mensagens globais do Streamlit.
    Utiliza o st.fragment para ele não dar rerun no app inteiro quando solicitado
    """

    if st.session_state.get('global_messages') is not None:
        with st.container():
            col1, col2 = st.columns([10, 1])
            with col1:
                st.write(st.session_state.get('global_messages', ''))
            with col2:
                if st.button("❌", key="close_button"):
                    st.session_state['global_messages'] = None
                    st.rerun()

def add_global_message(message:str):
    st.session_state['global_messages'] = message
