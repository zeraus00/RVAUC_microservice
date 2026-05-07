#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

// -------------------- CONFIG --------------------
#define SS_PIN 5
#define RST_PIN 27
#define BUZZER_PIN 25

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// TEST MODE (set true to run without hardware/server)
#define TEST_MODE true

const char* ssid = "Chlaus";
const char* password = "chlaus'-iphone";

String BASE_URL = "http://172.20.10.14:2620/session-broker/sign-in";
String STATION_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0aW9uTmFtZSI6InN0YXRpb24xIiwiaWF0IjoxNzY0NzAwNDc1LCJleHAiOjIwODAyNzY0NzV9.pXbCchvsc9uP5E6bbMzcHQZHHL90yFdcCijTKp7oHgM";
String STATION_NAME = "station1";
String ROOM_NAME = "406";

MFRC522 rfid(SS_PIN, RST_PIN);

// -------------------- DATA MODEL --------------------
struct AttendanceResult {
  bool valid;

  String sessionStatus;

  String attendanceStatus;
  String attendanceTime;

  String professorName;

  String classNumber;

  String courseCode;
  String courseName;

  String startTime;
  String endTime;
};

// -------------------- SETUP --------------------
void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);

  Wire.begin(21, 22);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED failed");
    while (true);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Booting...");
  display.display();

  SPI.begin();
  rfid.PCD_Init();

  #if !TEST_MODE
    connectWiFi();
  #endif

  displayMessage("READY", "System Online", "", "");
}

// -------------------- LOOP --------------------
void loop() {

  #if TEST_MODE
    runTest();
    delay(5000);
    return;
  #endif

  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  Serial.println("UID: " + uid);

  AttendanceResult result = sendToServer(uid);

  if (result.valid) {
    displayResult(result);
    buzzSuccess();
  } else {
    displayMessage("ERROR", "Invalid Response", uid, "");
    buzzFail();
  }

  rfid.PICC_HaltA();
}

// -------------------- SERVER FLOW --------------------
AttendanceResult sendToServer(String uid) {
  AttendanceResult empty;
  empty.valid = false;

  #if TEST_MODE
    return parseAttendanceResponse(getMockResponse());
  #endif

  if (WiFi.status() != WL_CONNECTED) {
    displayMessage("ERROR", "No WiFi", uid, "");
    return empty;
  }

  String token = signIn(uid);

  if (token.length() == 0) {
    return empty;
  }

  return takeAttendance(token);
}

// -------------------- SIGN IN --------------------
String signIn(String uid) {
  HTTPClient http;

  http.begin(BASE_URL + "/session-broker/sign-in");

  http.addHeader("Authorization", "Bearer " + STATION_TOKEN);
  http.addHeader("Content-Type", "application/json");

  String json =
    "{"
      "\"method\":\"rfidUid\","
      "\"stationName\":\"" + STATION_NAME + "\","
      "\"identifier\":\"" + uid + "\","
      "\"noCache\":\"true\""
    "}";

  int code = http.POST(json);

  if (code <= 0) return "";

  String response = http.getString();
  http.end();

  DynamicJsonDocument doc(1024);
  deserializeJson(doc, response);

  if (doc["status"] != "SUCCESS") return "";
  if (!doc["data"]["success"]) return "";

  return doc["data"]["result"].as<String>();
}

// -------------------- ATTENDANCE --------------------
AttendanceResult takeAttendance(String token) {
  AttendanceResult data;
  data.valid = false;

  HTTPClient http;

  http.begin(BASE_URL + "/enrollments/attendance/rfid-scan");

  http.addHeader("Authorization", "Bearer " + token);
  http.addHeader("Content-Type", "application/json");

  String json =
    "{"
      "\"room\":\"" + ROOM_NAME + "\""
    "}";

  int code = http.POST(json);

  if (code <= 0) return data;

  String response = http.getString();
  http.end();

  return parseAttendanceResponse(response);
}

// -------------------- PARSER (TESTABLE CORE) --------------------
AttendanceResult parseAttendanceResponse(String response) {
  AttendanceResult data;
  data.valid = false;

  DynamicJsonDocument doc(4096);

  DeserializationError err = deserializeJson(doc, response);
  if (err) return data;

  if (doc["status"] != "SUCCESS") return data;
  if (!doc["data"]["success"]) return data;

  JsonObject result = doc["data"]["result"];

  data.sessionStatus = result["session"]["status"].as<String>();

  data.attendanceStatus = result["attendance"]["status"].as<String>();
  data.attendanceTime = result["attendance"]["time"].as<String>();

  String first = result["professor"]["firstName"].as<String>();
  String last = result["professor"]["surname"].as<String>();
  data.professorName = first + " " + last;

  data.classNumber = result["class"]["classNumber"].as<String>();

  data.courseCode = result["course"]["code"].as<String>();
  data.courseName = result["course"]["name"].as<String>();

  data.startTime = result["offering"]["startTime"].as<String>();
  data.endTime = result["offering"]["endTime"].as<String>();

  data.valid = true;
  return data;
}

// -------------------- DISPLAY --------------------
void displayResult(AttendanceResult r) {
  displayMessage(
    r.attendanceStatus,
    r.classNumber + " " + r.courseCode + " " + r.courseName,
    r.classNumber,
    r.attendanceTime
  );

  Serial.println("Professor: " + r.professorName);
  Serial.println("Session: " + r.sessionStatus);
}

// -------------------- MOCK TEST --------------------
#if TEST_MODE
String getMockResponse() {
  return R"rawliteral(
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "result": {
      "session": { "status": "ACTIVE" },
      "attendance": { "status": "PRESENT", "time": "08:10" },
      "professor": { "firstName": "Maria", "surname": "Santos" },
      "class": { "classNumber": "CS101" },
      "course": { "code": "CS", "name": "Data Structures" },
      "offering": { "startTime": "08:00", "endTime": "10:00" }
    }
  }
}
)rawliteral";
}

void runTest() {
  Serial.println("\n--- TEST MODE ---");

  AttendanceResult r =
    parseAttendanceResponse(getMockResponse());

  if (r.valid) {
    Serial.println(r.professorName);
    Serial.println(r.courseName);
    Serial.println(r.attendanceTime);
  }

  delay(2000);
}
#endif

// -------------------- DISPLAY HELPER --------------------
void displayMessage(String a, String b, String c, String d) {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println(a);
  display.println(b);
  display.println("UID: " + c);
  display.println(d);
  display.display();
}

// -------------------- BUZZER --------------------
void buzzSuccess() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(100);
  digitalWrite(BUZZER_PIN, LOW);
}

void buzzFail() {
  for (int i = 0; i < 2; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

// -------------------- WIFI --------------------
void connectWiFi() {
  Serial.print("Connecting WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
}