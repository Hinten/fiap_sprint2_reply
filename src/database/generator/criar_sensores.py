from src.database.tipos_base.database import Database
from src.database.models.sensor import Sensor, TipoSensor

def criar_sensores_padrao(plantio_id: int):
    with Database.get_session() as session:
        tipos_necessarios = [
            {'tipo': 'H', 'nome': 'Sensor Umidade Solo'},
            {'tipo': 'pH', 'nome': 'Sensor pH Solo'}
        ]
        
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
                Sensor.plantio_id == plantio_id,
                Sensor.tipo_sensor_id == tipo_existente.id
            ).first()
            
            if not sensor_existente:
                novo_sensor = Sensor(
                    nome=f"{tipo['nome']} - Plantio {plantio_id}",
                    tipo_sensor_id=tipo_existente.id,
                    plantio_id=plantio_id,
                    descricao="Criado automaticamente pelo sistema"
                )
                session.add(novo_sensor)
        
        session.commit()
        print(f"Sensores padrão criados/verificados para plantio {plantio_id}")
