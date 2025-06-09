from enum import StrEnum
from typing import List, Self, Union
from datetime import datetime, date, time, timedelta

from sqlalchemy import Sequence, String, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

import numpy as np

from src.database.tipos_base.database import Database
from src.database.tipos_base.model import Model
from src.database.tipos_base.model_mixins.display import SimpleTableFilter
from src.plots.plot_config import GenericPlot, PlotField, TipoGrafico, OrderBy


class TipoSensorEnum(StrEnum):
    PROFUNDIDADE = "P"
    BUEIRO = "B"
    LEITO = "L"

    def __str__(self):
        return {
            "P": "Profundidade",
            "B": "Nível Bueiro (LDR)",
            "L": "Nível Leito (Ultrassônico)",
        }.get(self.value, super().__str__())

    def get_type_for_generation(self) -> Union[type[float], type[int], type[bool]]:
        return {
            "P": float,
            "B": float,
            "L": float,
        }.get(self.value, float)

    def get_range_for_generation(self) -> Union[tuple[float, float], None]:
        return {
            "P": (0.0, 200.0),
            "B": (0.0, 400.0),
            "L": (0.0, 500.0)
        }.get(self.value, None)


class TipoSensor(Model):
    __tablename__ = 'TIPO_SENSOR'
    __menu_group__ = "Sensores"
    __menu_order__ = 1
    __database_import_order__ = 10

    __table_view_filters__ = [
        SimpleTableFilter(field='tipo', label='Tipo', operator='==')
    ]

    @classmethod
    def display_name(cls) -> str:
        return "Tipo de Sensor"

    @classmethod
    def display_name_plural(cls) -> str:
        return "Tipos de Sensores"

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"), primary_key=True, autoincrement=True, nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, info={'label': 'Nome'},
        comment="Ex.: Fósforo, Potássio, pH, Umidade, Rele"
    )

    tipo: Mapped[TipoSensorEnum] = mapped_column(
        Enum(TipoSensorEnum, length=15), nullable=False, info={'label': 'Tipo'},
        comment="Tipo do sensor, Ex.: Profundidade, Bueiro, etc."
    )

    sensors: Mapped[List['Sensor']] = relationship('Sensor', back_populates='tipo_sensor')

    def __str__(self):
        return f"{self.id} - {self.nome}"


class Sensor(Model):
    __tablename__ = 'SENSOR'
    __menu_group__ = "Sensores"
    __menu_order__ = 2
    __database_import_order__ = 11

    __table_view_filters__ = [
        SimpleTableFilter(field='tipo_sensor_id', label='Tipo de Sensor', operator='==')
    ]

    @classmethod
    def display_name_plural(cls) -> str:
        return "Sensores"

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"), primary_key=True, autoincrement=True, nullable=False
    )

    tipo_sensor_id: Mapped[int] = mapped_column(
        ForeignKey('TIPO_SENSOR.id'), nullable=False, info={'label': 'Tipo de Sensor'}
    )

    tipo_sensor: Mapped[TipoSensor] = relationship('TipoSensor', back_populates='sensors')

    nome: Mapped[str] = mapped_column(
        String(255), nullable=True, unique=True, info={'label': 'Nome'},
        comment="Nome do sensor"
    )

    cod_serial: Mapped[str] = mapped_column(
        String(255), nullable=True, unique=False, info={'label': 'Código Serial'},
        comment="Código serial do sensor, usado para identificação única"
    )

    descricao: Mapped[str] = mapped_column(
        String(255), nullable=True, info={'label': 'Descrição'},
        comment="Descrição do sensor"
    )

    data_instalacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, info={'label': 'Data de Instalação'},
        comment="Data de instalação do sensor"
    )

    latitude: Mapped[float] = mapped_column(
        Float, nullable=True, info={'label': 'Latitude'},
        comment="Latitude do sensor"
    )

    longitude: Mapped[float] = mapped_column(
        Float, nullable=True, info={'label': 'Longitude'},
        comment="Longitude do sensor"
    )

    leituras: Mapped[List['LeituraSensor']] = relationship('LeituraSensor', back_populates='sensor', cascade="all, delete-orphan")

    def __str__(self):
        return f"{self.id} - {self.nome}"

    @classmethod
    def filter_by_tiposensor(cls, tipo_sensor: TipoSensorEnum) -> List['Sensor']:
        with Database.get_session() as session:
            tipo_sensor_obj = session.query(TipoSensor).filter(TipoSensor.tipo == tipo_sensor).all()
            tipo_ids = [ts.id for ts in tipo_sensor_obj]
            return session.query(Sensor).filter(Sensor.tipo_sensor_id.in_(tipo_ids)).all()


class LeituraSensor(Model):
    __tablename__ = 'LEITURA_SENSOR'
    __menu_group__ = "Sensores"
    __menu_order__ = 3
    __database_import_order__ = 12

    __table_view_filters__ = [
        SimpleTableFilter(field='sensor_id', label='Sensor', operator='=='),
        SimpleTableFilter(field='data_leitura', label='Data da Leitura Inicial', operator='>=', optional=True),
        SimpleTableFilter(field='data_leitura', label='Data da Leitura Final', operator='<=', optional=True)
    ]

    __generic_plot__ = GenericPlot(
        eixo_x=[PlotField(field='data_leitura', display_name='Data da Leitura')],
        eixo_y=[PlotField(field='valor', display_name='Valor')],
        tipo=TipoGrafico.LINHA,
        title="Gráfico de Leituras do Sensor",
        filters=[
            SimpleTableFilter(field='sensor_id', operator='==', label='Sensor', optional=False),
            SimpleTableFilter(field='data_leitura', name='data_leitura_inicial', operator='>=', label='Data da Leitura Inicial'),
            SimpleTableFilter(field='data_leitura', name='data_leitura_final', operator='<=', label='Data da Leitura Final'),
        ],
        order_by=[OrderBy(field='data_leitura', asc=True)]
    )

    @classmethod
    def display_name(cls) -> str:
        return "Leitura de Sensor"

    @classmethod
    def display_name_plural(cls) -> str:
        return "Leituras de Sensores"

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"), primary_key=True, autoincrement=True, nullable=False
    )

    sensor_id: Mapped[int] = mapped_column(
        ForeignKey('SENSOR.id'), nullable=False, info={'label': 'Sensor'}
    )

    sensor: Mapped[Sensor] = relationship('Sensor', back_populates='leituras')

    data_leitura: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, info={'label': 'Data da Leitura'}
    )

    valor: Mapped[float] = mapped_column(
        Float, nullable=False, info={'label': 'Valor'}
    )

    @classmethod
    def get_leituras_for_sensor(cls, sensor_id: int, data_inicial: date, data_final: date) -> List['LeituraSensor']:
        with Database.get_session() as session:
            return session.query(cls).filter(
                cls.sensor_id == sensor_id,
                cls.data_leitura >= datetime.combine(data_inicial, time.min),
                cls.data_leitura <= datetime.combine(data_final, time.max)
            ).order_by(cls.data_leitura).all()

    @classmethod
    def random_range(cls, nullable: bool = True, quantity: int = 100, **kwargs) -> List[Self]:
        data_inicial = kwargs.get('values_by_name', {}).get(
            'data_leitura_inicial', (datetime.now() - timedelta(days=7)).isoformat()
        )
        data_inicial = datetime.fromisoformat(data_inicial) if isinstance(data_inicial, str) else data_inicial

        return [
            cls(
                sensor_id=1,
                data_leitura=data_inicial + timedelta(days=i / 7),
                valor=np.random.choice(np.arange(0, 100, 0.01))
            )
            for i in range(quantity)
        ]
