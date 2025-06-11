# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Projeto: fiap_sprint2_reply

## Atividade em Grupo: FIAP - 1TIAOB - 2025/1 - Fase4 Sprint 2 - Reply

## 👨‍🎓 Integrantes: 
- <a href="">Alice C. M. Assis - RM 566233</a>
- <a href="">Leonardo S. Souza - RM 563928</a>
- <a href="">Lucas B. Francelino - RM 561409</a>
- <a href="">Pedro L. T. Silva - RM 561644</a>
- <a href="">Vitor A. Bezerra - RM 563001</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="proflucas.moreira@fiap.com.br">Lucas Gomes Moreira</a>
### Coordenador(a)
- <a href="profandre.chiovato@fiap.com.br">André Godoi Chiovato</a>

# 1. Descrição do Projeto

A coleta de dados em ambientes industriais modernos é realizada através de sensores conectados a sistemas embarcados, como o ESP32. Esses sensores monitoram variáveis como temperatura, vibração, luminosidade e qualidade do ar, fornecendo informações críticas para análise e predição de falhas.

Com a chegada da Indústria 4.0, empresas têm apostado fortemente na digitalização do chão de fábrica, conectando sensores e dispositivos a plataformas de dados em nuvem. Isso permite a análise em tempo real e a tomada de decisões baseadas em dados.

Nesta fase do desafio, simulamos esse cenário utilizando plataformas online de simulação de circuitos e sensores, como o VSCode, Wokwi e PlatformIO. O objetivo é criar um circuito virtual funcional com ESP32, integrando sensores simulados para gerar dados que serão utilizados em análises iniciais.

# 2. Objetivos do Projeto

- Projetar e simular um sistema básico de coleta de dados utilizando ESP32 e sensores virtuais.
- Compreender como sensores simulados podem representar sensores reais em sistemas embarcados.
- Construir um circuito simples e funcional, integrando sensores de temperatura, luminosidade e vibração.
- Registrar e analisar os dados coletados, gerando gráficos e estatísticas iniciais.
- Documentar todo o processo, incluindo prints, código, dados e análises.

# 3. Justificativa dos Sensores Escolhidos

- **Sensor de Temperatura (MPU6050):** Permite monitorar o aquecimento de equipamentos, prevenindo falhas por superaquecimento.
- **Sensor de Vibração (MPU6050):** Essencial para identificar padrões anormais que podem indicar desgaste ou mau funcionamento de máquinas.
- **Sensor de Luminosidade (LDR):** Útil para monitorar ambientes industriais onde a iluminação pode impactar processos ou segurança.

Esses sensores foram escolhidos por serem amplamente utilizados em ambientes industriais e facilmente simuláveis no Wokwi.

# 4. Esquema do Circuito Simulado

<p align="center">
  <img src="assets/ciruito.JPG" alt="Circuito Sensor" border="0" width=70% height=70%>
</p>

- O ESP32 está conectado ao sensor MPU6050 (I2C) e ao LDR (analógico).
- LED, relé e buzzer são usados para alertas visuais e sonoros.
- O LCD exibe informações em tempo real sobre os sensores.

# 5. Trechos Representativos do Código

O código que controla o ESP32 pode ser encontrado no arquivo [src/wokwi/src/sketch.cpp](src/wokwi/src/sketch.cpp). A seguir, apresentamos trechos representativos do código que demonstram a leitura dos sensores, o envio dos dados para a API e o alerta de vibração.

### Leitura dos Sensores e Envio dos Dados

```cpp
// Leitura do LDR
int ldrValue = analogRead(LDR_PIN);
int lux = map(ldrValue, 0, 4095, 0, 2000); 
doc["lux"] = lux;

// Leitura da temperatura do MPU6050
int rawTemp = mpu.getTemperature();
float tempC = rawTemp / 340.0 + 36.53;
doc["temperatura"] = tempC;

// Leitura da vibração (aceleração)
mpu.getAcceleration(&ax_raw, &ay_raw, &az_raw);
float ax = ax_raw / 16384.0;
float ay = ay_raw / 16384.0;
float az = az_raw / 16384.0;
doc["acelerometro_x"] = ax;
doc["acelerometro_y"] = ay;
doc["acelerometro_z"] = az;
```

