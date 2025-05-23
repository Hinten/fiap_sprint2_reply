import importlib
import inspect
import logging
import os

from src.database.tipos_base.model import Model


def import_models(sort:bool=False) -> dict[str, type[Model]]:
    """
    Importa dinamicamente todas as classes que herdam de Model
    na pasta src/python/database/models.
    :return: dict - Um dicionário com o nome das classes como chave e as classes como valor.
    """
    models = {}
    models_path = os.path.join(os.path.dirname(__file__), "models")

    for file in os.listdir(models_path):
        if file.endswith(".py") and file != "__init__.py":

            # Remove o caminho do arquivo e substitui por um ponto
            # para formar o nome do módulo
            # Exemplo: src/database/models/modelo.py -> src.database.models.modelo
            # Isso é necessário para que o import funcione corretamente e o módulo seja encontrado.

            src_path = list(models_path.split(os.sep))
            src_path = src_path[src_path.index('src'):]
            src_path = '.'.join(src_path)
            module_name = f"{src_path}.{file[:-3]}"
            # logging.debug(f"Importando módulo: {module_name}")

            module = importlib.import_module(module_name)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Model) and obj is not Model:
                    # logging.debug(f"Encontrada classe modelo: {name}")
                    models[name] = obj

    if sort:
        models = dict(sorted(models.items(), key=lambda item: item[1].__database_import_order__))

    return models

def get_model_by_name(name:str) -> type[Model]:
    """
    Retorna uma instância do modelo baseado no nome.
    :param name: Nome do modelo.
    :return: Model - Instância do modelo.
    """
    models = import_models()
    model_class = models.get(name)
    if model_class:
        return model_class
    else:
        raise ValueError(f"Model '{name}' não encontrado.")

def get_model_by_table_name(table_name:str) -> type[Model]:
    """
    Retorna uma instância do modelo baseado no nome da tabela.
    :param table_name: Nome da tabela.
    :return: Model - Instância do modelo.
    """
    models = import_models()
    for model_class in models.values():
        if model_class.__tablename__ == table_name:
            return model_class
    raise ValueError(f"Model com tabela '{table_name}' não encontrado.")

if __name__ == "__main__":
    models = import_models()
    for name, model in models.items():
        print(f"Modelo: {name}, Classe: {model}")