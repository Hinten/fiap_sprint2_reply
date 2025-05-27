from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def grafico_degrau_generico(
        dataframe: pd.DataFrame,
        eixo_x_key: str,
        eixo_y_key: str, #ticks do eixo Y
        eixo_x_label: Optional[str] = None,
        eixo_y_label: Optional[str] = None,
        labels: Optional[list] = None,
        title: str = 'Gráfico de Degrau',
) -> plt.Figure:
    """
    Função para gerar um gráfico de degrau genérico.
    :param dataframe: DataFrame contendo os dados a serem plotados
    :param eixo_x_key: Nome da coluna do DataFrame para o eixo X
    :param eixo_y_key: Nome da coluna do DataFrame para o eixo Y
    :param eixo_x_label: Rótulo do eixo X (opcional)
    :param eixo_y_label: Rótulo do eixo Y (opcional)
    :param labels: Rótulos personalizados para os valores do eixo Y (opcional)
    :param title: Título do gráfico
    :return:
    """

    if eixo_x_key not in dataframe.columns or eixo_y_key not in dataframe.columns:
        raise ValueError(f"As colunas '{eixo_x_key}' ou '{eixo_y_key}' não existem no DataFrame.")

    # pega os yticks do eixo Y
    ticks = dataframe[eixo_y_key].unique()

    # Gráfico de degrau
    fig, ax = plt.subplots()
    ax.step(dataframe[eixo_x_key], dataframe[eixo_y_key], where='post')
    ax.set_xlabel(eixo_x_label or eixo_x_key.title())
    ax.set_ylabel(eixo_y_label or eixo_y_key.title())
    ax.set_title(title)
    date_format = mdates.DateFormatter('%H:%M %d/%m/%Y')
    ax.xaxis.set_major_formatter(date_format)
    ax.set_yticks(ticks)  # Define os valores do eixo Y
    if labels:
        ax.set_yticklabels(labels)  # Define os rótulos do eixo Y
    plt.xticks(rotation=45)

    return fig