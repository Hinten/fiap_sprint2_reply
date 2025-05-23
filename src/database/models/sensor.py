from enum import StrEnum
from typing import List
from sqlalchemy import Sequence, String, Text, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models.fazenda import Plantio
from src.database.models.unidade import Unidade
from src.database.tipos_base.database import Database
from src.database.tipos_base.model import Model
from datetime import datetime, date, time, timedelta

class TipoSensorEnum(StrEnum):
    FOSFORO = "P"
    POTASSIO = "K"
    PH = "pH"
    UMIDADE = "H"
    RELE = "Rele"

    def __str__(self):

        if self.value == "P":
            return "Fósforo"
        if self.value == "K":
            return "Potássio"
        if self.value == "pH":
            return "PH"
        if self.value == "H":
            return "Umidade"
        if self.value == "Rele":
            return "Estado do Relé"

        return super().name


class TipoSensor(Model):
    """Representa um tipo de sensor que pode ser utilizado em uma plantação."""

    __tablename__ = 'TIPO_SENSOR'
    __menu_group__ = "Sensores"
    __menu_order__ = 1
    __database_import_order__ = 10

    @classmethod
    def display_name(cls) -> str:
        return "Tipo de Sensor"

    @classmethod
    def display_name_plural(cls) -> str:
        return "Tipos de Sensores"

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        info={
            'label': 'Nome'
        },
        comment="Ex.: Fósforo, Potássio, pH, Umidade, Rele"
    )

    tipo: Mapped[TipoSensorEnum] = mapped_column(
        Enum(TipoSensorEnum, length=15),
        nullable=False,
        unique=False,
        info={
            'label': 'Tipo'
        },
        comment="Tipo do sensor, Ex.: Fósforo, Potássio, pH, Umidade, Rele"
    )

    sensors: Mapped[list['Sensor']] = relationship('Sensor', back_populates='tipo_sensor')

    def __str__(self):
        return f"{self.id} - {self.nome}"

class Sensor(Model):
    """Representa um sensor que pode ser utilizado em uma plantação."""

    __tablename__ = 'SENSOR'
    __menu_group__ = "Sensores"
    __menu_order__ = 2
    __database_import_order__ = 11

    @classmethod
    def display_name_plural(cls) -> str:
        return "Sensores"

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    tipo_sensor_id: Mapped[int] = mapped_column(
        ForeignKey('TIPO_SENSOR.id'),
        nullable=False,
        info={
            'label': 'Tipo de Sensor'
        },
        comment="ID do tipo de sensor associado"
    )

    tipo_sensor: Mapped[TipoSensor] = relationship('TipoSensor', back_populates='sensors')

    plantio_id: Mapped[int] = mapped_column(
        ForeignKey('PLANTIO.id'),
        nullable=True,
        info={
            'label': 'Plantio'
        },
        comment="ID do plantio associado"
    )

    plantio: Mapped[Plantio] = relationship('Plantio', back_populates='sensores')

    nome: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        info={
            'label': 'Nome'
        },
        comment="Nome do sensor"
    )

    descricao: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        unique=False,
        info={
            'label': 'Descrição'
        },
        comment="Descrição do sensor"
    )

    data_instalacao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        unique=False,
        info={
            'label': 'Data de Instalação'
        },
        comment="Data de instalação do sensor"
    )

    unidade_id: Mapped[int] = mapped_column(
        ForeignKey('UNIDADE.id'),
        nullable=True,
        info={
            'label': 'Unidade'
        },
        comment="ID da unidade de medida associada"
    )

    unidade: Mapped[Unidade] = relationship('Unidade', back_populates='sensors')

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        unique=False,
        info={
            'label': 'Latitude'
        },
        comment="Latitude do sensor"
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        unique=False,
        info={
            'label': 'Longitude'
        },
        comment="Longitude do sensor"
    )


    leituras: Mapped[list['LeituraSensor']] = relationship('LeituraSensor', back_populates='sensor')

    irrigacoes: Mapped[list['Irrigacao']] = relationship('Irrigacao', back_populates='sensor')

    def __str__(self):
        return f"{self.id} - {self.nome}"

    @classmethod
    def filter_by_tiposensor(cls, tipo_sensor: TipoSensorEnum) -> List['Sensor']:
        """Retorna o tipo de sensor correspondente ao enum."""
        with Database.get_session() as session:
            # pega os tipos de sensores de umidade
            tipo_sensor = session.query(TipoSensor).filter(TipoSensor.tipo == tipo_sensor).all()
            tipo_ids = [ts.id for ts in tipo_sensor]

            sensores = session.query(Sensor).filter(Sensor.tipo_sensor_id.in_(tipo_ids)).all()

            return sensores


class LeituraSensor(Model):
    """Representa uma leitura de um sensor em um determinado momento."""

    __tablename__ = 'LEITURA_SENSOR'
    __menu_group__ = "Sensores"
    __menu_order__ = 3
    __database_import_order__ = 12

    @classmethod
    def display_name(cls) -> str:
        return "Leitura de Sensor"

    @classmethod
    def display_name_plural(cls) -> str:
        return "Leituras de Sensores"

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    sensor_id: Mapped[int] = mapped_column(
        ForeignKey('SENSOR.id'),
        nullable=False,
        info={
            'label': 'Sensor'
        },
        comment="ID do sensor associado"
    )

    sensor: Mapped[Sensor] = relationship('Sensor', back_populates='leituras')

    data_leitura: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        info={
            'label': 'Data da Leitura'
        },
        comment="Data da leitura do sensor"
    )

    valor : Mapped[float] = mapped_column(
        Float,
        nullable=False,
        info={
            'label': 'Valor'
        },
        comment="Valor da leitura do sensor"
    )

    @classmethod
    def get_leituras_for_sensor(cls, sensor_id: int, data_inicial: date, data_final: date):
        with Database.get_session() as session:
            leituras = session.query(LeituraSensor).filter(
                LeituraSensor.sensor_id == sensor_id,
                LeituraSensor.data_leitura >= datetime.combine(data_inicial, time(0, 0, 0)),
                LeituraSensor.data_leitura <= datetime.combine(data_final, time(23, 59, 59, 999999))
            ).order_by(LeituraSensor.data_leitura).all()

            return leituras