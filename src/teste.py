from src.database.generator.criar_dados_leitura import criar_dados_leitura
from src.database.login.iniciar_database import iniciar_database
from src.database.reset_contador_ids import reset_contador_ids, get_sequences_from_db
from src.database.tipos_base.database import Database
from src.logger.config import configurar_logger
from datetime import datetime

def main():
    """Função teste do programa."""
    configurar_logger()
    iniciar_database()
    Database.create_all_tables(drop_if_exists=False)
    ddl = Database.generate_ddl()

    print(ddl)

    with open("export.ddl", "w") as f:
        f.write(ddl)

    mer = Database.generate_mer()

    with open("export.mer", "w") as f:
        f.write(mer)

    print(mer)

    # leiturasPH = criar_dados_leitura(
    #     data_inicial=datetime(2025, 5, 15),
    #     data_final=datetime(2025, 5, 21),
    #     sensor_id=3,
    #     total_leituras=20,
    #     tipo='range',
    #     minimo=0,
    #     maximo=14
    # )
    #
    # for (i, leitura) in enumerate(leiturasPH):
    #     print(f"Leitura {i}: {leitura.data_leitura} - {leitura.valor}")
    #     leitura.save()
    #
    # leiturasPotassio = criar_dados_leitura(
    #     data_inicial=datetime(2025, 5, 15),
    #     data_final=datetime(2025, 5, 21),
    #     sensor_id=2,
    #     total_leituras=20,
    #     tipo='bool',
    # )
    #
    # for (i, leitura) in enumerate(leiturasPotassio):
    #     print(f"Leitura {i}: {leitura.data_leitura} - {leitura.valor}")
    #     leitura.save()
    #
    # leiturasFosforo = criar_dados_leitura(
    #     data_inicial=datetime(2025, 5, 15),
    #     data_final=datetime(2025, 5, 21),
    #     sensor_id=4,
    #     total_leituras=20,
    #     tipo='bool',
    # )
    #
    # for (i, leitura) in enumerate(leiturasFosforo):
    #     print(f"Leitura {i}: {leitura.data_leitura} - {leitura.valor}")
    #     leitura.save()

main()