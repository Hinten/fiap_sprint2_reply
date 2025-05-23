from sqlalchemy import Sequence, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.tipos_base.model import Model

class Unidade(Model):
    """Representa uma unidade de medida"""

    __tablename__ = 'UNIDADE'
    __database_import_order__ = 1

    @classmethod
    def display_name(cls) -> str:
        return "Unidade de Medida"

    @classmethod
    def display_name_plural(cls) -> str:
        return "Unidades de Medida"

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        info={
            'label': 'Nome'
        },
        comment="Nome da unidade de medida"
    )

    multiplicador: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        unique=False,
        info={
            'label': 'Multiplicador'
        },
        comment="Multiplicador da unidade de medida, Ex.: 1000 para kg, 1 para g e 0.001 para mg"
    )

    #irrigacoes = relationship('Irrigacao', back_populates='unidade')
    sensors = relationship('Sensor', back_populates='unidade')

    def __str__(self):
        return f"{self.id} - {self.nome}"