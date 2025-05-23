from datetime import datetime
from random import randrange, choice
from typing import Literal, Optional
from src.database.models.sensor import LeituraSensor, TipoSensorEnum


def criar_dados_leitura(
        data_inicial:datetime,
        data_final:datetime,
        sensor_id:int,
        total_leituras:int,
        tipo:Literal['bool', 'range'],
        minimo:Optional[float]=None,
        maximo:Optional[float]=None
) -> list[LeituraSensor]:
    """
    Cria dados de leitura um sensor específico em um intervalo de datas.

    Args:
        data_inicial (datetime): Data inicial do intervalo.
        data_final (datetime): Data final do intervalo.
        sensor_id (int): ID do sensor.
        total_leituras (int): Total de leituras a serem geradas.
        tipo (Literal['bool', 'range']): Tipo de leitura a ser gerada ('bool' ou 'range').
        minimo (float or None): Valor mínimo para o tipo 'range'. Ignorado se tipo for 'bool'.
        maximo (float or None): Valor máximo para o tipo 'range'. Ignorado se tipo for 'bool'.

    Returns:
        list: Lista de dicionários com os dados de leitura gerados.
    """

    assert (data_inicial < data_final), "A data inicial deve ser anterior à data final."
    assert (tipo == 'bool' or tipo == 'range'), "O tipo deve ser 'bool' ou 'range'."
    assert (tipo != 'range' or (minimo is not None and maximo is not None)), "O tipo 'range' requer valores mínimo e máximo."
    assert (minimo is None or maximo is None or minimo < maximo), "O valor mínimo deve ser menor que o máximo."

    leituras = []

    for i in range(total_leituras):
        data_leitura = data_inicial + (data_final - data_inicial) * (i / total_leituras)
        if tipo == 'bool':
            valor = choice([0, 1])
        elif tipo == 'range':
            valor = randrange(minimo, maximo)
        else:
            raise ValueError("Tipo inválido. Deve ser 'bool' ou 'range'.")
        leituras.append(LeituraSensor(
            sensor_id=sensor_id,
            data_leitura=data_leitura,
            valor=valor
        ))

    return leituras


def criar_dados_litura_para_sensor(
        data_inicial: datetime,
        data_final: datetime,
        sensor_id: int,
        total_leituras: int,
        tipo_sensor: TipoSensorEnum,
) -> list[LeituraSensor]:
    """
    Cria dados de leitura para um sensor específico em um intervalo de datas.
    Args:
        data_inicial (datetime): Data inicial do intervalo.
        data_final (datetime): Data final do intervalo.
        sensor_id (int): ID do sensor.
        total_leituras (int): Total de leituras a serem geradas.
        tipo_sensor (TipoSensorEnum): Tipo de sensor.

    Returns:
        list: Lista de dicionários com os dados de leitura gerados.
    """

    if tipo_sensor == TipoSensorEnum.FOSFORO:
        return criar_dados_leitura(
            data_inicial=data_inicial,
            data_final=data_final,
            sensor_id=sensor_id,
            total_leituras=total_leituras,
            tipo='bool'
        )
    elif tipo_sensor == TipoSensorEnum.POTASSIO:
        return criar_dados_leitura(
            data_inicial=data_inicial,
            data_final=data_final,
            sensor_id=sensor_id,
            total_leituras=total_leituras,
            tipo='bool'
        )

    elif tipo_sensor == TipoSensorEnum.PH:
        return criar_dados_leitura(
            data_inicial=data_inicial,
            data_final=data_final,
            sensor_id=sensor_id,
            total_leituras=total_leituras,
            tipo='range',
            minimo=0,
            maximo=14
        )
    elif tipo_sensor == TipoSensorEnum.UMIDADE:
        return criar_dados_leitura(
            data_inicial=data_inicial,
            data_final=data_final,
            sensor_id=sensor_id,
            total_leituras=total_leituras,
            tipo='range',
            minimo=0,
            maximo=100
        )
    elif tipo_sensor == TipoSensorEnum.RELE:
        return criar_dados_leitura(
            data_inicial=data_inicial,
            data_final=data_final,
            sensor_id=sensor_id,
            total_leituras=total_leituras,
            tipo='bool'
        )
    else:
        raise ValueError("Tipo de sensor inválido.")