from sqlalchemy import Sequence, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models.cultura import Cultura
from src.database.tipos_base.model import Model
from datetime import datetime

class Propriedade(Model):
    """Se refere a uma propriedade rural."""

    __tablename__ = 'PROPRIEDADE'
    __menu_group__ = 'Fazenda'
    __menu_order__ = 1
    __database_import_order__ = 1

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    cnpj: Mapped[str] = mapped_column(
        String(14),
        nullable=True,
        unique=False,
        info={
            'label': 'CNPJ'
        }
    )

    campos = relationship('Campo', back_populates='propriedade')

    def __str__(self):
        return f"{self.id} - {self.nome}"


class Campo(Model):
    """Se refere a um campo dentro de uma propriedade rural."""

    __tablename__ = 'CAMPO'
    __menu_group__ = 'Fazenda'
    __menu_order__ = 2
    __database_import_order__ = 2

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    propriedade_id: Mapped[int] = mapped_column(
        ForeignKey('PROPRIEDADE.id'),
        nullable=False,
        info={
            'label': 'Propriedade'
        },
    )

    propriedade: Mapped[Propriedade] = relationship('Propriedade', back_populates='campos')

    identificador: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    area_ha = mapped_column(
        Float,
        nullable=False,
        comment="Área do Campo em hectares (HA)",
        info={
            'label': 'Área (HA)'
        }
    )

    #todo colocar localizacao
    # localizacao: Mapped[str] = mapped_column(
    #     String(1000),
    #     nullable=True,
    #     unique=False,
    #     info={
    #         'label': 'Localização'
    #     }
    # )

    plantios = relationship('Plantio', back_populates='campo')

    def __str__(self):
        return f"{self.id} - {self.identificador}"


class Plantio(Model):
    """Se refere a um plantio que é realizado num campo."""

    __tablename__ = 'PLANTIO'
    __menu_group__ = 'Fazenda'
    __menu_order__ = 4
    __database_import_order__ = 3

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    nome = mapped_column(
        String(100),
        nullable=False,
        unique=False,
        info={
            'label': 'Nome'
        }
    )

    campo_id: Mapped[int] = mapped_column(
        ForeignKey('CAMPO.id'),
        nullable=False,
        info={
            'label': 'Campo'
        },
    )

    campo: Mapped[Campo] = relationship('Campo', back_populates='plantios')

    tipo_cultura: Mapped[int] = mapped_column(
        ForeignKey(Cultura.id),
        nullable=False,
        info={
            'label': 'Cultura'
        },
    )

    cultura: Mapped[Cultura] = relationship('Cultura', back_populates='plantios')

    data_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Data em que o plantio foi realizado (com timezone)",
        info={
            'label': 'Data de Início'
        }
    )

    data_fim = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data em que o plantio foi finalizado (com timezone)",
        info={
            'label': 'Data de Fim'
        }
    )

    observacao: Mapped[str] = mapped_column(
        Text(1000),
        nullable=True,
        unique=False,
        info={
            'label': 'Observação'
        }
    )

    #irrigacoes = relationship('Irrigacao', back_populates='plantio')

    sensores = relationship('Sensor', back_populates='plantio')
    aplicacoes_nutrientes = relationship('AplicacaoNutriente', back_populates='plantio')


    def __str__(self):
        return f"{self.id} - {self.nome}"