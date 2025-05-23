from src.dashboard.plots.plot_view import PlotView, TipoGraficoEnum
from src.dashboard.plots.todas_leituras.view_todas_leituras import PlotAllView
from src.database.models.sensor import TipoSensorEnum

grafico_tudo = PlotAllView(
    title="Gráfico de Todas as Leituras",
    url_path="/graficotudo",
)

grafico_umidade_view = PlotView(
    title="Gráfico de Umidade",
    url_path="/graficoumidade",
    tipo_sensor=TipoSensorEnum.UMIDADE,
    tipo_grafico=TipoGraficoEnum.LINHA
)
grafico_estado_do_rele = PlotView(
    title="Gráfico de Estado do Relé",
    url_path="/graficorele",
    tipo_sensor=TipoSensorEnum.RELE,
    tipo_grafico=TipoGraficoEnum.DEGRAU
)
grafico_ph = PlotView(
    title="Gráfico de pH",
    url_path="/graficoph",
    tipo_sensor=TipoSensorEnum.PH,
)

grafico_fosforo = PlotView(
    title="Gráfico de Fósforo",
    url_path="/graficofosforo",
    tipo_sensor=TipoSensorEnum.FOSFORO,
    tipo_grafico=TipoGraficoEnum.DEGRAU,
    labels=['Ausente', 'Presente']
)

grafico_potassio = PlotView(
    title="Gráfico de Potássio",
    url_path="/graficopotassio",
    tipo_sensor=TipoSensorEnum.POTASSIO,
    tipo_grafico=TipoGraficoEnum.DEGRAU,
    labels=['Ausente', 'Presente']
)