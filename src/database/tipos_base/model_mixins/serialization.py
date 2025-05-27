"""
AVISO: Este arquivo define apenas mixins para uso em herança múltipla.
NÃO importe este arquivo diretamente como módulo principal.
"""
import json
from typing import Self
from sqlalchemy import inspect,  String, Enum, Float, Boolean, Integer, DateTime
import pandas as pd
from typing import List
from src.database.tipos_base.database import Database
from src.database.tipos_base.model_mixins.fields import _ModelFieldsMixin


class _ModelSerializationMixin(_ModelFieldsMixin):
    """
    Mixin onde os métodos de serialização são definidos.
    """

    def to_dict(self) -> dict:
        """
        Converte a instância do modelo em um dicionário.
        :return: dict - Dicionário com os atributos da instância.
        """
        return {column.key: getattr(self, column.key) for column in inspect(self).mapper.column_attrs}

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """
        Cria uma instância do modelo a partir de um dicionário.
        :param data: dict - Dicionário com os dados para criar a instância.
        :return: Model - Instância do modelo.
        """

        return cls(**data)

    def to_json(self, indent=4):
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def as_dataframe(cls) -> pd.DataFrame:
        """
        Retorna os dados da tabela como um DataFrame.
        :return: DataFrame - Dados da tabela.
        """
        with Database.get_session() as session:
            query = session.query(cls).order_by(cls.id)
            return pd.read_sql(query.statement, session.bind)

    @classmethod
    def from_dataframe(cls, data: pd.DataFrame) -> List[Self]:
        """
        Cria uma lista de instâncias do modelo a partir de um DataFrame.
        :param data: DataFrame - Dados a serem convertidos.
        :return: List[Model] - Lista de instâncias do modelo.
        """
        instances = []
        for _, row in data.iterrows():
            data = {}
            row = row.where(pd.notnull(row), None)
            data_raw = row.to_dict()

            for field in cls.fields():

                if isinstance(field.type, Enum):

                    data[field.name] = None if data_raw.get(field.name) is None else field.type.enum_class(
                        data_raw[field.name])

                elif isinstance(field.type, Float):
                    data[field.name] = data_raw.get(field.name)

                elif isinstance(field.type, Integer):
                    data[field.name] = data_raw.get(field.name)

                elif isinstance(field.type, Boolean):
                    data[field.name] = data_raw.get(field.name)

                elif isinstance(field.type, String):
                    data[field.name] = data_raw.get(field.name)

                elif isinstance(field.type, DateTime):
                    data[field.name] = None if data_raw.get(field.name) is None else pd.to_datetime(
                        data_raw[field.name], errors='coerce')

                else:
                    data[field.name] = data_raw.get(field.name)

            # converte na do pandas para None e cria a instancia

            instance = cls(**data)
            instances.append(instance)
        return instances

    @classmethod
    def as_dataframe_display(cls) -> pd.DataFrame:
        """
        Retorna os dados da tabela como um DataFrame com os nomes de exibição.
        :return: DataFrame - Dados da tabela com os nomes de exibição.
        """

        dataframe = cls.as_dataframe()

        colum_names = {}

        for column in cls.fields():
            colum_names[column.name] = cls.get_field_display_name(column.name)

            if isinstance(column.type, Enum):
                dataframe[column.name] = dataframe[column.name].apply(lambda x: str(column.type.enum_class(x)))

        return dataframe.rename(columns=colum_names)