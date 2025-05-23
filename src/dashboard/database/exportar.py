import streamlit as st
from src.database.export_import_db import create_database_zip_export

def exportar_database():

    st.title("Exportar Banco de Dados")
    # Botão para iniciar o processo de exportação
    if st.button("Gerar Exportação do Banco de Dados"):
        with st.spinner("Gerando o arquivo ZIP..."):
            # Gera o buffer do arquivo ZIP
            zip_buffer = create_database_zip_export()


        # Exibe o botão de download após o processamento
        st.download_button(
            label="Baixar Exportação do Banco de Dados",
            data=zip_buffer,
            file_name="database_export.zip",
            mime="application/zip"
        )

exportar_db_page = st.Page(
    exportar_database,
    title="Exportar Banco de Dados",
    icon="📦",
    url_path='/exportar-base-de-dados'
)

