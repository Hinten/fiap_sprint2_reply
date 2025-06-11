# src/sensores/simulador.py

import random
import numpy as np
from datetime import datetime, timedelta

from src.database.tipos_base.database import Database
from src.database.models.sensor import LeituraSensor


def gerar_leituras_vibracao(sensor_id: int, tempo_total: int = 10, leituras_por_segundo: int = 5):
    total_leituras = tempo_total * leituras_por_segundo
    tempo = np.linspace(0, tempo_total, total_leituras)
    vibracao = 2 * tempo + np.random.normal(0, 0.5, total_leituras)

    # Falhas simuladas
    picos = []
    if random.random() < 0.7:
        num_falhas = random.randint(1, 3)
        picos = random.sample(range(total_leituras), num_falhas)
        for pico in picos:
            vibracao[pico] += random.uniform(4, 8)

    # Salva no banco
    with Database.get_session() as session:
        agora = datetime.now()
        leituras = [
            LeituraSensor(
                sensor_id=sensor_id,
                data_leitura=agora + timedelta(seconds=i),
                valor=float(vibracao[i])
            ) for i in range(total_leituras)
        ]
        session.add_all(leituras)
        session.commit()

    return picos
