import streamlit as st
from src.database.tipos_base.database import Database
from src.database.models.sensor import Sensor, TipoSensor, TipoSensorEnum, LeituraSensor
from datetime import datetime, timedelta, date, time
import pandas as pd
import matplotlib.pyplot as plt

#tirei o cache para evitar problemas
# @st.cache_data
def get_sensores_por_tipo(tipo:TipoSensorEnum) -> list[Sensor]:
    """Faz uma consulta com o SQLAlchemy para retornar os sensores de umidade."""

    return Sensor.filter_by_tiposensor(tipo)

# @st.cache_data
def get_leituras_for_sensor(sensor_id: int, data_inicial: date, data_final: date) -> list[LeituraSensor]:
    """Faz uma consulta com o SQLAlchemy para retornar as leituras de um sensor entre duas datas."""

    return LeituraSensor.get_leituras_for_sensor(sensor_id, data_inicial, data_final)