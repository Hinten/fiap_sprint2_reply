import matplotlib.pyplot as plt
from sqlalchemy import BinaryExpression
from src.plots.generic.grafico_degrau import grafico_degrau_generico
from src.plots.generic.grafico_barras import grafico_barras_generico
from src.plots.generic.grafico_linha import get_grafico_linha
from src.database.tipos_base.model import Model
import pandas as pd

from src.plots.plot_config import TipoGrafico


class ModelPlotter:
    def __init__(self, model:type[Model]):
        self.model = model

    def get_data_for_plot(self, filters:list[BinaryExpression] or None = None) -> pd.DataFrame:
        """
        Obtém os dados da instância formatados para plotagem.
        """

        if self.model.__generic_plot__ is None:
            raise NotImplementedError(
                "A classe não implementa o método 'get_data_for_plot' ou não possui um 'generic_plot' definido.")

        # faz um query com o sqlalchemy filtrando pelos filters do generic_plot e ordernando pelos order_by do generic_plot

        order_by = None

        if self.model.__generic_plot__.order_by is not None:
            order_by = [getattr(self.model, field.field) for field in self.model.__generic_plot__.order_by]
            order_by = [field.asc() if not field.desc else field.desc() for field in order_by]



        return self.model.filter_dataframe(
            filters=filters,
            order_by=order_by,
            select_fields=[f.field for f in self.model.__generic_plot__.eixo_x] + [f.field for f in self.model.__generic_plot__.eixo_y]
        )

    def get_plot(self, dataframe:pd.DataFrame) -> plt.Figure:
        """
        Obtém os dados da instância formatados para plotagem e retorna o DataFrame.
        """

        match self.model.__generic_plot__.tipo:
            case TipoGrafico.DEGRAU:
                return self.get_grafico_degrau(dataframe)
            case TipoGrafico.BARRAS:
                return self.get_grafico_barras(dataframe)
            case TipoGrafico.LINHA:
                return self.get_grafico_linha(dataframe)
            case _:
                raise ValueError(f"Tipo de gráfico '{self.model.__generic_plot__.tipo}' não suportado.")

        return fig

    def get_grafico_degrau(self, dataframe:pd.DataFrame) -> plt.Figure:
        """
        Obtém um gráfico de degrau para a instância.
        """

        if len(self.model.__generic_plot__.eixo_x) != 1:
            raise ValueError("O gráfico de degrau deve ter exatamente um eixo X definido.")

        if len(self.model.__generic_plot__.eixo_y) != 1:
            raise ValueError("O gráfico de degrau deve ter exatamente um eixo Y definido.")

        field_x = self.model.__generic_plot__.eixo_x[0]
        field_y = self.model.__generic_plot__.eixo_y[0]

        x_label =field_x.display_name or self.model.get_field_display_name(field_x.field)
        y_label = field_y.display_name or self.model.get_field_display_name(field_y.field)

        fig = grafico_degrau_generico(
            dataframe=dataframe,
            eixo_x_key=field_x.field,
            eixo_y_key=field_y.field,
            eixo_x_label=x_label,
            eixo_y_label=y_label,
            labels=self.model.__generic_plot__.labels_eixo_y,
            title=self.model.__generic_plot__.title or f'Gráfico de Degrau - {self.model.display_name()}'
        )

        return fig

    def get_grafico_barras(self, dataframe:pd.DataFrame) -> plt.Figure:
        """
        Obtém um gráfico de barras para a instância.
        """

        if len(self.model.__generic_plot__.eixo_x) != 1:
            raise ValueError("O gráfico de barras deve ter exatamente um eixo X definido.")

        if len(self.model.__generic_plot__.eixo_y) != 1:
            raise ValueError("O gráfico de barras deve ter exatamente um eixo Y definido.")

        field_x = self.model.__generic_plot__.eixo_x[0]
        field_y = self.model.__generic_plot__.eixo_y[0]

        x_label = field_x.display_name or self.model.get_field_display_name(field_x.field)
        y_label = field_y.display_name or self.model.get_field_display_name(field_y.field)

        fig = grafico_barras_generico(
            dataframe=dataframe,
            eixo_x_key=field_x.field,
            eixo_y_key=field_y.field,
            eixo_x_label=x_label,
            eixo_y_label=y_label,
            title=self.model.__generic_plot__.title or f'Gráfico de Barras - {self.model.display_name()}'
        )

        return fig

    def get_grafico_linha(self, dataframe:pd.DataFrame) -> plt.Figure:
        """
        Obtém um gráfico de linha para a instância.
        """

        if len(self.model.__generic_plot__.eixo_x) != 1:
            raise ValueError("O gráfico de linha deve ter exatamente um eixo X definido.")

        if len(self.model.__generic_plot__.eixo_y) != 1:
            raise ValueError("O gráfico de linha deve ter exatamente um eixo Y definido.")

        field_x = self.model.__generic_plot__.eixo_x[0]
        field_y = self.model.__generic_plot__.eixo_y[0]

        x_label = field_x.display_name or self.model.get_field_display_name(field_x.field)
        y_label = field_y.display_name or self.model.get_field_display_name(field_y.field)

        fig = get_grafico_linha(
            dataframe=dataframe,
            eixo_x_key=field_x.field,
            eixo_y_key=field_y.field,
            eixo_x_label=x_label,
            eixo_y_label=y_label,
            title=self.model.__generic_plot__.title or f'Gráfico de Linha - {self.model.display_name()}'
        )

        return fig