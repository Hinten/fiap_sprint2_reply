import os
import logging
from src.database.login.senha import salvar_senha_arquivo_base64, carregar_senha_arquivo_base64
from src.database.tipos_base.database import Database
from src.database.input_validation import input_str, input_bool


def iniciar_database():

    print("Iniciando o banco de dados...")
    user = os.environ.get('user')
    senha = os.environ.get('senha')
    dsn = os.environ.get('dsn')

    pegou_ambiente = False
    pegou_b64 = False

    if user is not None and senha is not None:
        pegou_ambiente = True
    else:
        user, senha, dsn = carregar_senha_arquivo_base64()

        if user is not None and senha is not None:
            pegou_b64 = True



    iniciou = False

    while not iniciou:

        if user is None:
            print("--- Usuário não encontrado ---")
            user = input_str('user', message_override="Digite o usuário do banco de dados: ")

        if senha is None:
            print("--- Senha não encontrada ---")
            senha = input_str('senha', message_override="Digite a senha do banco de dados: ")

        if dsn is None:
            print("--- DSN não encontrado ---")
            dsn = input_str('dsn', message_override="Digite o DSN do banco de dados\n(Pressione enter para o valor oracle.fiap.com.br:1521/ORCL): ", old_value='oracle.fiap.com.br:1521/ORCL')

        try:
            Database.init_oracledb(user=user, password=senha, dsn=dsn)
            iniciou = True
        except Exception as e:
            logging.error(f"{e}\n--- Erro ao conectar ao banco de dados, tentando novamente. ---")
            user = None
            senha = None
            dsn = None
            iniciou = False

    logging.info("--- Banco de dados conectado com sucesso! ---")

    if not pegou_ambiente and not pegou_b64:
        print("Deseja salvar o usuário e senha?")
        salvar = input_bool('Salvar Senha', modo='S')

        if salvar:
            salvar_senha_arquivo_base64(user, senha, dsn)
            print("--- Senha salva com sucesso! ---")



if __name__ == "__main__":
    iniciar_database()