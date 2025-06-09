from pydantic import BaseModel
from src.database.models.sensor import Sensor, TipoSensor, TipoSensorEnum
from src.database.tipos_base.database import Database
from fastapi import APIRouter

init_router = APIRouter()


class InitSensorRequest(BaseModel):
    serial: str

@init_router.post('/')
def init_sensor(request:InitSensorRequest):
    """
    Cadastra o Sensor na base de dados
    """

    with Database.get_session() as session:

        for tipo in TipoSensorEnum:
            # Verifica se o tipo de sensor já existe
            tipo_sensor = session.query(TipoSensor).filter(
                TipoSensor.tipo == tipo.value
            ).first()

            if not tipo_sensor:
                # Cria o tipo de sensor se não existir
                tipo_sensor = TipoSensor(tipo=tipo.value, nome=str(tipo))
                session.add(tipo_sensor)
                session.commit()


            old_sensor = session.query(Sensor).filter(
                Sensor.cod_serial == request.serial,
                Sensor.tipo_sensor_id == tipo_sensor.id
            ).first()

            if old_sensor:
                # Se já existir um sensor com o mesmo serial e tipo, retorna uma mensagem
                continue

            # Cria o novo sensor com o tipo encontrado ou criado
            new_sensor = Sensor(
                nome=f"Sensor {tipo.value} - {request.serial}",
                cod_serial=request.serial,
                tipo_sensor_id=tipo_sensor.id,
                descricao="Sensor cadastrado via API",
            )

            session.add(new_sensor)

        session.commit()

    return {
        "status": "success",
        "message": "Sensor cadastrado com sucesso."
    }


