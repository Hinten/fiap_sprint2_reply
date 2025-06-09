"""
AVISO: Este arquivo define apenas mixins para uso em herança múltipla.
NÃO importe este arquivo diretamente como módulo principal.
"""

from sqlalchemy import inspect, Column, String


class _ModelFieldsMixin:
    """
    Mixin to add model fields to a class.
    """

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
            if field.type.length is not None and value is not None:
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