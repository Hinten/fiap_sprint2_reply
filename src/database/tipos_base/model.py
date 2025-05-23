import json
from abc import abstractmethod
from sqlalchemy import inspect, Column, String, Enum, Float, Boolean, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
import pandas as pd
from typing import List
from src.database.tipos_base.database import Database


#https://docs.sqlalchemy.org/en/20/orm/quickstart.html
class Model(DeclarativeBase):

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

    __menu_order__ = 100000
    __menu_group__: str or None = None
    __database_import_order__ = 100000

    @classmethod
    def field_names(cls) -> list[str]:
        """
        Retorna os campos da classe.
        :return: List[str] - Lista com os nomes dos campos.
        """
        return [column.name for column in inspect(cls).c]

    @classmethod
    def fields(cls) -> list[Column]:
        """
        Retorna os campos da classe.
        :return: List[str] - Lista com os nomes dos campos.
        """
        return [column for column in inspect(cls).c]


    @classmethod
    def get_field(cls, field_name: str) -> Column:
        """
        Retorna o campo da classe com base no nome fornecido.
        :param field_name: str - Nome do campo.
        :return: Column - Campo correspondente ao nome fornecido.
        """
        for column in inspect(cls).c:
            if column.name == field_name:
                return column

        raise ValueError(f"Campo '{field_name}' não encontrado na classe '{cls.__name__}'.")


    @classmethod
    def get_field_display_name(cls, field_name: str | Column) -> str:
        """
        Retorna o nome de exibição do campo com base no nome fornecido.
        :param field_name: str - Nome do campo.
        :return: str - Nome de exibição do campo.
        """

        if isinstance(field_name, Column):
            field = field_name
        else:
            field = cls.get_field(field_name)

        return field.info.get('label', field.name).title() if field.info else field.name.title()

    @classmethod
    def validate_field(cls, field_name: str, value) -> str | None:
        """
        Valida o valor de um campo com base no tipo definido na classe.
        :param field_name: str - Nome do campo.
        :param value: Valor a ser validado.
        :return: str | None - Mensagem de erro se houver, ou None se o valor for válido.
        """

        field = cls.get_field(field_name)

        if field.nullable and value is None:
            return None

        if field.nullable is False and value is None:
            return f"O campo '{cls.get_field_display_name(field)}' não pode ser nulo."

        if isinstance(field.type, Column):
            if not isinstance(value, field.type.python_type):
                return f"Valor inválido para o campo '{cls.get_field_display_name(field)}'. Esperado: {field.type.python_type.__name__}."


        if isinstance(field.type, String):
            if len(value) > field.type.length:
                return f"Valor muito longo para o campo '{cls.get_field_display_name(field)}'. Máximo: {field.type.length} caracteres."

        return None

    @classmethod
    def is_valid(cls, data: dict) -> bool:
        """
        Valida os dados fornecidos para a classe.
        :param data: dict - Dados a serem validados.
        :return: bool - True se os dados forem válidos, False caso contrário.
        """
        for field_name, value in data.items():
            error = cls.validate_field(field_name, value)
            if error:
                return False

        return True

    def to_dict(self):
        """
        Converte a instância do modelo em um dicionário.
        :return: dict - Dicionário com os atributos da instância.
        """
        return {column.key: getattr(self, column.key) for column in inspect(self).mapper.column_attrs}

    @classmethod
    def from_dict(cls, data: dict):
        """
        Cria uma instância do modelo a partir de um dicionário.
        :param data: dict - Dicionário com os dados para criar a instância.
        :return: Model - Instância do modelo.
        """

        return cls(**data)

    def to_json(self, indent = 4):
        return  json.dumps(self.to_dict(), indent=indent)

    def update_from_dict(self, data: dict):
        """
        Atualiza os atributos da instância com os dados fornecidos em um dicionário.
        :param data: dict - Dados a serem usados para atualizar a instância.
        :return: Model - Instância atualizada.
        """
        for key, value in data.items():
            if key in self.field_names():
                setattr(self, key, value)

        return self

    def copy_with(self, **kwargs):
        """
        Cria uma cópia da instância atual com os atributos modificados.
        :param kwargs: Atributos a serem alterados na cópia.
        :return: Nova instância com os atributos atualizados.
        """
        cls = type(self)
        new_instance = cls(**{**self.__dict__, **kwargs})
        new_instance.id = None  # Evita duplicar a chave primária
        return new_instance

    def save(self) -> 'Model':
        """
        Cria ou atualiza a instância no banco de dados.
        :return: Model - Instância salva.
        """

        with Database.get_session() as session:
            session.add(self)
            session.commit()
            print(self.id)

        return self

    def merge(self) -> 'Model':
        """
        Cria ou atualiza a instância no banco de dados.
        :return: Model - Instância salva.
        """

        with Database.get_session() as session:
            session.merge(self)
            session.commit()
            print(self.id)

        return self

    def update(self, **kwargs) -> 'Model':
        """
        Atualiza os atributos da instância com os valores fornecidos.
        :param kwargs: Atributos a serem atualizados.
        :return: Model - Instância atualizada.
        """
        for key, value in kwargs.items():
            if key in self.field_names():
                setattr(self, key, value)

        with Database.get_session() as session:
            session.commit()

        return self

    def delete(self) -> 'Model':
        """
        Remove a instância do banco de dados.
        :return: Model - Instância removida.
        """
        with Database.get_session() as session:
            session.delete(self)
            session.commit()

        return self

    @classmethod
    def get_from_id(cls, id:int) -> 'Model':
        """
        Busca uma instância pelo ID.
        :param id: int - ID da instância a ser buscada.
        :return: Model - Instância encontrada ou None.
        """
        with Database.get_session() as session:
            return session.query(cls).filter(cls.id == id).one()

    @classmethod
    def as_dataframe(cls):
        """
        Retorna os dados da tabela como um DataFrame.
        :return: DataFrame - Dados da tabela.
        """
        with Database.get_session() as session:
            query = session.query(cls).order_by(cls.id)
            return pd.read_sql(query.statement, session.bind)

    @classmethod
    def from_dataframe(cls, data:pd.DataFrame) -> List['Model']:
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

                    data[field.name] = None if data_raw.get(field.name) is None else field.type.enum_class(data_raw[field.name])

                elif isinstance(field.type, Float):
                    data[field.name] = data_raw.get(field.name)

                elif isinstance(field.type, Integer):
                    data[field.name] = data_raw.get(field.name)

                elif isinstance(field.type, Boolean):
                    data[field.name] = data_raw.get(field.name)

                elif isinstance(field.type, String):
                    data[field.name] = data_raw.get(field.name)

                elif isinstance(field.type, DateTime):
                    data[field.name] = None if data_raw.get(field.name) is None else pd.to_datetime(data_raw[field.name], errors='coerce')

                else:
                    data[field.name] = data_raw.get(field.name)

            #converte na do pandas para None e cria a instancia

            instance = cls(**data)
            instances.append(instance)
        return instances



    @classmethod
    def as_dataframe_display(cls):
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

    @classmethod
    def all(cls) -> list['Model']:
        """
        Retorna todos os registros da tabela.
        :return: list[Model] - Lista de instâncias do modelo.
        """
        with Database.get_session() as session:
            #order by id
            return session.query(cls).order_by(cls.id).all()


    @classmethod
    def display_name(cls) -> str:
        """
        Retorna o nome da tabela.
        :return: str - Nome da tabela.
        """
        return cls.__name__.title()

    @classmethod
    def display_name_plural(cls) -> str:
        """
        Retorna o nome da tabela no plural.
        :return: str - Nome da tabela no plural.
        """
        return f"{cls.__name__.title()}s"