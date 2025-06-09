from contextlib import contextmanager
from io import StringIO
from typing import Optional
from sqlalchemy import create_engine, Engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import json
import os

from sqlalchemy.sql.ddl import CreateTable

from src.settings import SQL_ALCHEMY_DEBUG

DEFAULT_DSN = "oracle.fiap.com.br:1521/ORCL"

class Database:

    engine:Engine
    session:sessionmaker

    @staticmethod
    def init_sqlite(path:Optional[str] = None):
        """
        Inicializa a conexão com o banco de dados SQLite.
        :param path: Caminho do banco de dados SQLite.
        :return:
        """

        if path is None:
            path = os.path.join(os.getcwd(), "database.db")

        # Cria o engine de conexão
        engine = create_engine(f"sqlite:///{path}", echo=SQL_ALCHEMY_DEBUG)

        # Testa a conexão
        with engine.connect() as _:
            print(f"Conexão bem-sucedida ao banco de dados SQLite!\n Path: {path}")
        Database.engine = engine
        Database.session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @staticmethod
    def init_oracledb(user:str, password:str, dsn:str=DEFAULT_DSN):
        '''
        Inicializa a conexão com o banco de dados Oracle.
        :param user: Nome do usuário do banco de dados.
        :param password: Senha do usuário do banco de dados.
        :param dsn: DSN do banco de dados.
        :return:
        '''

        # Cria o engine de conexão
        engine = create_engine(f"oracle+oracledb://{user}:{password}@{dsn}", echo=SQL_ALCHEMY_DEBUG)

        # Testa a conexão
        with engine.connect() as _:
            print("Conexão bem-sucedida ao banco de dados Oracle!")
        Database.engine = engine
        Database.session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @staticmethod
    def init_from_session(engine:Engine, session:sessionmaker):
        """
        Inicializa a conexão com o banco de dados a partir de um engine e sessionLocal já existentes.
        :param engine: Engine do banco de dados.
        :param session: SessionLocal do banco de dados.
        :return:
        """
        Database.engine = engine
        Database.session = session

    @staticmethod
    def init_oracledb_from_file(path:str = r"E:\PythonProject\fiap_fase3_cap1\login.json"):

        """
        Inicializa a conexão com o banco de dados Oracle a partir de um arquivo JSON.
        :param path: Caminho do arquivo JSON com as credenciais do banco de dados.
        :return:
        """
        with open(path, "r") as file:
            data = json.load(file)
            user = data["user"]
            password = data["password"]

        Database.init_oracledb(user, password)

    @staticmethod
    @contextmanager
    def get_session() -> Generator[Session, None, None]:
        db = Database.session()
        try:
            yield db
        finally:
            db.close()

    @classmethod
    def list_tables(cls) -> list[str]:
        """
        Lista as tabelas do banco de dados.
        :return: List[str] - Lista com os nomes das tabelas.
        """
        engine = cls.engine
        metadata = MetaData()
        metadata.reflect(bind=engine)
        tables = metadata.tables.keys()
        return list(tables)

    @classmethod
    def list_sequences(cls):
        """
        Lista todas as sequences do banco de dados.
        :return: Lista com os nomes das sequences.
        """
        metadata = MetaData()
        metadata.reflect(bind=cls.engine)
        sequences = [seq.name for seq in metadata._sequences.values()]
        return sequences

    @classmethod
    def create_all_tables(cls, drop_if_exists:bool=False):
        """
            Cria todas as tabelas do banco de dados que herdam de Model.
            ATENÇÃO: Para isso funcionar deve-se carregar todos os models na memória.
            :param drop_if_exists: Se True, remove as tabelas existentes antes de criar novas.
        """

        if drop_if_exists:
            cls.drop_all_tables()

        from src.database.tipos_base.model import Model
        from src.database.dynamic_import import import_models

        import_models(sort=True)

        try:
            Model.metadata.create_all(bind=cls.engine)
            print("Tabelas criadas com sucesso.")
        except Exception as e:
            print("Erro ao criar tabelas no banco de dados.")
            raise

    @classmethod
    def drop_all_tables(cls):
        """
            Dropa todas as tabelas do banco de dados.
            ATENÇÃO: Para isso funcionar deve-se carregar todos os models na memória.
        """
        from src.database.tipos_base.model import Model
        from src.database.dynamic_import import import_models

        import_models(sort=True)

        try:
            Model.metadata.drop_all(bind=cls.engine)
            print("Tabelas removidas com sucesso.")
        except Exception as e:
            print("Erro ao remover tabelas do banco de dados.")
            raise

    @classmethod
    def generate_ddl(cls,) -> str:
        """
        Gera os comandos SQL (DDL) para criar as tabelas baseadas nos models.
        """

        #Os imports são feitos dentro da função para evitar problemas de importação circular.
        from src.database.tipos_base.model import Model
        # É necessário importar os models para que as tabelas sejam criadas corretamente.
        from src.database.dynamic_import import import_models

        import_models(sort=True)

        output = StringIO()

        for table in Model.metadata.sorted_tables:
            ddl_statement = str(CreateTable(table).compile(cls.engine))
            output.write(ddl_statement + ";\n\n")

        return output.getvalue()

    @classmethod
    def generate_mer(cls) -> str:
        """
        Retorna um MER simplificado baseado nos models e relacionamentos declarados.
        """
        #Os imports são feitos dentro da função para evitar problemas de importação circular.
        from src.database.tipos_base.model import Model
        # É necessário importar os models para que as tabelas sejam carregadas corretamente.
        from src.database.dynamic_import import import_models

        import_models(sort=True)
        mer_output = "\nModelo de Entidade-Relacionamento:\n\n"

        for table in Model.metadata.tables.values():
            mer_output += f"Tabela: {table.name}\n"
            for column in table.columns:
                col_info = f"  - {column.name} {f'({column.type} NOT NULL)' if not column.nullable else f'({column.type})'}"
                if column.primary_key:
                    col_info += " [PK]"
                if column.foreign_keys:
                    foreign_table = list(column.foreign_keys)[0].column.table.name
                    col_info += f" [FK -> {foreign_table}]"
                mer_output += col_info + "\n"
            mer_output += "\n"

        return mer_output