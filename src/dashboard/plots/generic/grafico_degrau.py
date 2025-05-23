import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_grafico_degrau(leituras, title: str, labels: list = None):
    """
    Função para gerar um gráfico de degrau com os dados do sensor.
    :param leituras: instâncias de LeituraSensor
    :param title: título do gráfico
    :param labels: rótulos para os valores do eixo Y (opcional)
    :return:
    """

    # Cria um DataFrame a partir das leituras
    df = pd.DataFrame([{
        'data_leitura': leitura.data_leitura,
        'estado': 1 if leitura.valor > 0 else 0  # Considera 1 para ligado e 0 para desligado
    } for leitura in leituras])

    # Gráfico de degrau
    fig, ax = plt.subplots()
    ax.step(df['data_leitura'], df['estado'], where='post')
    ax.set_xlabel('Data')
    ax.set_ylabel('Estado')
    ax.set_title(title)
    date_format = mdates.DateFormatter('%H:%M %d/%m/%Y')
    ax.xaxis.set_major_formatter(date_format)
    ax.set_yticks([0, 1])  # Define os valores do eixo Y
    ax.set_yticklabels(labels or ['Desligado', 'Ligado'])  # Define os rótulos do eixo Y
    plt.xticks(rotation=45)

    # Exibe o gráfico no Streamlit
    st.pyplot(fig)

    # Tabela com os dados
    st.write(df)