### Alerta de Vibração

```cpp
if (vibracaoMedia > LIMIAR_VIBRACAO) {
  lcd.setCursor(0, 1);
  lcd.print("#ALERTA DE VIBRACAO#");
  // Ativa LED, relé e buzzer
}
```

### Envio dos Dados para a API

```cpp
if (iniciou_sensor) {
  int httpcode = post_data(doc, post_sensor);
  if (httpcode >= 200 && httpcode < 300) {
    Serial.println("Dados enviados com sucesso!");
  }
}
```

# 6. Registro do Funcionamento da Simulação

As leituras dos sensores são coletadas pelo ESP32 e enviadas automaticamente para a API via requisições HTTP. O envio ocorre a cada ciclo de leitura, garantindo que os dados estejam sempre atualizados no banco de dados para análise posterior. O monitor serial e o display LCD exibem em tempo real as leituras e alertas, enquanto a API armazena cada registro recebido.

- **Print do Monitor Serial:**

<p align="center">
  <img src="assets/print_monitor_serial.JPG" alt="Monitor Serial" border="0" width=70% height=70%>
</p>

- **Print do LCD:**

<p align="center">
  <img src="assets/print_lcd.JPG" alt="LCD" border="0" width=70% height=70%>
</p>

## Conexão com o Wi-Fi e envio de dados para a API

Para que a simulação funcione corretamente, é necessário configurar a conexão com o Wi-Fi simulado do Wokwi e definir o IP do servidor local da API.

No momento, neste projeto, a API e a simulação do ESP32 estão rodando localmente. Para a configuração funcionar corretamente, é necessário alterar o arquivo [platformio.ini](src/wokwi/platformio.ini) e setar a variável 'API_URL' para 'http://**IP DE SUA MÁQUINA NA REDE LOCAL**:8180', conforme exemplo abaixo:

```plaintext
[env:esp32]
platform = espressif32
framework = arduino
board = esp32dev
lib_deps = 
    bblanchon/ArduinoJson@^7.4.1
    electroniccats/MPU6050@^1.4.3
    marcoschwartz/LiquidCrystal_I2C@^1.1.4
build_flags = 
    '-D API_URL="http://192.168.0.60:8180"'
    '-D NETWORK_SSID="Wokwi-GUEST"'
    '-D NETWORK_PASSWORD=""'
```

> NOTA1: Não sete o IP da API para localhost ou 127.0.0.1, pois o ESP32 não conseguirá se conectar a ele. O localhost do ESP32 é o próprio ESP32, e não a máquina onde o servidor está rodando.

> NOTA2: Caso você esteja rodando a simulação e mesmo assim o ESP32 não consiga se conectar à API, verifique se o firewall da sua máquina está bloqueando a porta 8180. Se estiver, libere a porta para que o ESP32 consiga se conectar.

Após configurado o arquivo `platformio.ini`, você poderá iniciar a simulação do ESP32 no Wokwi. O circuito irá coletar os dados dos sensores e enviá-los para a API, que por sua vez irá armazenar os dados no banco de dados.

## API para salvar os dados do sensor

Neste projeto, foi implementada uma API básica utilizando o FastAPI para receber os dados do sensor e armazená-los no banco de dados. A API permite que o ESP32 envie as leituras dos sensores, que são então salvas no banco de dados para posterior análise e visualização.

Para facilitar os testes, a API está configurada para rodar localmente na porta 8180 e será iniciada automaticamente junto ao dashboard ao executar o comando `streamlit run main_dash.py` quando a variável de ambiente `ENABLE_API` for setada como `true`.

No entanto, caso queira, a API pode ser executada separadamente executando o arquivo [api_basica.py](src/wokwi_api/api_basica.py).

Explicações mais detalhadas sobre como iniciar o dashboard e variáveis de ambiente serão apresentadas na seção "Instalando e Executando o Projeto", a seguir neste mesmo README.md.

# 7. Armazenamento de Dados em Banco SQL com Python

<p align="center">
  <img src="assets/mer.png" alt="MER" border="0" width=70% height=70%>
</p>

Modelo de Entidade-Relacionamento:

