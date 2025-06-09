import pandas as pd
import streamlit as st
from sqlalchemy import BinaryExpression
from src.dashboard.generic.model_query_filters import ModelQueryFilters

from src.database.tipos_base.model import Model
from src.plots.model_plot import ModelPlotter


class SimplePlotView:

    def __init__(self, model:type[Model]):
        self.model = model

    def view(self):
        """
        Função para exibir a página principal do aplicativo.
        :return:
        """
        st.title(f"Gráfico de {self.model.display_name_plural()}")

        plot_filters = ModelQueryFilters(self.model,
                                         self.model.__generic_plot__.filters,
                                         show_validation=st.query_params.get('show_validation', False) == '1',
                                         show_botao_filtrar=False
                                         )

        plot_filters.render()

        col1, col2 = st.columns(2)

        simulacao = st.query_params.get('simulacao', False)
        real = st.query_params.get('real', False)

        with col1:
            if st.button("Gerar Simulação"):
                plot_filters.apply_filters()
                st.query_params['simulacao'] = '1'
                st.query_params.pop('real', None)
                st.rerun()


        with col2:
            if st.button("Gerar Gráfico Real"):
                plot_filters.apply_filters()
                st.query_params['real'] = '1'
                st.query_params.pop('simulacao', None)
                st.rerun()

        if simulacao or real:

            if not plot_filters.filters_valid():
                st.error("Por favor, preencha todos os filtros obrigatórios.")
                st.query_params['show_validation'] = '1'
                return
            else:
                st.query_params.pop('show_validation', None)

        if simulacao:
            data = self.model.random_range(nullable=False, quantity=100, **{'values': plot_filters.get_filter_values(), 'values_by_name': plot_filters.get_filter_values_by_name()})

            dataframe = pd.DataFrame(map(lambda x: x.to_dict(), data))

            print(dataframe)

            model_plotter = ModelPlotter(self.model)

            grafico = model_plotter.get_plot(dataframe)

            st.pyplot(grafico)

        elif real:

            filters:list[BinaryExpression] = plot_filters.get_sqlalchemy_filters()

            model_plotter = ModelPlotter(self.model)
            dataframe = model_plotter.get_data_for_plot(filters=filters)
            grafico = model_plotter.get_plot(dataframe)
            st.pyplot(grafico)



    def get_page(self) -> st.Page:
        """
        Função para retornar a página de gráfico de umidade.
        :return: st.Page - A página para gerar o gráfico de umidade do aplicativo.
        """
        return st.Page(
            self.view,
            title=self.title,
            url_path=self.url_path
        )

