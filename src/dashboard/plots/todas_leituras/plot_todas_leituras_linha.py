from src.database.models.sensor import LeituraSensor
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import functools
import numpy as np

def moda(arr):
    vals, counts = np.unique(arr, return_counts=True)
    return vals[np.argmax(counts)]

def preencher_moda(row, coluna, coluna_bfill, coluna_ffill):
    if np.isnan(row[coluna]):
        anteriores = [row[coluna_bfill], row[coluna_ffill]]
        # Remove NaN
        anteriores = [v for v in anteriores if not np.isnan(v)]
        if anteriores:
            # Se os valores são iguais, retorna o valor
            if anteriores[0] == anteriores[-1]:
                return anteriores[0]
            # Se são diferentes, retorna a moda
            return moda(anteriores)
        else:
            return np.nan
    else:
        return row['valor_rele']

def get_grafico_linha_todas_leituras(
        leituras_umidade: list[LeituraSensor],
        leituras_rele: list[LeituraSensor],
        leituras_ph: list[LeituraSensor],
        leituras_fosforo: list[LeituraSensor],
        leituras_potassio: list[LeituraSensor],
        title: str):
    """
    Função para gerar um gráfico de linha com os dados do sensor.
    :param leituras: instâncias de LeituraSensor
    :param leituras_umidade: instâncias de LeituraSensor
    :param leituras_rele: instâncias de LeituraSensor
    :param leituras_ph: instâncias de LeituraSensor
    :param leituras_fosforo: instâncias de LeituraSensor
    :param leituras_potassio: instâncias de LeituraSensor
    :param title: título do gráfico
    :return:
    """

    # Cria um DataFrame a partir das leituras
    dfs = [
        pd.DataFrame([{'data_leitura': l.data_leitura, 'valor_umidade': l.valor} for l in leituras_umidade]),
        pd.DataFrame([{'data_leitura': l.data_leitura, 'valor_rele': l.valor} for l in leituras_rele]),
        pd.DataFrame([{'data_leitura': l.data_leitura, 'valor_ph': l.valor} for l in leituras_ph]),
        pd.DataFrame([{'data_leitura': l.data_leitura, 'valor_fosforo': l.valor} for l in leituras_fosforo]),
        pd.DataFrame([{'data_leitura': l.data_leitura, 'valor_potassio': l.valor} for l in leituras_potassio]),
    ]

    # Concatena os DataFrames
    df = functools.reduce(lambda left, right: pd.merge(left, right, on='data_leitura', how='outer'), dfs)

    df['valor_umidade'] = df['valor_umidade'].fillna(df['valor_umidade'].mean())
    df['valor_ph'] = df['valor_ph'].fillna(df['valor_ph'].mean())

    df['rele_ffill'] = df['valor_rele'].ffill()
    df['rele_bfill'] = df['valor_rele'].bfill()
    df['valor_rele'] = df.apply(preencher_moda, args=('valor_rele', 'rele_bfill', 'rele_ffill'), axis=1)
    df = df.drop(columns=['rele_ffill', 'rele_bfill'])
    #
    df['fosforo_fill'] = df['valor_fosforo'].ffill()
    df['fosforo_bfill'] = df['valor_fosforo'].bfill()
    df['valor_fosforo'] = df.apply(preencher_moda, args=('valor_fosforo', 'fosforo_bfill', 'fosforo_fill'), axis=1)
    df = df.drop(columns=['fosforo_fill', 'fosforo_bfill'])

    df['potassio_fill'] = df['valor_potassio'].ffill()
    df['potassio_bfill'] = df['valor_potassio'].bfill()
    df['valor_potassio'] = df.apply(preencher_moda, args=('valor_potassio', 'potassio_bfill', 'potassio_fill'), axis=1)
    df = df.drop(columns=['potassio_fill', 'potassio_bfill'])

    # Gráfico de linha
    fig, ax = plt.subplots()

    ax.plot(df['data_leitura'], df['valor_umidade'], label='Umidade', alpha=0.7)
    ax.plot(df['data_leitura'], df['valor_rele'], label='Rele', alpha=0.7)
    ax.plot(df['data_leitura'], df['valor_ph'], label='pH', alpha=0.7)
    ax.plot(df['data_leitura'], df['valor_fosforo'], label='Fósforo', alpha=0.7)
    ax.plot(df['data_leitura'], df['valor_potassio'], label='Potássio', alpha=0.7)
    ax.grid(True)
    ax.set_xlabel('Data')
    ax.set_ylabel('Valor')
    ax.set_title(title)
    ax.legend()
    plt.xticks(rotation=45)
    # Exibe o gráfico no Streamlit
    plt.tight_layout()

    st.pyplot(fig)

    st.write(df)
