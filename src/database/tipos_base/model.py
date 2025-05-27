from abc import abstractmethod
from typing import Self, Optional, List
from random import choice, randint
import pandas as pd
from sqlalchemy.orm import DeclarativeBase
from enum import Enum
from src.database.tipos_base.database import Database
from src.database.tipos_base.model_mixins.crud import _ModelCrudMixin # noqa
from src.database.tipos_base.model_mixins.display import _ModelDisplayMixin # noqa
from src.database.tipos_base.model_mixins.fields import _ModelFieldsMixin # noqa
from src.database.tipos_base.model_mixins.serialization import _ModelSerializationMixin # noqa
from src.plots.plot_config import GenericPlot
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression
from sqlalchemy import String, Enum, Float, Boolean, Integer, DateTime
from datetime import datetime


#https://docs.sqlalchemy.org/en/20/orm/quickstart.html
class Model(DeclarativeBase,
            _ModelSerializationMixin,
            _ModelFieldsMixin,
            _ModelDisplayMixin,
            _ModelCrudMixin,
            ):

    __database_import_order__:int = 100000
    __generic_plot__:Optional[GenericPlot] = None

    @property
    @abstractmethod
    def id(self):
        """
        Este atributo deve ser definido na classe herdeira.

        exemplo:
        id: Mapped[int] = mapped_column(
             Sequence(f"{__tablename__}_SEQ_ID"),
             primary_key=True,
             autoincrement=True,
             nullable=False
         )
        """
        raise NotImplementedError("O atributo 'id' deve ser definido na classe herdeira.")

    def update_from_dict(self, data: dict) -> Self:
        """
        Atualiza os atributos da instância com os dados fornecidos em um dicionário.
        :param data: dict - Dados a serem usados para atualizar a instância.
        :return: Model - Instância atualizada.
        """
        for key, value in data.items():
            if key in self.field_names():
                setattr(self, key, value)

        return self

    def copy_with(self, **kwargs) -> Self:
        """
        Cria uma cópia da instância atual com os atributos modificados.
        :param kwargs: Atributos a serem alterados na cópia.
        :return: Nova instância com os atributos atualizados.
        """
        cls = type(self)
        new_instance = cls(**{**self.__dict__, **kwargs})
        new_instance.id = None  # Evita duplicar a chave primária
        return new_instance

    @classmethod
    def random(cls, nullable: bool = True) -> Self:
        """
        Cria uma nova instância da classe com valores aleatórios para os campos definidos.
        :return: Instância da classe com valores aleatórios.
        """

        data = {}

        for field in cls.fields():

            if field.name == 'id':
                # O campo 'id' é gerado automaticamente pelo banco de dados, não deve ser preenchido aqui
                continue

            if nullable and field.nullable:
                # 50% de chance de ser None
                if choice([True, False]):
                    data[field.name] = None
                    continue

            if isinstance(field.type, Enum):

                options = [item.value for item in field.type.enum_class]

                # Seleciona um valor aleatório do Enum
                data[field.name] = choice(options)

            elif isinstance(field.type, DateTime):
                # Data e hora aleatórias entre 2000-01-01 e 2023-12-30
                year = randint(2000, 2023)
                month = randint(1, 12)
                day = randint(1, 30)

                data[field.name] = datetime(year, month, day, randint(0, 23), randint(0, 59), randint(0, 59))

            elif isinstance(field.type, Integer):
                # Inteiro aleatório entre 0 e 100
                data[field.name] = randint(0, 100)
            elif isinstance(field.type, Float):
                # Float aleatório entre 0.0 e 100.0
                data[field.name] = round(randint(0, 100) + choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]), 2)
            elif isinstance(field.type, Boolean):
                # Booleano aleatório
                data[field.name] = choice([True, False])
            elif isinstance(field.type, String):
                # String aleatória com tamanho entre 1 e 10 caracteres
                data[field.name] = ''.join(choice('abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.upper()) for _ in range(randint(1, 10)))
            else:
                raise NotImplementedError(f"Tipo de campo '{field.type}' não suportado para geração aleatória.")

        return cls.from_dict(data)


    @classmethod
    def filter_dataframe(cls,
                         filters: Optional[List[BinaryExpression]] = None,
                         order_by: Optional[List[UnaryExpression]] = None,
                         select_fields: Optional[List[str]] = None,
                         as_display: bool = False,
                         ) -> pd.DataFrame:
        """
        Obtém os dados da instância formatados para plotagem.
        """

        # faz um query com o sqlalchemy filtrando pelos filters do generic_plot e ordernando pelos order_by do generic_plot

        with Database.get_session() as session:
            query = session.query(cls.__class__)

            if filters is not None:
                query = query.filter(*filters)

            if order_by:
                query = query.order_by(*order_by)

            else:
                # se não tiver order_by, ordena pelo id
                query = query.order_by(cls.id.asc())

            # limita os campos retornados
            campos_para_retornar = []

            if select_fields is None:
                campos_para_retornar = cls.fields()
            else:
                for field in select_fields:
                    if not hasattr(cls, field):
                        raise AttributeError(f"A classe {cls.__class__.__name__} não possui o atributo '{field}'.")
                    campos_para_retornar.append(getattr(cls, field))

            # como vai retornar apenas o dataframe para gerar o gráfico, não precisa retornar todos os campos da tabela,
            query = query.with_entities(campos_para_retornar)

            dataframe = pd.read_sql(query.statement, session.bind)

            if as_display:
                colum_names = {}
                for column in dataframe.columns:
                    colum_names[column] = cls.get_field_display_name(column)
                dataframe.rename(columns=colum_names)

            return dataframe