Tabela: TIPO_SENSOR
  - id (INTEGER NOT NULL) [PK]
  - nome (VARCHAR(255) NOT NULL)
  - tipo (VARCHAR(15) NOT NULL)

Tabela: SENSOR
  - id (INTEGER NOT NULL) [PK]
  - tipo_sensor_id (INTEGER NOT NULL) [FK -> TIPO_SENSOR]
  - nome (VARCHAR(255))
  - cod_serial (VARCHAR(255))
  - descricao (VARCHAR(255))
  - data_instalacao (DATETIME)
  - latitude (FLOAT)
  - longitude (FLOAT)

Tabela: LEITURA_SENSOR
  - id (INTEGER NOT NULL) [PK]
  - sensor_id (INTEGER NOT NULL) [FK -> SENSOR]
  - data_leitura (DATETIME NOT NULL)
  - valor (FLOAT NOT NULL)

Neste projeto, utilizamos um banco de dados SQLite para armazenar as leituras dos sensores. A estrutura do banco de dados é composta por três tabelas principais: `TIPO_SENSOR`, `SENSOR` e `LEITURA_SENSOR`.

## Models e Python

Para realizar a conversão das linhas e colunas da database para Python, foram definidas classes as quais são responsáveis por fazer as operações CRUD e demais funcionalidades do banco de dados.
Essas classes podem ser encontradas na pasta `src/database/models`, e todas elas herdam a classe principal chamada [Model](src/database/tipos_base/model.py).

# 8. Instalando e Executando o Projeto

O sistema foi desenvolvido em Python e utiliza um banco de dados SQLite para armazenar os dados. O código é modularizado, permitindo fácil manutenção e expansão.

## 📦 Requisitos
- Python 3.13.2
- Bibliotecas:
  - oracledb==3.1.0
  - pandas==2.2.3
  - matplotlib==3.10.1
  - streamlit==1.44.1
  - SQLAlchemy==2.0.40
  - fastapi==0.115.12
  - pydantic==2.11.5
  - uvicorn==0.34.3
  - dotenv==0.9.9
  - seaborn==0.13.2
  - plotly==6.1.2

## 📂 Instalação

- Instale as dependências utilizando o arquivo requirements.txt:
    ```bash
    pip install -r requirements.txt
    ```
  
- Para iniciar o dashboard interativo, execute o seguinte comando no terminal:
    ```bash
    streamlit run main_dash.py
    ```

## Arquivo de Configuração

O projeto utiliza um arquivo especial denominado **`.env`** para armazenar variáveis de ambiente sensíveis, como credenciais de banco de dados e chaves de APIs externas. Por razões de segurança, esse arquivo **não deve ser compartilhado publicamente**.

### 📄 O que é o `.env`?

O `.env` é um arquivo-texto simples, onde cada linha define uma variável de ambiente no formato `NOME_VARIAVEL=valor`. Esse método permite separar informações confidenciais do código-fonte, facilitando a configuração do sistema para diferentes ambientes (desenvolvimento, testes, produção, etc).

### 🔑 Variáveis Utilizadas

| Variável      | Descrição                                                                                                | Exemplo de Valor                  |
|---------------|----------------------------------------------------------------------------------------------------------|-----------------------------------|
| LOGGING_ENABLED      | Define se o logger da aplicação será ativado (`true` ou `false`)                                         | `true` ou `false`                 |
| ENABLE_API      | Define se a API que salva os dados do sensor será ativada juntamente com o dashboard (`true` ou `false`) | `true` ou `false`                 |

### ⚙️ Exemplo de arquivo `.env`

```plaintext
LOGGING_ENABLED=true
ENABLE_API=true
```
  
Ao iniciar o Dashboard, o usuário será direcionado para a interface do Streamlit, onde poderá visualizar os dados coletados pelos sensores e interagir com os gráficos gerados.
A página pricipal do dashboard exibe uma exploração de dados, a qual pode ser filtrada por data de leitura.


<p align="center">
  <img src="assets/dashboard/principal/principal_1.JPG" alt="principal_1" border="0" width=70% height=70%>
</p>
<p align="center">
  <img src="assets/dashboard/principal/principal_2.JPG" alt="principal_2" border="0" width=70% height=70%>
