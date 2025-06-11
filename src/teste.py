from src.database.generator.criar_dados_leitura import criar_dados_leitura
from src.database.generator.gerar_sensores_e_dados import criar_dados_sample
from src.database.login.iniciar_database import iniciar_database
from src.database.models.sensor import LeituraSensor
from src.database.reset_contador_ids import reset_contador_ids, get_sequences_from_db
from src.database.tipos_base.database import Database
from src.logger.config import configurar_logger
from datetime import datetime, timedelta


def teste():
    """Função teste do programa."""
    configurar_logger()
    Database.init_sqlite("../database.db")
    Database.create_all_tables(drop_if_exists=False)
    ddl = Database.generate_ddl()

    print(ddl)

    with open("../assets/export.ddl", "w") as f:
        f.write(ddl)

    mer = Database.generate_mer()

    with open("export.mer", "w") as f:
        f.write(mer)

    hoje = datetime.now()

    data_inicial = hoje - timedelta(days=30)

    leituras = criar_dados_sample(
        data_inicial=data_inicial,
        data_final=hoje,
        total_leituras=1000
    )

    todas_leituras = []

    for sensor, l in leituras:
        todas_leituras = todas_leituras + l

    with Database.get_session() as session:

        for object in todas_leituras:
            session.add(object)
            session.commit()

    print(LeituraSensor.count())


if __name__ == "__main__":
    teste()