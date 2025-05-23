import base64
import json

salt = 'SecretSaltExtremamenteSecreto'

def salvar_senha_arquivo_base64(user:str, senha:str, dsn:str|None=None) -> None:

    user = user + salt
    senha = senha + salt

    # Cria o dicionário com os dados

    dados = {
        'user': user,
        'senha': senha,
        'dsn': dsn
    }

    json_string = json.dumps(dados)
    base64_bytes = base64.b64encode(json_string.encode('utf-8'))
    base64_string = base64_bytes.decode('utf-8')

    with open('senha_muito_secreta.txt', 'w') as arquivo:
        arquivo.write(base64_string)

def carregar_senha_arquivo_base64() -> tuple[str | None, str | None, str | None]:

    try:
        with open('senha_muito_secreta.txt', 'r') as arquivo:
            base64_string = arquivo.read()
    except FileNotFoundError:
        return None, None, None

    base64_bytes = base64_string.encode('utf-8')
    json_bytes = base64.b64decode(base64_bytes)
    json_string = json_bytes.decode('utf-8')

    if json_string.strip() == '':
        return None, None, None

    dados = json.loads(json_string)

    return dados.get('user', '').replace(salt, ''), dados.get('senha', '').replace(salt, ''), dados.get('dsn', None)