//Verifica a vibração máxima permitida com base no valor da variável "LIMIAR_VIBRACAO", caso ultrapasse esse limiar envia um alerta
//

#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>
#include <LiquidCrystal_I2C.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>


// Inicializa o LCD I2C no endereço 0x27 com tamanho 16x2
LiquidCrystal_I2C lcd(0x27, 20, 4);

void iniciar_lcd() {
  lcd.begin(20, 4);
  lcd.backlight();  // Garante que o backlight do LCD esteja ligado
  lcd.print("LCD OK!");
  delay(1000);
}

void print_lcd_and_serial(const String& message) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(message);
  Serial.println(message);
}

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
  print_lcd_and_serial("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  print_lcd_and_serial("WiFi conectado!");
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
  print_lcd_and_serial("Chip ID: " + String(chipidStr));

  JsonDocument doc;
  doc["serial"] = chipidStr; // Adiciona o Chip ID ao JSON
  int httpcode = post_data(doc, init_sensor); // Envia o Chip ID para a API

  if (httpcode >= 200 && httpcode < 300) {
    print_lcd_and_serial("Sensor iniciado com sucesso!");
    delay(1000); // delay para garantir que a mensagem seja visível
    iniciou_sensor = true;
  } else {
    print_lcd_and_serial(String("Falha ao iniciar o sensor na API: ") + String(httpcode));
    delay(1000); // delay para garantir que a mensagem seja visível
  }
}

MPU6050 mpu;

// Pinos do LDR, Relé, LED e Buzzer
const int LDR_PIN = 34;      // Pino do LDR
const int RELAY_PIN = 32;    // Pino do Relé
const int LED_PIN = 15;      // Pino do LED
const int BUZZER_PIN = 2;    // Pino do Buzzer

// Variáveis
float vibracaoTotal = 0;
float vibracaoMedia = 0;
const int NUM_AMOSTRAS = 100;
const float LIMIAR_VIBRACAO = 1.0;  // Ajuste esse valor com base nos testes


void setup() {
  Serial.begin(115200);
  
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  // Configuração do PWM para o buzzer
  ledcSetup(0, 2000, 8); // Canal 0, 2kHz, 8 bits
  ledcAttachPin(BUZZER_PIN, 0);

  // Inicializa o I2C e o MPU6050
  Wire.begin(21, 22);  // SDA: 21, SCL: 22 para ESP32

  iniciar_lcd();

  mpu.initialize();
  while (!mpu.testConnection()) {
    print_lcd_and_serial("MPU6050 nao conectado!");
    delay(1000);
  }

  conectaWiFi();

}

