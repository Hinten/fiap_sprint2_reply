#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============================================================================
// SISTEMA DE ALERTA DE ENCHENTES - FIAP GS1
// Utiliza sensores para monitorar nível de água e envia alertas via API.
// Sensores: LDR (nível simulado) e HC-SR04 (ultrassônico).
// Relé aciona bomba e LED indica status. Buzzer emite alerta sonoro.
// Botão simula resposta da API meteorológica.
// ============================================================================

// === DEFINIÇÃO DE PINOS ===
#define LDR_PIN      32  // Pino analógico para simular nível de água via LDR
#define RELAY_PIN    4   // Relé que aciona a bomba
#define LED_PIN      2   // LED indicativo da bomba
#define BUTTON_API   18  // Botão para simular resposta da API meteorológica
#define ECHO_PIN     25  // ECHO do HC-SR04 (medição de distância)
#define TRIG_PIN     26  // TRIG do HC-SR04 (disparo de pulso)
#define BUZZER_PIN   23  // Buzzer de alerta

// === CONFIGURAÇÃO DE REDE E API ===
const char* ssid = NETWORK_SSID;
const char* password = NETWORK_PASSWORD;
const int canal_wifi = 6; // Canal do WiFi (no uso real, deixar automático)
const char* endpoint_api = API_URL; // URL da API
const String init_sensor = String(endpoint_api) + "/init/";     // Endpoint de inicialização
const String post_sensor = String(endpoint_api) + "/leitura/";  // Endpoint de envio de dados

// === FUNÇÃO DE CONEXÃO WI-FI ===
void conectaWiFi() {
  WiFi.begin(ssid, password, canal_wifi);
  Serial.print("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
}

// === FUNÇÃO DE ENVIO DE DADOS PARA API ===
int post_data(JsonDocument& doc, const String& endpoint_api) {
  Serial.println("Enviando dados para a API: " + endpoint_api);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(endpoint_api);

    String jsonStr;
    serializeJson(doc, jsonStr);
    int httpCode = http.POST(jsonStr);

    if (httpCode > 0) {
      Serial.println("Status code: " + String(httpCode));
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.println("Erro na requisição");
    }
    http.end();
    return httpCode;
  } else {
    Serial.println("WiFi desconectado, impossível fazer requisição!");
  }

  return -1; // Retorna -1 se não conseguiu enviar os dados

}

// === IDENTIFICAÇÃO DO DISPOSITIVO ===
char chipidStr[17];
bool iniciou_sensor = false;

void iniciar_sensor() {
  uint64_t chipid = ESP.getEfuseMac();
  sprintf(chipidStr, "%016llX", chipid);
  Serial.printf("Chip ID: %s\n", chipidStr);

  JsonDocument doc;
  doc["serial"] = chipidStr; // Adiciona o Chip ID ao JSON
  int httpcode = post_data(doc, init_sensor); // Envia o Chip ID para a API

  if (httpcode >= 200 && httpcode < 300) {
    Serial.println("Sensor iniciado com sucesso!");
    iniciou_sensor = true;
  } else {
    Serial.println("Falha ao iniciar o sensor na API.");
  }
}

// === CONFIGURAÇÃO INICIAL ===
void setup() {
  Serial.begin(115200);

  // Configuração dos sensores
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Configuração dos botões
  pinMode(BUTTON_API, INPUT_PULLUP);

  // Configuração dos atuadores
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Configuração do PWM para o buzzer
  ledcSetup(0, 2000, 8); // Canal 0, 2kHz, 8 bits
  ledcAttachPin(BUZZER_PIN, 0);

  conectaWiFi();
}

// === FUNÇÃO DE LEITURA DO SENSOR ULTRASSÔNICO (HC-SR04) ===
float readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  int duration = pulseIn(ECHO_PIN, HIGH);
  return duration * 0.034 / 2;
}


// === LOOP PRINCIPAL ===
void loop() {
  // Cria objeto JSON para envio dos dados

  if (!iniciou_sensor) {
    iniciar_sensor();
  }

  JsonDocument doc;
  doc["serial"] = chipidStr;

  // Leitura do botão da API meteorológica
  bool leituraAPIMetereologica = digitalRead(BUTTON_API);
  bool LedValue = digitalRead(LED_PIN);

  // Leitura do LDR (nível simulado do bueiro)
  int ldrValue = analogRead(LDR_PIN); // 0 a 4095 no ESP32

  // Leitura do sensor ultrassônico (nível do leito)
  float distance = readDistanceCM();

  // Condições críticas
  bool nivelBueiroCritico = (ldrValue > 3000); // Nível elevado no bueiro
  bool nivelLeitoCritico = (distance > 300);   // Nível elevado no leito (>3m)
  int condicoesCriticas = 0;
  if (nivelBueiroCritico) condicoesCriticas++;
  if (nivelLeitoCritico) condicoesCriticas++;

  // Mostrar valores no Serial Monitor
  Serial.print("LDR (Nível Bueiro): "); Serial.print(ldrValue / 10.0); Serial.print("cm");
  Serial.print(" | Nível Leito: "); Serial.print(distance); Serial.print("cm");
  Serial.print(" | Relé (Envio de Dados): "); Serial.print(LedValue);
  Serial.print(" | API: "); Serial.println(leituraAPIMetereologica);

  // Preenche o JSON para envio
  doc["bueiro"] = ldrValue / 10.0;
  doc["leito"] = distance;
  doc["rele"] = LedValue;

  serializeJsonPretty(doc, Serial);

  // === AÇÃO: ATIVAR ALERTA ===
  if (condicoesCriticas >= 1 or leituraAPIMetereologica == LOW) {
    Serial.println("ALERTA: Nível elevado de água detectado!");
    digitalWrite(RELAY_PIN, HIGH);  // Liga a bomba
    digitalWrite(LED_PIN, HIGH);    // Liga o LED

    // Sequência de tons no buzzer
    tone(BUZZER_PIN, 261); delay(100);
    tone(BUZZER_PIN, 293); delay(100);
    tone(BUZZER_PIN, 329); delay(100);
    tone(BUZZER_PIN, 349); delay(100);
    tone(BUZZER_PIN, 392); delay(100);
    noTone(BUZZER_PIN);
  } else {
    digitalWrite(RELAY_PIN, LOW);   // Desliga a bomba
    digitalWrite(LED_PIN, LOW);     // Desliga o LED
    noTone(BUZZER_PIN);
  }

  // Envia os dados para a API
  if (iniciou_sensor){
    digitalWrite(LED_PIN, HIGH);
    post_data(doc, post_sensor);
    digitalWrite(LED_PIN, LOW);
  }

  delay(2000); // Aguarda 2 segundos para próxima leitura
}
