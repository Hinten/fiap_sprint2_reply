from src.database.tipos_base.database import Database
from src.database.models.sensor import Sensor, TipoSensor, TipoSensorEnum

def criar_sensores_padrao() -> list[Sensor]:
    retorno: list[dict] = []

    with Database.get_session() as session:
        tipos_necessarios = []

        for tipo in TipoSensorEnum:
            tipos_necessarios.append({
                'tipo': tipo.value,
                'nome': str(tipo)
            })

        for tipo in tipos_necessarios:
            tipo_existente = session.query(TipoSensor).filter(
                TipoSensor.tipo == tipo['tipo']
            ).first()

            if not tipo_existente:
                tipo_existente = TipoSensor(
                    nome=tipo['nome'],
                    tipo=tipo['tipo']
                )
                session.add(tipo_existente)
                session.commit()

            sensor_existente = session.query(Sensor).filter(
                Sensor.tipo_sensor_id == tipo_existente.id
            ).first()

            if not sensor_existente:
                novo_sensor = Sensor(
                    nome=f"Sensor {tipo['nome']}",
                    tipo_sensor_id=tipo_existente.id,
                    descricao="Criado automaticamente pelo sistema"
                )
                session.add(novo_sensor)
                session.flush()
                session.refresh(novo_sensor)
                retorno.append(novo_sensor.to_dict())
            else:
                session.refresh(sensor_existente)
                retorno.append(sensor_existente.to_dict())

        session.commit()
        print(f"Total de sensores criados: {len(retorno)}")

    return list(map(lambda x: Sensor.from_dict(x), retorno))