void loop() {

  if (!iniciou_sensor) {
    iniciar_sensor();
  }

  JsonDocument doc;
  doc["serial"] = chipidStr; // Adiciona o Chip ID ao JSON

  // Lê o valor do LDR
  int ldrValue = analogRead(LDR_PIN);
  int lux = map(ldrValue, 0, 4095, 0, 2000); 
  doc["lux"] = lux; // Adiciona o valor de luminosidade ao JSON

  // Lê a temperatura do MPU6050
  int rawTemp = mpu.getTemperature();
  float tempC = rawTemp / 340.0 + 36.53;  //Converte o valor bruto para graus Celsius
  doc["temperatura"] = tempC; // Adiciona a temperatura ao JSON
  // Exibe a temperatura e a condição claro/escuro no LCD e no Monitor Serial
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(tempC, 1);
  lcd.print(" C");

  Serial.print("Temperatura: ");
  Serial.print(tempC, 1);
  Serial.print(" C |");

  lcd.setCursor(0, 1);
  if (lux < 500) {
    lcd.print("Condicao: Escuro");
    Serial.print(" Condição: Escuro");
    Serial.print(" (Lux: " + String(lux) + ") |");
    digitalWrite(LED_PIN, LOW);
    digitalWrite(RELAY_PIN, LOW);
    noTone(BUZZER_PIN);
  } else {
    lcd.print("Condicao: Claro");
    Serial.print(" Condição: Claro");
    Serial.print(" (Lux: " + String(lux) + ") |");
    for (int i = 0; i < 3; i++) { // Buzzer e LED piscam juntos por 3x
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(RELAY_PIN, HIGH);
      tone(BUZZER_PIN, 1000);
      delay(300);
      digitalWrite(LED_PIN, LOW);
      digitalWrite(RELAY_PIN, LOW);
      noTone(BUZZER_PIN);
      delay(300);
    }
  }
  delay(1000);

  // Lê os valores brutos de aceleração
  int16_t ax_raw, ay_raw, az_raw;
  mpu.getAcceleration(&ax_raw, &ay_raw, &az_raw);

  // Converte para g (gravidade da Terra)
  float ax = ax_raw / 16384.0;
  float ay = ay_raw / 16384.0;
  float az = az_raw / 16384.0;
  doc["acelerometro_x"] = ax; // Adiciona o valor de aceleração X ao JSON
  doc["acelerometro_y"] = ay; // Adiciona o valor de aceleração Y ao JSON
  doc["acelerometro_z"] = az; // Adiciona o valor de aceleração Z ao JSON

  // Lê os valores brutos de rotação
  int16_t gx_raw, gy_raw, gz_raw;
  mpu.getRotation(&gx_raw, &gy_raw, &gz_raw);

    // Converte para g (gravidade da Terra)
  float gx = gx_raw / 131.0;
  float gy = gy_raw / 131.0;
  float gz = gz_raw / 131.0;

  // ### Calcula o nível de vibração ###
  float somaVibracao = 0;

  for (int i = 0; i < NUM_AMOSTRAS; i++) {

    // Calcular o módulo da aceleração total
    float modulo = sqrt(ax * ax + ay * ay + az * az);

    // Subtrair 1g da gravidade estática
    float vibracao = abs(modulo - 1.0);
    somaVibracao += vibracao;

    delay(5); // pequeno intervalo para capturar vibrações rápidas
  }

  vibracaoMedia = somaVibracao / NUM_AMOSTRAS;
  doc["vibracao_media"] = vibracaoMedia; // Adiciona a vibração média ao JSON

  Serial.print(" Vibracao media: ");
  Serial.print(vibracaoMedia, 2);
  Serial.print(" |");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Vibracao media: ");
  lcd.print(vibracaoMedia, 2);

  if (vibracaoMedia > LIMIAR_VIBRACAO) {
    Serial.print(" ⚠️ Vibração anormal detectada! ⚠️ |");
    lcd.setCursor(0, 1);
    lcd.print("#ALERTA DE VIBRACAO#");

    for (int i = 0; i < 3; i++) { // Buzzer e LED piscam juntos por 3x
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(RELAY_PIN, HIGH);
      tone(BUZZER_PIN, 1000);
      delay(300);
      digitalWrite(LED_PIN, LOW);
      digitalWrite(RELAY_PIN, LOW);
      noTone(BUZZER_PIN);
      delay(300);
    }
  
  } else {
    Serial.print(" Vibração normal |");
    lcd.setCursor(0, 1);
    lcd.print("Vibracao normal!");
  }
  //delay(1000);

    // Alerta de temperatura
  if (tempC > 70.0) {
    lcd.setCursor(0, 1);
    lcd.print("#ALERTA: >70 C#");
    Serial.print(" ⚠️ TEMPERATURA ALTA! ⚠️ |");

    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(RELAY_PIN, HIGH);
      tone(BUZZER_PIN, 1500);
      delay(300);
      digitalWrite(LED_PIN, LOW);
      digitalWrite(RELAY_PIN, LOW);
      noTone(BUZZER_PIN);
      delay(300);
    }
  }

  // Exibe os valores de aceleração X, Y, Z no LCD e Monitor Serial
  lcd.setCursor(0, 2);
  lcd.print("Accelerometer:");
  
  lcd.setCursor(0, 3);
  lcd.print("x:");
  lcd.print(ax, 1);
  lcd.print(" y:");
  lcd.print(ay, 1);
  lcd.print(" z:");
  lcd.print(az, 1);

 
  //Imprime os dados
  Serial.print(" X:");
  Serial.print(ax, 2);
  Serial.print(" Y:");
  Serial.print(ay, 2);
  Serial.print(" Z:");
  Serial.println(az, 2);

  if (iniciou_sensor) {
    // Envia os dados para a API
    int httpcode = post_data(doc, post_sensor);
    if (httpcode >= 200 && httpcode < 300) {
      Serial.println("Dados enviados com sucesso!");
    } else {
      Serial.println("Falha ao enviar dados.");
    }
  }

  delay(5000);
}
