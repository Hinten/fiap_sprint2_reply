from enum import Enum


def input_bool(field_name:str, old_value:bool|None=None, *,
               modo:str='V' # ou 'S'
               ) -> bool:
    """
    Função auxiliar para obter um valor booleano do usuário.
    """

    if modo == 'V':
        input_string = f"Digite o valor de {field_name} [V]erdadeiro/[F]also"
    elif modo == 'S':
        input_string = "[S]im/[N]ão"
    else:
        raise ValueError(f"Modo inválido: {modo}. Esperado 'V' ou 'S'")


    if old_value is not None:
        input_string += f"\n(Pressione enter para manter o valor {old_value}): "
    else:
        input_string += ": "

    value = input(input_string)

    if value.strip() == '' and old_value is not None:
        return old_value

    verdadeiro = ['v', 'verdadeiro', '[v]erdadeiro', 'true', 's', 'sim', '[s]im', 'yes']

    falso = ['f', 'false', '[f]alse', 'n', 'não', '[n]ão', 'nao', '[n]ao', 'no']

    if value.lower().strip() in verdadeiro:
        return True
    elif value.lower().strip() in falso:
        return False
    else:
        if modo == 'V':
            raise ValueError(f"Valor inválido para {field_name}: {value}. Esperado [V]erdadeiro/[F]also")
        else:
            raise ValueError(f"Valor inválido para {field_name}: {value}. Esperado [S]im/[N]ão")

def input_int(field_name:str, old_value:int|None=None, message_override:str=None) -> int:
    """
    Função auxiliar para obter um valor inteiro do usuário.
    """
    input_string = f"Digite um número inteiro para {field_name}"

    if old_value is not None:
        input_string += f"\n(Pressione enter para manter o valor {old_value}): "
    else:
        input_string += ": "

    input_string = message_override or input_string

    value = input(input_string)

    if value.strip() == '' and old_value is not None:
        return old_value

    try:
        return int(value.strip())
    except ValueError:
        raise ValueError(f"Valor inválido para {field_name}: {value}. Esperado um número inteiro")

def input_float(field_name:str, old_value:float|None=None) -> float:
    """
    Função auxiliar para obter um valor float do usuário.
    """
    input_string = f"Digite um número para {field_name}"

    if old_value is not None:
        input_string += f"\n(Pressione enter para manter o valor {old_value}): "
    else:
        input_string += ": "

    value = input(input_string)

    if value.strip() == '' and old_value is not None:
        return old_value

    try:
        return float(value.strip().replace(',','.'))
    except ValueError:
        raise ValueError(f"Valor inválido para {field_name}: {value}. Esperado um número com ou sem casas decimais")

def input_str(field_name:str, old_value:str|None=None, *, max_length:int|None=None, message_override:str=None) -> str:
    """
    Função auxiliar para obter um valor string do usuário.
    """
    input_string = f"Digite o valor de {field_name}"

    if old_value is not None:
        input_string += f"\n(Pressione enter para manter o valor {old_value}): "
    else:
        input_string += ": "

    input_string = message_override or input_string

    value = input(input_string)

    if value.strip() == '' and old_value is not None:
        return old_value

    if max_length is not None and len(value.strip()) > max_length:
        raise ValueError(f"Valor inválido para {field_name}: {value}. O valor deve ter no máximo {max_length} caracteres")

    return value.strip()

def input_enum(field_name:str, enum_class: type[Enum], old_value: str|None=None) -> str:
    """
    Função auxiliar para obter um valor de um Enum do usuário.
    """
    input_string = f"Opções disponíveis para {field_name}:"

    options = list(enum_class)

    for index, value in enumerate(options):
        input_string += f"\n{index+1}) {value.name}"

    if old_value is not None:
        input_string += f"\n(Pressione enter para manter o valor {enum_class(old_value).name}): "
    else:
        input_string += "\nEscolha uma opção: "

    value = input(input_string)

    if value.strip() == '' and old_value is not None:
        return old_value

    try:
        value = options[int(value.strip()) - 1].value
    except (ValueError, IndexError):
        raise ValueError(f"Opção inválida para {field_name}: {value}. Esperada uma das seguintes opções: {', '.join(map(str, range(1, len(options) + 1)))}")

    return value.strip()