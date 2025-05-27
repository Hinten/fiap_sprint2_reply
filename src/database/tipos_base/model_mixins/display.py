
"""
AVISO: Este arquivo define apenas mixins para uso em herança múltipla.
NÃO importe este arquivo diretamente como módulo principal.
"""

class _ModelDisplayMixin:
    """
    Mixin onde os métodos de exibição são definidos.
    """

    __menu_order__ = 100000
    __menu_group__: str or None = None

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