</p>
<p align="center">
  <img src="assets/dashboard/principal/principal_3.JPG" alt="principal_3" border="0" width=70% height=70%>
</p>
<p align="center">
  <img src="assets/dashboard/principal/principal_4.JPG" alt="principal_4" border="0" width=70% height=70%>
</p>
<p align="center">
  <img src="assets/dashboard/principal/principal_5.JPG" alt="principal_5" border="0" width=70% height=70%>
</p>
<p align="center">
  <img src="assets/dashboard/principal/principal_6.JPG" alt="principal_6" border="0" width=70% height=70%>
</p>

O Dashboard também permite realizar operações CRUD. A seguir, um exemplo de como cadastrar uma nova leitura de sensor:

Clique em "Leituras de Sensores" no menu lateral e posteriormente em "Novo".

<p align="center">
  <img src="assets/dashboard/exemplo_cadastro/exemplo_cadastro_1.JPG" alt="exemplo_cadastro_1" border="0" width=70% height=70%>
</p>

Preencha os campos necessários e clique em "Salvar".

<p align="center">
  <img src="assets/dashboard/exemplo_cadastro/exemplo_cadastro_2.JPG" alt="exemplo_cadastro_2" border="0" width=70% height=70%>
</p>

Uma mensagem de sucesso será exibida, confirmando que a leitura foi cadastrada com sucesso.


<p align="center">
  <img src="assets/dashboard/exemplo_cadastro/exemplo_cadastro_3.JPG" alt="exemplo_cadastro_3" border="0" width=70% height=70%>
</p>

Caso necessário o usuário pode editar ou excluir uma leitura existente. Basta selecionar a linha desejada e clicar no botão "Editar". Para excluir é só clicar no botão "Excluir" dentro da tela de edição.

<p align="center">
  <img src="assets/dashboard/exemplo_cadastro/exemplo_cadastro_4.JPG" alt="exemplo_cadastro_4" border="0" width=70% height=70%>
</p>

<p align="center">
  <img src="assets/dashboard/exemplo_cadastro/exemplo_cadastro_5.JPG" alt="exemplo_cadastro_5" border="0" width=70% height=70%>
</p>


# 9. Gráficos e Insights Iniciais

A análise exploratória dos dados coletados é realizada por meio do dashboard desenvolvido em Python/Streamlit, localizado em [src/dashboard/plots/analise_exploratoria.py](src/dashboard/plots/analise_exploratoria.py). A seguir, detalhamos os principais gráficos e suas funções:

- **Tabela Consolidada de Leituras**: Apresenta todos os dados coletados pelos sensores, organizados por data/hora e tipo de sensor. Permite uma visão geral dos valores registrados ao longo do tempo.

- **Gráficos de Linha por Tipo de Sensor**: Para cada sensor (temperatura, vibração, luminosidade), é gerado um gráfico de linha mostrando a evolução dos valores ao longo do tempo. Isso facilita a identificação de tendências, picos e padrões sazonais nos dados.

    <p align="center">
      <img src="assets/grafico_linhas.JPG" alt="Gráfico de Linha" width="70%">
    </p>

- **Boxplot dos Valores dos Sensores**: Exibe a distribuição estatística dos valores de cada sensor, destacando mediana, quartis e possíveis outliers. É útil para comparar a variabilidade entre sensores e identificar leituras atípicas.

- **Matriz de Correlação entre Sensores**: Mostra o grau de correlação entre os diferentes tipos de sensores. Um mapa de calor (heatmap) indica visualmente se há relação linear entre, por exemplo, temperatura e vibração, auxiliando na análise de possíveis causas e efeitos.

- **Scatterplot (Dispersão) entre Sensores**: Permite visualizar a relação entre dois sensores (ex: temperatura vs. vibração), facilitando a identificação de padrões ou agrupamentos nos dados.

- **Scatterplot 3D**: Quando há pelo menos três sensores, é possível visualizar a relação entre eles em um gráfico tridimensional, enriquecendo a análise multivariada.

- **Barplot da Média dos Valores por Tipo de Sensor**: Mostra a média dos valores registrados para cada tipo de sensor, permitindo uma comparação direta entre eles.

- **Pairplot dos Sensores**: Exibe múltiplos gráficos de dispersão entre todos os pares de sensores, facilitando a análise cruzada e a identificação de correlações múltiplas.

