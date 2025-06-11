from pydantic import BaseModel
from src.database.tipos_base.database import Database
from src.database.models.sensor import Sensor, TipoSensor, TipoSensorEnum, LeituraSensor
from datetime import datetime
from fastapi import APIRouter

receber_router = APIRouter()


class LeituraRequest(BaseModel):
    serial: str
    lux: float or None
    temperatura: float or None
    vibracao_media: float or None
    acelerometro_x: float or None # não utilizado
    acelerometro_y: float or None # não utilizado
    acelerometro_z: float or None # não utilizado


@receber_router.post("/")
def receber_leitura(request: LeituraRequest):

    print(f"Recebendo leitura para o sensor com serial: {request.serial}", request)

    now = datetime.now()

    with Database.get_session() as session:
        sensores = session.query(Sensor).filter(Sensor.cod_serial == request.serial).filter().all()

        if not sensores:
            return {
                "status": "error",
                "message": f"Sensor com serial '{request.serial}' não encontrado."
            }

        for sensor in sensores:

            tipo = session.query(TipoSensor).filter(TipoSensor.id == sensor.tipo_sensor_id).first()

            if not tipo:
                return {
                    "status": "error",
                    "message": f"Tipo de sensor para o sensor com serial '{request.serial}' não encontrado."
                }

            if tipo.tipo == TipoSensorEnum.LUX and request.lux is not None:
                nova_leitura = LeituraSensor(
                    sensor_id=sensor.id,
                    data_leitura=now,
                    valor= request.lux
                )
            elif tipo.tipo == TipoSensorEnum.TEMPERATURA and request.temperatura is not None:
                nova_leitura = LeituraSensor(
                    sensor_id=sensor.id,
                    data_leitura=now,
                    valor=request.temperatura
                )
            elif tipo.tipo == TipoSensorEnum.VIBRACAO and request.vibracao_media is not None:
                nova_leitura = LeituraSensor(
                    sensor_id=sensor.id,
                    data_leitura=now,
                    valor=request.vibracao_media
                )
            else:
                continue
            session.add(nova_leitura)
            print('Nova leitura salva:', nova_leitura)

        session.commit()


    return {
        "status": "success",
        "message": "Leitura recebida com sucesso",
    }
