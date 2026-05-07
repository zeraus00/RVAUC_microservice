#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_SSD1306.h>

// -------------------- WIRE/PINS CONFIG DUE TO THE CONFLICT SLOTS --------------------
#define SS_PIN 5 
#define RST_PIN 27
#define BUZZER_PIN 25

// OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// WIFI CONFIG
const char* ssid = "Chlaus";
const char* password = "chlaus'-iphone";

// RVAUCMS API URL
String apiURL = "http://172.20.10.14:2620/session-broker/sign-in";
String token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0aW9uTmFtZSI6InN0YXRpb24xIiwiaWF0IjoxNzY0NzAwNDc1LCJleHAiOjIwODAyNzY0NzV9.pXbCchvsc9uP5E6bbMzcHQZHHL90yFdcCijTKp7oHgM";

MFRC522 rfid(SS_PIN, RST_PIN);

// -------------------- SETUP --------------------
void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);

  Wire.begin(21, 22);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)){ 
    Serial.println("OLED failed");
    while(true); 
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println("RFID System Booting...");
  display.display();

  SPI.begin();
  rfid.PCD_Init();

  connectWiFi();

  display.clearDisplay();
  display.setCursor(0,0);
  display.println("Ready...");
  display.display();
}

// -------------------- LOOP --------------------
void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  // UID to string
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if(rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
    if (i < rfid.uid.size - 1) uid += " ";
  }
  uid.toUpperCase();

  Serial.println("Card UID: " + uid);

  sendToServer(uid);

  rfid.PICC_HaltA();
}

// -------------------- SEND TO DJANGO --------------------
void sendToServer(String uid) {
  if(WiFi.status() != WL_CONNECTED){
    connectWiFi();
  }

  HTTPClient http;
  http.begin(apiURL);
  http.addHeader("Authorization", "Bearer " + token);
  http.addHeader("Content-Type", "application/json");

  String json = "{\"method\": \"rfidUid\", \"stationName\": \"station1\", \"identifier\": \"" + uid + "\"}";
  int httpCode = http.POST(json);

  if(httpCode > 0){
    String response = http.getString();
    Serial.println("Response: " + response);

    // Parse response
    String status = getValue(response, "status");
    String name   = getValue(response, "name");
    String sid    = getValue(response, "sid");
    String time   = getValue(response, "time");

    if(status == "SUCCESS"){
      buzzSuccess();
    } else {
      buzzFail();
    }

    displayMessage(status, name + " " + sid, uid, time);

  } else {
    Serial.println("Failed to reach server");
    displayMessage("ERROR", "Server Failed", uid, "No Time");
  }

  http.end();
}

// -------------------- SIMPLE JSON PARSER --------------------
String getValue(String json, String key){
  int start = json.indexOf(key);
  if(start < 0) return "";

  start = json.indexOf(":", start) + 2;
  int end = json.indexOf("\"", start);

  return json.substring(start, end);
}

// -------------------- DISPLAY MESSAGE --------------------
void displayMessage(String status, String info, String uid, String timeStr){
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(0,0);
  display.println(status);

  display.setTextSize(1);
  display.setCursor(0,25);
  display.println(info);

  display.setCursor(0,40);
  display.println("UID: " + uid);

  display.setCursor(0,50);
  display.println(timeStr);
  display.display();
}

// -------------------- BUZZER --------------------
void buzzSuccess() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(100);
  digitalWrite(BUZZER_PIN, LOW);
}

void buzzFail() {
  for(int i=0;i<2;i++){
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

// -------------------- WIFI --------------------
void connectWiFi(){
  Serial.print("Connecting...");
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
}


//-------library used for this sketch------//

//          MFRC522 by GithubCommunity
//    Adafruit SSD1306 or Adafruit GFX Library