Esses gráficos são fundamentais para compreender o comportamento dos sensores, identificar anomalias, padrões e possíveis relações entre as variáveis monitoradas. A interface do dashboard permite filtrar por datas e tipos de sensores, tornando a análise flexível e interativa.

# 10. Importando a Base de dados utilizada pelo Grupo

As tabelas com os dados utilizados no sistema podem ser encontradas na pasta em [assets/database_export.zip](assets/database_export.zip).

O Grupo disponibilizou uma base de dados inicial para facilitar o uso do sistema. Para importar essa base de dados, siga os passos abaixo:

1. O usuário deve selecionar a opção "Importar Banco de Dados" no menu principal.
<p align="center">
  <img src="assets/dashboard/importar_banco_de_dados/importar_bd_1.JPG" alt="importar_db" border="0" width=80% height=80%>
</p>

2. Selecione o arquivo ZIP localizado em [assets/database_export.zip](assets/database_export.zip), espere carregar, role a página até o final e clique no botão "Salvar no Banco de Dados".
<p align="center">
  <img src="assets/dashboard/importar_banco_de_dados/importar_bd_2.JPG" alt="salvar_db" border="0" width=80% height=80%>
</p>

3. Não feche a janela e espere a operação ser concluída. Após a conclusão, o sistema irá exibir uma mensagem de sucesso. Caso ocorra algum erro, tente novamente.

<p align="center">
  <img src="assets/dashboard/importar_banco_de_dados/importar_bd_3.JPG" alt="salvar_db" border="0" width=80% height=80%>
</p>


## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.streamlit</b>: Pasta que contém arquivos de configuração do Streamlit, como o tema da interface e a organização da barra lateral.
- <b>assets</b>: Diretório destinado ao armazenamento de elementos não estruturados do projeto, como imagens e ícones utilizados no dashboard.
- <b>src</b>: Diretório principal que contém todo o código-fonte desenvolvido ao longo das fases do projeto. Ele está organizado nos seguintes submódulos:  
  - <b>dashboard</b>: Código responsável pela construção do dashboard, desenvolvido em Python com uso da biblioteca Streamlit. ([dashboard](src/dashboard/))
  - <b>database</b>: Módulo responsável pelas operações de banco de dados, incluindo conexões, inserções, listagens, edições e exclusões de registros.  
  - <b>logger</b>: Código responsável por registrar (logar) todas as operações executadas no sistema, garantindo rastreabilidade.  
  - <b>plots</b>: Contém o código responsável pela geração de gráficos e visualizações, utilizado para exibir dados de forma clara e intuitiva no dashboard.  
  - <b>wokwi</b>: Contém o código do sensor ESP32 utilizado na simulação de sensores.
  - <b>wokwi_api</b>: Contém o código responsável por criar a API que vai salvar as leituras dos sensores no banco de dados.
- <b>.env</b>: Arquivo de configuração que contém as chaves de API e outras variáveis de ambiente necessárias para o funcionamento do sistema. É necessário criar este arquivo na raiz do projeto, conforme orientações na seção "Arquivo de Configuração".
- <b>.gitignore</b>: Arquivo que especifica quais arquivos e pastas devem ser ignorados pelo Git, evitando que informações sensíveis ou desnecessárias sejam versionadas. É importante garantir que o arquivo `.env` esteja incluído neste arquivo para evitar o upload de chaves de API e outras informações sensíveis.
- <b>README</b>: Arquivo de documentação do projeto (este que está sendo lido), com orientações gerais, instruções de uso e contextualização.
- <b>main_dash</b>: Arquivo principal para a execução do dashboard. Está localizado na raiz do projeto com o objetivo de evitar problemas com importações de módulos internos.
- <b>requirements.txt</b>: Arquivo que lista todas as dependências do projeto, necessário para a instalação do ambiente virtual. Deve ser utilizado com o comando `pip install -r requirements.txt` para instalar as bibliotecas necessárias.

## 🗃 Histórico de versionamento

* **0.2.0 - 11/06/2025** – README versão final  
* **0.1.0 - 23/05/2025** – Versão preliminar da nossa aplicação

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>

