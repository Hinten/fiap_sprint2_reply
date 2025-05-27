import pandas as pd
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def grafico_barras_generico(
        dataframe: pd.DataFrame,
        eixo_x_key: str,
        eixo_y_key: str,
        eixo_x_label: Optional[str] = None,
        eixo_y_label: Optional[str] = None,
        title: str = 'Gráfico de Barras',
) -> plt.Figure:
    """
    Função para gerar um gráfico de barras genérico.
    :param dataframe: DataFrame contendo os dados a serem plotados
    :param eixo_x_key: Nome da coluna do DataFrame para o eixo X
    :param eixo_y_key: Nome da coluna do DataFrame para o eixo Y
    :param eixo_x_label: Rótulo do eixo X (opcional)
    :param eixo_y_label: Rótulo do eixo Y (opcional)
    :param title: Título do gráfico
    :return:
    """

    if eixo_x_key not in dataframe.columns or eixo_y_key not in dataframe.columns:
        raise ValueError(f"As colunas '{eixo_x_key}' ou '{eixo_y_key}' não existem no DataFrame.")

    #gráfico de barras
    fig, ax = plt.subplots()
    ax.bar(dataframe[eixo_x_key], dataframe[eixo_y_key])
    ax.set_xlabel(eixo_x_label or eixo_x_key.title())
    ax.set_ylabel(eixo_y_label or eixo_y_key.title())
    ax.set_title(title)
    date_format = mdates.DateFormatter('%H:%M %d/%m/%Y')
    ax.xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    return fig


