#include <ETH.h>
#include <WiFi.h>
#include <WiFiAP.h>
#include <WiFiClient.h>
#include <WiFiGeneric.h>
#include <WiFiMulti.h>
#include <WiFiScan.h>
#include <WiFiServer.h>
#include <WiFiSTA.h>
#include <WiFiType.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <HTTPClient.h>

#include <SPI.h>
#include <MFRC522.h>
#include <ESP32Servo.h>
//#include <ESP8266WiFi.h>
//#include <ESP8266HTTPClient.h>
//#include <HTTPClient.h>

//#include<Servo.h>
#define SS_PIN    2  // ESP32 pin GIOP5 
#define RST_PIN   15 // ESP32 pin GIOP27 
int ir=14;
int servopin=26;
unsigned long counter;
bool camera = true;
String tag = "";
Servo myservo;
MFRC522 rfid(SS_PIN, RST_PIN);
int paid;
bool servo = false;
bool response_sent = false;

//192.168.0.102
#define SERVER_IP "" // PC address with emulation on host


#ifndef STASSID
#define STASSID ""
#define STAPSK ""
#endif

void setup() {
  
  Serial.begin(115200);
  SPI.begin(); // init SPI bus
  rfid.PCD_Init(); // init MFRC52
  pinMode(16,OUTPUT);
  digitalWrite(16,LOW);
  pinMode(ir,INPUT);
  myservo.attach(servopin);
  Serial.println("Tap an RFID/NFC tag on the RFID-RC522 reader");
  myservo.write(0);
  WiFi.begin(STASSID, STAPSK);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());
  
  Serial.println("HTTP server started");
}

void loop() {
  
//  Serial.println(digitalRead(ir));
  if(digitalRead(ir)==LOW)
  {
    Serial.println("Object detected");
    myservo.write(0);
    counter = 1;
    while(counter<=200){
    if (rfid.PICC_IsNewCardPresent()) {
    // new tag is available
    if (rfid.PICC_ReadCardSerial()) 
    { // NUID has been readed
      MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
       
    
        Serial.print("UID:");
      
        for (int i = 0; i < rfid.uid.size; i++) {

          
//          Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
//            Serial.print(rfid.uid.uidByte[i], HEX);
//          tag = tag + (String)(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
          tag = tag + String(rfid.uid.uidByte[i], HEX);
          
        }
        tag.toUpperCase();
        Serial.println();
        Serial.println(tag);
//        delay(2000);
        Serial.println();
      
      rfid.PICC_HaltA(); // halt PICC
      rfid.PCD_StopCrypto1(); // stop encryption on PCD
      if ((WiFi.status() == WL_CONNECTED)) {

    WiFiClient client;
    HTTPClient http;
    
    Serial.print("[HTTP] begin...\n");
    // configure traged server and url
    http.begin(SERVER_IP"/api/vehicle/vehicleReached");  // HTTP
    http.addHeader("Content-Type", "application/json");

    
    Serial.print("[HTTP] POST...\n");
    // start connection and send HTTP header and body


    String data = "{\"tag\":\""+tag+"\"}";
    Serial.println(data);
    int httpCode = http.POST(data);
    
    // httpCode will be negative on error
    if (httpCode > 0) {
      // HTTP header has been send and Server response header has been handled
      Serial.printf("[HTTP] POST... code: %d\n", httpCode);

      // file found at server
      if (httpCode == HTTP_CODE_OK) {
        const String& payload = http.getString();
        Serial.print("received payload: <<");
        response_sent = true;
        Serial.print(payload);
        Serial.print(">>\n");
      } 
    } 
    
    else 
    {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  }
    }

  camera = false;
//  delay(3000);
  
  break;
  }
  counter = counter + 1; 
    }

   if(camera)
   {
    Serial.println("Ran out of time so activating camera\n");
    digitalWrite(16,HIGH);
    response_sent = true;
//    delay(2000);
    }
    digitalWrite(16,LOW);


    if(response_sent){
        paid = 1;
    while(paid<6){
      HTTPClient http;
      Serial.print("[HTTP] begin...\n");
    // configure traged server and url
    http.begin(SERVER_IP"/api/vehicle/vehiclePaid");  // HTTP
    Serial.print("[HTTP] GET PAID...\n");
    int httpCode = http.GET();
    if (httpCode == 200) {
      servo = true;
      break;
    }
    paid++; 
    }
    }
    

    if (servo){
      delay(3000);
      myservo.write(90);
      delay(4000);
      myservo.write(0);
      }

      // file found at server
      }
   servo = false;
   myservo.write(0);
  camera = true;
  tag = "";
  response_sent = false;
  }
  
  
  
