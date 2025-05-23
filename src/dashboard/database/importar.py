import streamlit as st
from sqlalchemy.exc import DatabaseError, IntegrityError
from src.database.export_import_db import import_database_zip
import pandas as pd

from src.database.reset_contador_ids import reset_contador_ids


def importar_database():

    st.title("Importar Banco de Dados")
    # Botão para iniciar o processo de exportação
    # Componente para upload de arquivo
    uploaded_file = st.file_uploader("Escolha um arquivo para enviar", type=["zip"])

    if uploaded_file is not None:
        st.info(f"Arquivo '{uploaded_file.name}' lido com sucesso!")
        # Exemplo: leitura do arquivo se for CSV
        models = import_database_zip(uploaded_file)

        for model, rows in models:
            st.write(f"Modelo: {model.__tablename__}")

            #faz um dataframe com as rows
            df = pd.DataFrame(map(lambda x: x.to_dict(), rows))
            st.write(df)

        if st.button("Salvar no Banco de Dados"):
            with st.spinner("Salvando no banco de dados..."):
                # Salva os dados no banco de dados
                for model, rows in models:
                    for row in rows:
                        try:
                            row.save()
                        except IntegrityError as e:
                            if e.code == "gkpj":
                                print('record already exists')
                                row.merge()
                            else:
                                print(e.code)
                                raise
                        except DatabaseError as e:
                            print('aqui')
                            if e.code == " DPY-4011":
                                row.save()
                            else:
                                print(e.code)
                                raise

                # Atualiza o contador de IDs
                reset_contador_ids()


            st.success("Banco de dados atualizado com sucesso!")


importar_db_page = st.Page(
    importar_database,
    title="Importar Banco de Dados",
    icon="📦",
    url_path='/importar-base-de-dados'
)

