from src.database.dynamic_import import import_models
from src.database.tipos_base.database import Database
from sqlalchemy import text


def get_sequences_from_db():
    """
    Retorna uma lista com os nomes das sequences existentes no banco de dados Oracle.
    """
    session = Database.session()
    result = session.execute(text("SELECT sequence_name FROM user_sequences"))
    sequences = [row.sequence_name for row in result]
    session.close()
    return sequences

def get_table_and_sequence_names():
    """
    Retorna uma lista de tuplas (table_name, sequence_name) para todas as tabelas.
    """
    models = import_models(sort=True)
    result = []
    for _, model in models.items():
        table_name = model.__tablename__
        sequence_name = f"{table_name}_SEQ_ID"
        result.append((table_name, sequence_name))
    return result

def reset_contador_ids():
    """
    Reseta o contador de IDs para cada tabela no banco de dados.
    """
    session = Database.session()
    for table_name, sequence_name in get_table_and_sequence_names():
        primary_key_column = 'ID'
        reset_sequence_sql = text(f"""
            DECLARE
                max_id NUMBER;
                diff NUMBER;
                dummy NUMBER;
            BEGIN
                SELECT NVL(MAX({primary_key_column}), 0) INTO max_id FROM {table_name};
                BEGIN
                    SELECT {sequence_name}.CURRVAL INTO dummy FROM dual;
                EXCEPTION
                    WHEN OTHERS THEN
                        SELECT {sequence_name}.NEXTVAL INTO dummy FROM dual;
                END;
                SELECT (max_id + 1 - {sequence_name}.CURRVAL) INTO diff FROM dual;
                IF diff <> 0 THEN
                    EXECUTE IMMEDIATE 'ALTER SEQUENCE {sequence_name} INCREMENT BY ' || diff;
                    EXECUTE IMMEDIATE 'SELECT {sequence_name}.NEXTVAL FROM dual' INTO dummy;
                    EXECUTE IMMEDIATE 'ALTER SEQUENCE {sequence_name} INCREMENT BY 1';
                END IF;
            END;
        """)
        session.execute(reset_sequence_sql)
    session.commit()
    session.close()