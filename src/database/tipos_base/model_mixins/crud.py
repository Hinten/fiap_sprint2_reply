from abc import abstractmethod

import logging

from src.database.tipos_base.database import Database
from sqlalchemy import inspect, BinaryExpression, UnaryExpression
from typing import Self

class _ModelCrudMixin:
    """
    Mixin class onde os métodos de CRUD são definidos.
    """

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError("O atributo 'id' deve ser definido na classe herdeira.")

    @classmethod
    def get_from_id(cls, id:int) -> Self:
        """
        Busca uma instância pelo ID.
        :param id: int - ID da instância a ser buscada.
        :return: Model - Instância encontrada ou None.
        """
        with Database.get_session() as session:
            return session.query(cls).filter(cls.id == id).one()

    @classmethod
    def all(cls) -> list[Self]:
        """
        Retorna todos os registros da tabela.
        :return: list[Model] - Lista de instâncias do modelo.
        """
        with Database.get_session() as session:
            #order by id
            return session.query(cls).order_by(cls.id).all()

    def save(self) -> Self:
        """
        Cria ou atualiza a instância no banco de dados.
        :return: Model - Instância salva.
        """

        with Database.get_session() as session:
            session.add(self)
            session.commit()
            logging.info(f"Registro salvo com sucesso: {self.id}")

        return self

    def merge(self) -> Self:
        """
        Cria ou atualiza a instância no banco de dados.
        :return: Model - Instância salva.
        """

        with Database.get_session() as session:
            session.merge(self)
            session.commit()

        return self

    def update(self, **kwargs) -> Self:
        """
        Atualiza os atributos da instância com os valores fornecidos.
        :param kwargs: Atributos a serem atualizados.
        :return: Model - Instância atualizada.
        """
        column_names = {col.key for col in inspect(self).mapper.column_attrs}
        for key, value in kwargs.items():
            if key in column_names:
                setattr(self, key, value)

        with Database.get_session() as session:
            session.commit()

        return self

    def delete(self) -> Self:
        """
        Remove a instância do banco de dados.
        :return: Model - Instância removida.
        """
        with Database.get_session() as session:
            session.delete(self)
            session.commit()

        return self

    @classmethod
    def count(cls, filters:list[BinaryExpression] or None = None) -> int:
        """
        Conta o número de registros na tabela.
        :param filters: list[BinaryExpression] or None - Filtros a serem aplicados na contagem.
        :return: int - Número de registros.
        """
        with Database.get_session() as session:

            if filters:
                return session.query(cls).filter(*filters).count()

            return session.query(cls).count()

    @classmethod
    def first(cls,
              filters:list[BinaryExpression] or None = None,
              order_by: list[UnaryExpression] or None = None,
              ) -> Self | None:
        """
        Busca o primeiro registro que atende aos filtros fornecidos.
        :param filters: list[BinaryExpression] or None - Filtros a serem aplicados na busca.
        :param order_by: list[UnaryExpression] or None - Ordenação a ser aplicada na busca.
        :return: Model | None - Primeira instância encontrada ou None.
        """
        with Database.get_session() as session:

            query = session.query(cls)

            if filters:
                query = query.filter(*filters)
            if order_by:
                query = query.order_by(*order_by)
            else:
                query = query.order_by(cls.id.asc())

            return query.first()

    @classmethod
    def last(cls,
              filters:list[BinaryExpression] or None = None,
              order_by: list[UnaryExpression] or None = None,
              ) -> Self | None:
        """
        Busca o último registro que atende aos filtros fornecidos.
        :param filters: list[BinaryExpression] or None - Filtros a serem aplicados na busca.
        :param order_by: list[UnaryExpression] or None - Ordenação a ser aplicada na busca.
        :return: Model | None - Última instância encontrada ou None.
        """
        with Database.get_session() as session:

            query = session.query(cls)

            if filters:
                query = query.filter(*filters)

            if order_by:

                query = query.order_by(*order_by)

                count = query.count()

                if count == 0:
                    return None

                return query.offset(count - 1).first()

            else:
                # se não tiver order_by, ordena pelo id
                order_by = [cls.id.desc()]
                query = query.order_by(*order_by)
                return query.first()