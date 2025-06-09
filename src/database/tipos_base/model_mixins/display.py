from typing import Literal, Any
from sqlalchemy import BinaryExpression
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class SimpleTableFilter:
    """
    Classe para definir filtros de tabela.

    Args:
        field (str): Campo a ser filtrado.
        operator (Literal["==", "!=", "<", ">", "<=", ">="]): Operador de comparação.
        name (str or None): Sobrescrita do campo, se necessário.
        label (str or None): Rótulo do filtro.
        optional (bool): Indica se o filtro é opcional.
        value (Any): Valor a ser filtrado.
    """

    field: str
    operator: Literal["==", "!=", "<", ">", "<=", ">="]
    name: str or None = None
    label: str or None = None
    optional: bool = True
    value: Any = None


    def get_sqlalchemy_filter(self, model:type['Model'], value:Any = None) -> BinaryExpression:
        """
        Retorna o filtro SQLAlchemy correspondente ao valor fornecido.

        Args:
            model (type[Model]): Modelo SQLAlchemy onde o filtro será aplicado.
            value: Valor a ser filtrado.

        Returns:
            BinaryExpression: Filtro SQLAlchemy.
        """

        correct_value = value if value is not None else self.value

        if self.operator == "==":
            return getattr(model, self.field) == correct_value
        elif self.operator == "!=":
            return getattr(model, self.field) != correct_value
        elif self.operator == "<":
            return getattr(model, self.field) < correct_value
        elif self.operator == ">":
            return getattr(model, self.field) > correct_value
        elif self.operator == "<=":
            return getattr(model, self.field) <= correct_value
        elif self.operator == ">=":
            return getattr(model, self.field) >= correct_value
        else:
            raise ValueError(f"Operador '{self.operator}' não suportado.")

    def copy_with(self, **kwargs):
        return replace(self, **kwargs)

    def to_json(self):
        """
        Retorna uma representação JSON do filtro.

        Returns:
            dict: Representação JSON do filtro.
        """
        return {
            "field": self.field,
            "name": self.name,
            "operator": self.operator,
            "label": self.label,
            "optional": self.optional,
            "value": self.value if not type(self.value) is datetime else self.value.isoformat()
        }

    @classmethod
    def from_json(cls, data: dict):
        """
        Cria uma instância de SimpleTableFilter a partir de um dicionário JSON.

        Args:
            data (dict): Dicionário contendo os dados do filtro.

        Returns:
            SimpleTableFilter: Instância do filtro.
        """
        return cls(
            field=data.get("field"),
            name=data.get("name"),
            operator=data.get("operator"),
            label=data.get("label"),
            optional=data.get("optional", True),
            value=data.get("value")
        )



class _ModelDisplayMixin:
    """
    Mixin onde os métodos de exibição são definidos.

    Args:
        __menu_order__ (int): Ordem de exibição no menu.
        __menu_group__ (str or None): Grupo do menu onde o modelo será exibido.
        __table_view_fields__ (list[str]): Campos a serem exibidos na visualização da tabela.

    """


    __menu_order__ = 100000
    __menu_group__: str or None = None
    __table_view_fields__: list[str] = None
    __table_view_filters__: list[SimpleTableFilter] or None = None
    __table_view_itens_per_page__: int = 50

    # def __str__(self):
    #     """
    #     Return a string representation of the model instance.
    #     """
    #     return self.display_name()

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