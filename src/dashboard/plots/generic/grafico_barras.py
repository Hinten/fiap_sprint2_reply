import streamlit as st
from src.database.models.sensor import LeituraSensor
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_grafico_barras(leituras: list[LeituraSensor], title: str):
    """
    Função para gerar um gráfico de barras com os dados do sensor.
    :param leituras: instâncias de LeituraSensor
    :param title: título do gráfico
    :return:
    """


    df = pd.DataFrame([{
        'data_leitura': leitura.data_leitura,
        'valor': leitura.valor
    } for leitura in leituras])

    #gráfico de barras
    fig, ax = plt.subplots()
    ax.bar(df['data_leitura'], df['valor'])
    ax.set_xlabel('Data')
    ax.set_ylabel('Valor')
    ax.set_title(title)
    date_format = mdates.DateFormatter('%H:%M %d/%m/%Y')
    ax.xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    #tabela com os dados
    st.write(df)


