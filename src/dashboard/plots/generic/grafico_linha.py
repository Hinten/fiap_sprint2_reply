import streamlit as st
from src.database.models.sensor import LeituraSensor
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_grafico_linha(leituras: list[LeituraSensor], title: str):
    """
    Função para gerar um gráfico de linha com os dados do sensor.
    :param leituras: instâncias de LeituraSensor
    :param title: título do gráfico
    :return:
    """

    # Cria um DataFrame a partir das leituras
    df = pd.DataFrame([{
        'data_leitura': leitura.data_leitura,
        'valor': leitura.valor
    } for leitura in leituras])

    # Gráfico de linha
    fig, ax = plt.subplots()
    ax.plot(df['data_leitura'], df['valor'])
    ax.grid(True)
    ax.set_xlabel('Data')
    ax.set_ylabel('Valor')
    ax.set_title(title)
    date_format = mdates.DateFormatter('%H:%M %d/%m/%Y')
    ax.xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    # Exibe o gráfico no Streamlit
    st.pyplot(fig)

    # Tabela com os dados
    st.write(df)
