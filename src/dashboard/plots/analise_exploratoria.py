import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta,time
import seaborn as sns
import matplotlib.pyplot as plt

from src.database.models.sensor import LeituraSensor, Sensor, TipoSensor, TipoSensorEnum
from src.database.tipos_base.database import Database


def analise_exploratoria_view():
    st.title('Análise Exploratória das Leituras dos Sensores')

    data_inicial = st.date_input(
        'Data Inicial',
        format="DD/MM/YYYY",
        value=None
    )

    data_final = st.date_input(
        'Data Final',
        format="DD/MM/YYYY",
        value=None
    )

    if data_inicial and data_final is None:
        st.warning('Por favor, selecione uma data final.')
        return

    if data_final and data_inicial is None:
        st.warning('Por favor, selecione uma data inicial.')
        return

    if (data_inicial and data_final) and (data_inicial > data_final):
        st.warning('A data inicial não pode ser maior que a data final.')
        return

    if data_inicial is None and data_final is None:

        st.info('''
        Esta página apresenta uma análise exploratória dos dados coletados pelos sensores do sistema. 
        Os dados são extraídos diretamente do banco de dados, considerando os últimos 7 dias. Caso não haja leituras nesse período, são exibidas as últimas 1000 leituras disponíveis.
        ''')

        data_inicial = datetime.now() - timedelta(days=7)
        data_final = datetime.now()

    data_inicial = datetime.combine(data_inicial, time.min)
    data_final = datetime.combine(data_final, time.max)

    with Database.get_session() as session:
        leituras = session.query(LeituraSensor).filter(
            LeituraSensor.data_leitura >= data_inicial,
            LeituraSensor.data_leitura <= data_final
            ).all()
        if not leituras and data_inicial is None and data_final is None:
            leituras = session.query(LeituraSensor).order_by(LeituraSensor.data_leitura.desc()).limit(1000).all()

        # Obter todos os tipos de sensor existentes

        tipos_sensor_query = session.query(TipoSensor).all()

        tipos_sensor = {ts.id: ts for ts in tipos_sensor_query}
        sensores = session.query(Sensor).all()
        sensor_id_to_tipo = {s.id: s.tipo_sensor_id for s in sensores}

    if not leituras:
        st.warning('Não há leituras disponíveis para exibir os gráficos.')
        return

    # Montar DataFrame consolidado
    data = []
    for l in leituras:
        tipo = sensor_id_to_tipo.get(l.sensor_id, None)

        tipo_target:TipoSensor or None = tipos_sensor.get(tipo, None)

        valor_target = np.nan

        if tipo_target:
            tipo_enum:TipoSensorEnum = tipo_target.tipo
            valor_target = tipo_enum.get_valor_escalado(l.valor)

        data.append({
            'data_leitura': l.data_leitura,
            tipo: valor_target
        })
    df = pd.DataFrame(data)
    df = df.groupby('data_leitura').first().reset_index()

    # Garantir colunas para todos os tipos de sensor
    for tipo in tipos_sensor:
        if tipo not in df.columns:
            df[tipo] = np.nan

    # Ordenar por data
    df = df.sort_values('data_leitura')

    # Preencher valores ausentes pelo metodo do vizinho mais próximo
    df = df.set_index('data_leitura')
    df = df.apply(lambda col: col.ffill().bfill())
    df = df.reset_index()

    st.markdown('#### Visualização dos dados consolidados')

    sensor_labels = {ts.id: ts.nome for ts in tipos_sensor_query}

    dataframe_labels = {
        'data_leitura': 'Data da Leitura',
        **sensor_labels,
    }

    st.dataframe(df.rename(columns=dataframe_labels), use_container_width=True)

    # Gráfico de linha para cada tipo de sensor
    st.markdown('#### Gráficos de Linha por Tipo de Sensor')
    for tipo in tipos_sensor:
        if df[tipo].notnull().any():
            fig = px.line(df,
                          x='data_leitura',
                          y=tipo,
                          title=f'Evolução das Leituras - {str(tipos_sensor[tipo])}',
                          labels={
                              'data_leitura': 'Data da Leitura',
                              str(tipo): f'Valor do Sensor ({sensor_labels.get(tipo, "Desconhecido")})'
                          }
                          )
            st.plotly_chart(fig, use_container_width=True)

    # Boxplot dos valores dos sensores
    st.markdown('#### Boxplot dos Valores dos Sensores')
    df_melt = df.melt(
        id_vars=['data_leitura'],
        value_vars=list(tipos_sensor.keys()),
        var_name='TipoSensor',
        value_name='Valor'
    )
    # Mapeia os ids para nomes legíveis no DataFrame "melted"
    df_melt['TipoSensor'] = df_melt['TipoSensor'].map(sensor_labels)

    fig_box = px.box(
        df_melt,
        x='TipoSensor',
        y='Valor',
        title='Distribuição dos Valores por Tipo de Sensor',
        labels={
            'TipoSensor': 'Tipo de Sensor',
            'Valor': 'Valor do Sensor'
        }
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # Matriz de correlação
    st.markdown('#### Matriz de Correlação entre Sensores')
    if df[list(tipos_sensor.keys())].dropna().shape[0] > 1:
        corr = df[list(tipos_sensor.keys())].corr()
        corr.index = corr.index.map(sensor_labels)
        corr.columns = corr.columns.map(sensor_labels)
        fig_corr = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorscale='Viridis'))
        fig_corr.update_layout(title='Correlação entre Tipos de Sensor')
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning('Não há dados suficientes para calcular a matriz de correlação.')

    # Scatterplot para os dois primeiros tipos de sensor (se existirem)
    sensor_keys = list(tipos_sensor.keys())
    if len(sensor_keys) >= 2:
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        sns.scatterplot(
            data=df,
            x=sensor_keys[0],
            y=sensor_keys[1],
            ax=ax1,
            hue=sensor_keys[0],
            palette='viridis'
        )
        ax1.set_xlabel(sensor_labels[sensor_keys[0]])
        ax1.set_ylabel(sensor_labels[sensor_keys[1]])
        ax1.set_title(f'Scatterplot: {sensor_labels[sensor_keys[0]]} vs {sensor_labels[sensor_keys[1]]}')
        st.pyplot(fig1)

    if len(sensor_keys) >= 3:
        fig_3d = px.scatter_3d(
            df,
            x=sensor_keys[0],
            y=sensor_keys[1],
            z=sensor_keys[2],
            color=sensor_keys[0],
            title='Scatter 3D: {} vs {} vs {}'.format(
                sensor_labels[sensor_keys[0]],
                sensor_labels[sensor_keys[1]],
                sensor_labels[sensor_keys[2]]
            )
            ,
            labels={
                sensor_keys[0]: sensor_labels[sensor_keys[0]],
                sensor_keys[1]: sensor_labels[sensor_keys[1]],
                sensor_keys[2]: sensor_labels[sensor_keys[2]],
            },
            color_continuous_scale='Viridis'
        )

        fig_3d.update_traces(marker=dict(size=5))
        fig_3d.update_layout(scene=dict(
            xaxis_title=sensor_labels[sensor_keys[0]],
            yaxis_title=sensor_labels[sensor_keys[1]],
            zaxis_title=sensor_labels[sensor_keys[2]]
        ))

        st.plotly_chart(fig_3d, use_container_width=True)

    # Barplot da média dos valores por tipo de sensor
    df_bar = df.melt(id_vars=['data_leitura'], value_vars=sensor_keys, var_name='TipoSensor', value_name='Valor')
    df_bar['TipoSensor'] = df_bar['TipoSensor'].map(sensor_labels)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=df_bar, x='TipoSensor', y='Valor', estimator=np.mean, ax=ax2)
    ax2.set_title('Barplot: Média dos Valores por Tipo de Sensor')

    st.pyplot(fig2)

    # Pairplot dos sensores
    if len(sensor_keys) > 1:
        df_renomeado = df[sensor_keys].rename(columns=sensor_labels)
        fig4 = sns.pairplot(df_renomeado.dropna(), height=2)
        st.pyplot(fig4)

