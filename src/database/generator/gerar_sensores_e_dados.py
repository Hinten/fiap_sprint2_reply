from datetime import datetime
from src.database.generator.criar_dados_leitura import criar_dados_leitura
from src.database.generator.criar_sensores import criar_sensores_padrao
from src.database.models.sensor import LeituraSensor, TipoSensorEnum, Sensor, TipoSensor


def criar_dados_sample(
        data_inicial:datetime,
        data_final:datetime,
        total_leituras:int,
) -> list[tuple[Sensor, list[LeituraSensor]]]:
    """
    Cria dados de leitura para sensores em um intervalo de datas.
    :param data_inicial: data inicial do intervalo.
    :param data_final: data final do intervalo.
    :param total_leituras: total de leituras a serem geradas para cada sensor.
    :return: lista de tuplas contendo o sensor e suas leituras geradas.
    """

    retorno:list[tuple[Sensor, list[LeituraSensor]]] = []

    criar_sensores = criar_sensores_padrao()

    for sensor in criar_sensores:

        tipo = TipoSensor.get_from_id(sensor.tipo_sensor_id)

        leituras = criar_dados_leitura(
            data_inicial=data_inicial,
            data_final=data_final,
            sensor_id=sensor.id,
            total_leituras=total_leituras,
            tipo=tipo.tipo.get_type_for_generation(),
            minimo=None if tipo.tipo.get_range_for_generation() is None else tipo.tipo.get_range_for_generation()[0],
            maximo=None if tipo.tipo.get_range_for_generation() is None else tipo.tipo.get_range_for_generation()[1]
        )
        retorno.append((sensor, leituras))

    return retorno

