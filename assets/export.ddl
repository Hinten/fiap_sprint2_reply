
CREATE TABLE "TIPO_SENSOR" (
	id INTEGER NOT NULL, 
	nome VARCHAR(255) NOT NULL, 
	tipo VARCHAR(15) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;


CREATE TABLE "SENSOR" (
	id INTEGER NOT NULL, 
	tipo_sensor_id INTEGER NOT NULL, 
	nome VARCHAR(255), 
	cod_serial VARCHAR(255), 
	descricao VARCHAR(255), 
	data_instalacao TIMESTAMP,
	latitude FLOAT, 
	longitude FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tipo_sensor_id) REFERENCES "TIPO_SENSOR" (id), 
	UNIQUE (nome)
)

;


CREATE TABLE "LEITURA_SENSOR" (
	id INTEGER NOT NULL, 
	sensor_id INTEGER NOT NULL, 
	data_leitura TIMESTAMP NOT NULL,
	valor FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sensor_id) REFERENCES "SENSOR" (id)
)

;

