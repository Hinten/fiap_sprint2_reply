import streamlit as st
from src.dashboard.generic.model_form_fields import ModelFormField
from src.dashboard.plots.generic.grafico_barras import get_grafico_barras
from src.dashboard.plots.generic.grafico_degrau import get_grafico_degrau
from src.dashboard.plots.generic.grafico_linha import get_grafico_linha
from src.dashboard.plots.generic.utils import get_sensores_por_tipo, get_leituras_for_sensor
from src.database.generator.criar_dados_leitura import criar_dados_litura_para_sensor
from src.database.models.sensor import TipoSensorEnum, LeituraSensor, Sensor
from datetime import datetime, timedelta

from src.database.tipos_base.model import Model


class SimplePlotView:

    def __init__(self, model:type[Model]):
        self.model = model

    def view(self):
        """
        Função para exibir a página principal do aplicativo.
        :return:
        """
        st.title(f"Gráfico de {self.model.display_name_plural()}")

        filter_data = {}

        for plot_field in self.model.__generic_plot__.filters:

            form_field = ModelFormField(self.model, plot_field.field)

            new_value = form_field.render()

            filter_data[plot_field.field] = new_value

        col1, col2 = st.columns(2)

        simulacao = None
        real = None

        with col1:
            simulacao = st.button("Gerar Simulação")


        with col2:
            real = st.button("Gerar Gráfico")

        raise NotImplementedError("A funcionalidade de plotagem ainda não foi implementada.")

        # if simulacao or real:
        #
        #     for plot_field in self.model.__generic_plot__.filters:
        #         form_field = ModelFormField(self.model, plot_field.field)
        #         value = filter_data.get(plot_field.field)
        #         if not form_field.is_valid(value, required=not plot_field.optional):
        #             st.error(f"Erro ao validar o campo {plot_field.field}: {form_field.validate(value, required=not plot_field.optional)}")
        #             return
        #
        #
        # if (simulacao or real) and (
        #         sensor_selecionado is None or data_inicial is None or data_final is None
        # ):
        #     st.warning("Selecione um sensor e as datas para gerar o gráfico.")
        #
        # elif simulacao:
        #     leituras = criar_dados_litura_para_sensor(
        #         data_inicial=data_inicial,
        #         data_final=data_final,
        #         sensor_id=sensor_selecionado.id,
        #         total_leituras=20,
        #         tipo_sensor=self.tipo_sensor
        #     )
        #
        #     self.get_grafico(sensor_selecionado, leituras,
        #                      f"Gráfico Simulação de {self.tipo_sensor} do sensor {sensor_selecionado.nome}")
        #
        #
        # elif real:
        #     leituras = get_leituras_for_sensor(sensor_selecionado.id, data_inicial, data_final)
        #
        #     if len(leituras) > 0:
        #         self.get_grafico(sensor_selecionado, leituras,
        #                          f"Gráfico Real de {self.tipo_sensor} do sensor {sensor_selecionado.nome}")
        #     else:
        #         st.warning("Nenhum dado encontrado para o sensor selecionado entre as datas informadas.")


    def get_grafico(self, sensor_selecionado:Sensor, leituras: list[LeituraSensor], title: str):
        """
        Função para gerar o gráfico de acordo com o tipo selecionado.
        :param leituras: instâncias de LeituraSensor
        :param title: título do gráfico
        :return:
        """

        raise NotImplementedError("A funcionalidade de plotagem ainda não foi implementada.")

        # if self.tipo_grafico == TipoGraficoEnum.BARRAS:
        #     get_grafico_barras(leituras, f"Gráfico de {self.tipo_sensor} do sensor {sensor_selecionado.nome}")
        # elif self.tipo_grafico == TipoGraficoEnum.LINHA:
        #     get_grafico_linha(leituras, f"Gráfico de {self.tipo_sensor} do sensor {sensor_selecionado.nome}")
        # elif self.tipo_grafico == TipoGraficoEnum.DEGRAU:
        #     get_grafico_degrau(leituras, f"Gráfico de {self.tipo_sensor} do sensor {sensor_selecionado.nome}", labels=self.labels)


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

