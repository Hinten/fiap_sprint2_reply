from pydantic import BaseModel
from src.database.tipos_base.database import Database
from src.database.models.sensor import Sensor, TipoSensor, TipoSensorEnum, LeituraSensor
from datetime import datetime
from fastapi import APIRouter

receber_router = APIRouter()


class LeituraRequest(BaseModel):
    serial: str
    bueiro: float or None
    leito: float or None
    rele: bool or None


@receber_router.post("/")
def receber_leitura(item: LeituraRequest):

    print(f"Recebendo leitura para o sensor com serial: {item.serial}", item)

    now = datetime.now()

    with Database.get_session() as session:
        sensores = session.query(Sensor).filter(Sensor.cod_serial == item.serial).filter().all()

        if not sensores:
            return {
                "status": "error",
                "message": f"Sensor com serial '{item.serial}' não encontrado."
            }

        for sensor in sensores:

            tipo = session.query(TipoSensor).filter(TipoSensor.id == sensor.tipo_sensor_id).first()

            if not tipo:
                return {
                    "status": "error",
                    "message": f"Tipo de sensor para o sensor com serial '{item.serial}' não encontrado."
                }

            if tipo.tipo == TipoSensorEnum.BUEIRO and item.bueiro is not None:
                nova_leitura = LeituraSensor(
                    sensor_id=sensor.id,
                    data_leitura=now,
                    valor= item.bueiro
                )
            elif tipo.tipo == TipoSensorEnum.LEITO and item.leito is not None:
                nova_leitura = LeituraSensor(
                    sensor_id=sensor.id,
                    data_leitura=now,
                    valor=item.leito
                )
            else:
                continue
            print('Salvando nova leitura:', nova_leitura)
            session.add(nova_leitura)

        session.commit()


    return {
        "status": "success",
        "message": "Leitura recebida com sucesso",
    }
