//Verifica a vibração máxima permitida com base no valor da variável "LIMIAR_VIBRACAO", caso ultrapasse esse limiar envia um alerta
//

#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>
#include <LiquidCrystal_I2C.h>

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

// Inicializa o LCD I2C no endereço 0x27 com tamanho 16x2
LiquidCrystal_I2C lcd(0x27, 20, 4);

void setup() {
  Serial.begin(115200);
  
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Inicializa o I2C e o MPU6050
  Wire.begin(21, 22);  // SDA: 21, SCL: 22 para ESP32
  lcd.begin(20, 4);
  lcd.backlight();  // Garante que o backlight do LCD esteja ligado
  lcd.print("LCD OK!");
  delay(1000);

  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 nao conectado!");
    while (1);
  }
}

void loop() {

  // Lê o valor do LDR
  int ldrValue = analogRead(LDR_PIN);
  int lux = map(ldrValue, 0, 4095, 0, 2000); 

  // Lê a temperatura do MPU6050
  int rawTemp = mpu.getTemperature();
  float tempC = rawTemp / 340.0 + 36.53;  //Converte o valor bruto para graus Celsius

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
    Serial.print(" Condição: Escuro |");
    digitalWrite(LED_PIN, LOW);
    digitalWrite(RELAY_PIN, LOW);
    noTone(BUZZER_PIN);
  } else {
    lcd.print("Condicao: Claro");
    Serial.print(" Condição: Claro |");
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

  delay(5000);
}
