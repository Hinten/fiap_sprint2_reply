from datetime import datetime
from random import randrange, choice
from typing import Literal, Optional, Union
from src.database.models.sensor import LeituraSensor
import numpy as np


def criar_dados_leitura(
        data_inicial:datetime,
        data_final:datetime,
        sensor_id:int,
        total_leituras:int,
        tipo:Union[type[bool], type[float], type[int]],
        minimo:Optional[int or float or None]=None,
        maximo:Optional[int or float or None]=None
) -> list[LeituraSensor]:
    """
    Cria dados de leitura um sensor específico em um intervalo de datas.

    Args:
        data_inicial (datetime): Data inicial do intervalo.
        data_final (datetime): Data final do intervalo.
        sensor_id (int): ID do sensor.
        total_leituras (int): Total de leituras a serem geradas.
        tipo (Union[type[bool], type[float], type[int]]): Tipo de dado a ser gerado. Pode ser 'bool', 'float' ou 'int'.
        minimo (float or None): Valor mínimo para o tipo 'int' e 'float'. Ignorado se tipo for 'bool'.
        maximo (float or None): Valor máximo para o tipo 'int' e 'float. Ignorado se tipo for 'bool'.

    Returns:
        list: Lista de dicionários com os dados de leitura gerados.
    """

    assert (data_inicial < data_final), "A data inicial deve ser anterior à data final."
    assert tipo == bool or (tipo != bool and minimo is not None and maximo is not None), "Informe valores mínimo e máximo apenas para tipos 'int' e 'float'."
    assert (minimo is None or maximo is None or minimo < maximo), "O valor mínimo deve ser menor que o máximo."

    leituras = []

    for i in range(total_leituras):
        data_leitura = data_inicial + (data_final - data_inicial) * (i / total_leituras)
        if tipo == bool:
            valor = choice([0, 1])
        elif tipo == int:
            valor = randrange(int(minimo), int(maximo))
        elif tipo == float:
            valor = np.random.uniform(minimo, maximo)
        else:
            raise ValueError("Tipo inválido. Deve ser 'bool' ou 'range'.")
        leituras.append(LeituraSensor(
            sensor_id=sensor_id,
            data_leitura=data_leitura,
            valor=valor
        ))

    print(f"Geradas {len(leituras)} leituras para o sensor {sensor_id} entre {data_inicial} e {data_final}.")

    return leituras
