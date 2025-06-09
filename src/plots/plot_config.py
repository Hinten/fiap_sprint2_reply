from typing import Optional, Literal, List
from enum import Enum
from dataclasses import dataclass

from src.database.tipos_base.model_mixins.display import SimpleTableFilter


class TipoGrafico(Enum):
    LINHA = 'linha'
    BARRAS = 'barras'
    DEGRAU = 'degrau'

@dataclass(frozen=True)
class PlotField:
    field: str
    optional: bool = False

    display_name: Optional[str] = None


@dataclass(frozen=True)
class OrderBy:
    field: str

    #ascendente ou descendente
    asc: bool = True


@dataclass(frozen=True)
class GenericPlot:
    '''
    Classe para gerar gráficos genéricos para um Model.

    Args:
        eixo_x (list[PlotField]): Lista de campos para o eixo X.
        eixo_y (list[PlotField]): Lista de campos para o eixo Y.
        tipo (TipoGrafico): Tipo do gráfico (opcional, padrão é 'linha').
        labels_eixo_y (Optional[list]): Rótulos personalizados para os valores do eixo Y (opcional).
        title (Optional[str]): Título do gráfico (opcional).
        filters (Optional[list[SimpleTableFilter]]): Filtros para os campos do gráfico (opcional).
        order_by (Optional[list[OrderBy]]): Ordenação dos dados do gráfico (opcional).

    '''

    eixo_x: list[PlotField]
    eixo_y: list[PlotField]
    tipo: TipoGrafico = TipoGrafico.LINHA
    labels_eixo_y: Optional[List[str]] = None
    title: Optional[str] = None
    filters: Optional[list[SimpleTableFilter]] = None
    order_by: Optional[list[OrderBy]] = None

