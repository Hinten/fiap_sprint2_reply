// Essa aplicação tem o objetivo verificar a necessidade de irrigação através da utilização de 4 sensores
// Sensores: LDR (pH simulador), Umidade, Botão Azul (Fósforo Simulado) e Botão Amarelo (Potássio Simulado)
// Quando 2 ou mais sensores apontarem resultados negativos o relé do sistema de irrigação será acionado e o led irá acender
// Cado API Meteorológica. representada pelo Botão Vermelho, informe que que haverá chuva o sistema de irrigação será interrompido

// CONDIÇÃO NEGATIVA DE CADA SENSOR:
// LDR (pH simulador): Valor > 7 (Aplicado um fator de divisão por 100, por pH só vai de 0 a 14 e o LDR vai de 0 a 4000), 
// Umidade: Valor < 60% 
// Botão Azul (Fósforo Simulado): Desligado
// Botão Amarelo (Potássio Simulado): Desligado

#include <DHT.h> // Inclusão da biblioteca do sensor DHT22

// === DEFINIÇÃO DE PINOS ===
#define BUTTON_P 5        // Botão de fósforo (azul)
#define BUTTON_K 4        // Botão de potássio (amarelo)
#define LDR_PIN 14        // Pino analógico para simular pH via LDR
#define DHTPIN 12         // Sensor DHT22 (umidade)
#define DHTTYPE DHT22     // Tipo do sensor
#define RELAY_PIN 34      // Relé que aciona a bomba
#define LED_PIN 2         // LED indicativo da bomba
#define BUTTON_API 18     // Botão de API Meteorológica (vermelho)

// === OBJETO DO SENSOR DHT ===
DHT dht(DHTPIN, DHTTYPE);

// === VARIÁVEIS DE ESTADO DOS BOTÕES ===
bool estadoFosforo = false;
bool ultimoEstadoFosforo = HIGH;

bool estadoPotassio = false;
bool ultimoEstadoPotassio = HIGH;

bool estadoAPI = false;
bool ultimoEstadoAPI = HIGH;

void setup() {
  // Inicializa comunicação serial
  Serial.begin(115200);

  // Configuração dos pinos de entrada
  pinMode(BUTTON_P, INPUT_PULLUP);  // Botão de fósforo
  pinMode(BUTTON_K, INPUT_PULLUP);  // Botão de potássio
  pinMode(BUTTON_API, INPUT_PULLUP);  // Botão da API

  // Configuração dos pinos de saída
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  // Inicializa o sensor DHT
  dht.begin();
}

void loop() {
  // === LEITURA E CONTROLE DE ESTADO DOS BOTÕES ===
  bool leituraFosforo = digitalRead(BUTTON_P);
  bool leituraPotassio = digitalRead(BUTTON_K);
  bool leituraAPI = digitalRead(BUTTON_API);
  bool LedValue = digitalRead(LED_PIN);

  // Verifica mudança de estado do botão de fósforo
  if (leituraFosforo == LOW && ultimoEstadoFosforo == HIGH) {
    estadoFosforo = !estadoFosforo; // Alterna o estado
    delay(200); // Debounce
  }
  ultimoEstadoFosforo = leituraFosforo;

  // Verifica mudança de estado do botão de potássio
  if (leituraPotassio == LOW && ultimoEstadoPotassio == HIGH) {
    estadoPotassio = !estadoPotassio; // Alterna o estado
    delay(200); // Debounce
  }
  ultimoEstadoPotassio = leituraPotassio;

  // Verifica mudança de estado do botão da API
  if (leituraAPI == LOW && ultimoEstadoAPI == HIGH) {
    estadoAPI = !estadoAPI; // Alterna o estado
    delay(200); // Debounce
  }
  ultimoEstadoAPI = leituraAPI;

  // Leitura do LDR (simulando pH)
  int ldrValue = analogRead(LDR_PIN);  // Faixa de 0 a 4095 no ESP32

  // Leitura da umidade com o DHT22
  float umidade = dht.readHumidity();

  // === CONDIÇÕES DE IRRIGAÇÃO ===

  // Verifica se fósforo e potássio estão presentes
  bool nutrientesPresentes = !estadoFosforo && !estadoPotassio;

 // Verifica se fósforo e potássio estão presentes
  bool resultadoAPI = !estadoAPI;

  // Condição de pH ideal (simulado pelo LDR)
  bool phIdeal = (ldrValue > 700);

  // Verifica se a umidade está abaixo do ideal (< 60%)
  bool umidadeBaixa = umidade < 60;

  // Mostrar valores no Serial Monitor
  Serial.print("Fósforo: "); Serial.print(estadoFosforo);
  Serial.print(" | Potássio: "); Serial.print(estadoPotassio);
  Serial.print(" | LDR (pH simulado): "); Serial.print(ldrValue / 100.0);
  Serial.print(" | Umidade: "); Serial.print(umidade); Serial.print("%");
  Serial.print(" | relé (Irrigacao): "); Serial.print(LedValue);
  Serial.print(" | API: "); Serial.println(estadoAPI);
   
  // === AÇÃO: ATIVAR BOMBA ===

  // Atribui 1 para a API de estiver ligada
  int condicoesAPI = 0;
  if (estadoAPI) condicoesAPI++;
  // Conta quantas variáveis estão com valor falso (condição crítica)
  int condicoesCriticas = 0;
  if (!estadoFosforo) condicoesCriticas++;
  if (!estadoPotassio) condicoesCriticas++;
  if (phIdeal) condicoesCriticas++;
  if (umidadeBaixa) condicoesCriticas++;

  // Caso 2 ou mais sensores acusem problema a irrigação será acionado
  // Caso a API comunique que haverá chuva a irrigação será desativada
  if (condicoesCriticas >= 2 && condicoesAPI == 0) {
    digitalWrite(RELAY_PIN, HIGH);  // Liga a bomba
    digitalWrite(LED_PIN, HIGH);    // Liga o LED indicativo
  } else {
    digitalWrite(RELAY_PIN, LOW);   // Desliga a bomba
    digitalWrite(LED_PIN, LOW);     // Desliga o LED
  }

  delay(1000);  // Espera 1 segundo antes da próxima leitura
}
