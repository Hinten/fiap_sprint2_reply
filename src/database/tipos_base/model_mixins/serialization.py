"""
AVISO: Este arquivo define apenas mixins para uso em herança múltipla.
NÃO importe este arquivo diretamente como módulo principal.
"""
import json
import logging
from io import BytesIO
from typing import Self, Optional
from sqlalchemy import inspect, String, Enum, Float, Boolean, Integer, DateTime, BinaryExpression, UnaryExpression, LargeBinary
import pandas as pd
from typing import List
from src.database.tipos_base.database import Database
from src.database.tipos_base.model_mixins.fields import _ModelFieldsMixin
from PIL import Image
import base64


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

                elif isinstance(field.type, LargeBinary):
                    # LargeBinary pode ser convertido para bytes

                    if isinstance(data_raw.get(field.name), bytes):
                        data[field.name] = data_raw.get(field.name)

                    elif isinstance(data_raw.get(field.name), str):

                        data[field.name] = base64.b64decode(data_raw.get(field.name))

                    else:
                        data[field.name] = data_raw.get(field.name)

                else:
                    data[field.name] = data_raw.get(field.name)

            # converte na do pandas para None e cria a instancia

            instance = cls(**data)
            instances.append(instance)
        return instances

    @classmethod
    def as_dataframe_all(cls, select_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Retorna os dados da tabela como um DataFrame.
        :return: DataFrame - Dados da tabela.
        """
        with Database.get_session() as session:
            query = session.query(cls).order_by(cls.id)

            campos_para_retornar = []

            if select_fields is None:
                campos_para_retornar = cls.fields()
            else:
                for field in select_fields:
                    if not hasattr(cls, field):
                        raise AttributeError(f"A classe {cls.__class__.__name__} não possui o atributo '{field}'.")
                    campos_para_retornar.append(getattr(cls, field))

            query = query.with_entities(*campos_para_retornar)

            df = pd.read_sql(query.statement, session.bind)

            # Converte campos LargeBinary para base64
            for field in campos_para_retornar:
                # field pode ser Column ou InstrumentedAttribute
                column = getattr(field, 'property', None)
                if column is not None:
                    column = getattr(column, 'columns', [None])[0]
                else:
                    column = getattr(field, 'expression', None)
                if column is not None and hasattr(column, 'type') and isinstance(column.type, LargeBinary):
                    col_name = field.key if hasattr(field, 'key') else field.name
                    if col_name in df.columns:
                        df[col_name] = df[col_name].apply(
                            lambda x: base64.b64encode(x).decode('utf-8') if isinstance(x, (bytes, bytearray)) and x is not None else x
                        )

            return df

    @classmethod
    def as_dataframe_display_all(cls, select_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Retorna os dados da tabela como um DataFrame com os nomes de exibição.
        :return: DataFrame - Dados da tabela com os nomes de exibição.
        """

        dataframe = cls.as_dataframe_all(select_fields)

        colum_names = {}

        for column in cls.fields():

            if select_fields is not None and column.name not in select_fields:
                continue

            colum_names[column.name] = cls.get_field_display_name(column.name)

            if isinstance(column.type, Enum):
                dataframe[column.name] = dataframe[column.name].apply(lambda x: str(column.type.enum_class(x)))

        return dataframe.rename(columns=colum_names)



    @classmethod
    def filter_dataframe(cls,
                         filters: Optional[List[BinaryExpression]] = None,
                         order_by: Optional[List[UnaryExpression]] = None,
                         select_fields: Optional[List[str]] = None,
                         as_display: bool = False,
                         offset: Optional[int] = None,
                         limit: Optional[int] = None
                         ) -> pd.DataFrame:
        """
        Obtém os dados da instância formatados para plotagem.
        """

        # faz um query com o sqlalchemy filtrando pelos filters do generic_plot e ordernando pelos order_by do generic_plot

        with Database.get_session() as session:
            query = session.query(cls)

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
            query = query.with_entities(*campos_para_retornar)

            if offset is not None:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            dataframe = pd.read_sql(query.statement, session.bind)

            if as_display:
                colum_names = {}
                for column in dataframe.columns:

                    colum_names[column] = cls.get_field_display_name(column)
                dataframe = dataframe.rename(columns=colum_names)
            return dataframe