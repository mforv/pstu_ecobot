#include "GY_85.h"
#include <Wire.h>
#include <Servo.h> 
#include "Kalman.h"
#include <NewPing.h> //подключение библиотеки
#include <VL53L0X.h>

#define MY_SERIAL_ECHO 1
#define TRIGGER_PIN  8 //пин подключения контакта Trig
#define ECHO_PIN     11 //Пин подключения контакта Echo
#define MAX_DISTANCE 700 //максимально-измеряемое расстояние

#define Laser_Pin 7
#define IR_Pin 12

VL53L0X sensor;

//создание объекта дальномера 
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); 

GY_85 GY85;     //create the object
float dt = 0.01;
float delta = 0.0;
float gx2 = 0;
float gy2 = 0;
float gz2 = 0;
Servo myservoY; 
Servo myservoX; 
double cureS=0;
double cureSX=0;
int last_cureS_int=0;
int last_cureSX_int=0;
int setCoordY = 180;
int setCoordX = 180;

Kalman kalmanX;
Kalman kalmanY;
double accXangle; // Angle calculate using the accelerometer
double accYangle;
double temp;
double gyroXangle = 180; // Angle calculate using the gyro
double gyroYangle = 180;
double compAngleX = 180; // Calculate the angle using a Kalman filter
double compAngleY = 180;
double kalAngleX; // Calculate the angle using a Kalman filter
double kalAngleY;
uint32_t timer;

double sumkalAngleY=0;
long uS_cm = 0;

void setup()
{
  Wire.begin();
  delay(10);
  // Настройка вывода платы в режим "Выход"
  pinMode (Laser_Pin, OUTPUT);
  pinMode (IR_Pin, INPUT);
  //
  Serial.begin(57600);
  delay(10);
  //
  sensor.init();
  sensor.setTimeout(500);
 
  // Start continuous back-to-back mode (take readings as
  // fast as possible).  To use continuous timed mode
  // instead, provide a desired inter-measurement period in
  // ms (e.g. sensor.startContinuous(100)).
  sensor.startContinuous();
  delay(10);
  //
  GY85.init();
  //----
  //float old_z = GY85.gyro_z(GY85.readGyro());
  //for (int i=0; i < 10; i++)
  //{
  //  //delay(300);
  //  float new_z = GY85.gyro_z(GY85.readGyro());
  //  delta += new_z - old_z;
  //}
  //delta /= 10;
  //----------
  myservoY.attach(9);
  myservoY.write(80);
  myservoX.attach(10);
  //myservoX.write(40);
  cureS = 90;

  kalmanX.setAngle(180); // Set starting angle
  kalmanY.setAngle(180);
  timer = micros();

  delay(10);
}

void cmd_proc()
{
  int x1 = Serial.parseInt();
  if (x1==2){//ROTOADDR  = 0x02; # адрес компьютера
    int x2 = Serial.parseInt();
    if (x2==170){//CMD       = 0xaa; # признак начала команды
      int x3 = Serial.parseInt();
      if (x3==2){//SET_CT    = 0x02; # команда - "встать в положение"
        float fx = Serial.parseInt();
        float fx2 = Serial.parseInt();
        setCoordY = fx;
        setCoordX = fx2;
        Serial.print("1 170 3\n");
      }
      if (x3==3){//ASK_CT    = 0x03; # команда - "вернуть положение"
        Serial.print("1 170 3 ");
        Serial.print(setCoordY);
        Serial.print(" ");
        Serial.print(setCoordX);
        Serial.print("\n");
      }
      //--------------------Пример добавления функции-------------
      if (x3==13){//
        //flaser ? digitalWrite (Laser_Pin, HIGH) : digitalWrite (Laser_Pin, LOW); // Включить/off лазер
        digitalWrite (Laser_Pin, HIGH);
        Serial.print("1 170 13\n");     
      }
      if (x3==14){//
        digitalWrite (Laser_Pin, LOW);
        Serial.print("1 170 14\n");     
      }
      //----------------------------------------------------------
      if (x3==15){//ASK_USONIC    = 0x15; # команда - ""
        Serial.print("1 170 15 ");
        Serial.print(uS_cm*10);
        Serial.print("\n");
      }
      if (x3==16){//ASK_VLMM    = 0x16; # команда - ""
        Serial.print("1 170 16 ");
        Serial.print(sensor.readRangeContinuousMillimeters());
        Serial.print("\n");
      }
    }
  }
}

void loop()
{
  static int i=0;
  int accX = GY85.accelerometer_x( GY85.readFromAccelerometer() );
  int accY = GY85.accelerometer_y( GY85.readFromAccelerometer() );
  int accZ = GY85.accelerometer_z( GY85.readFromAccelerometer() );

  int cx = GY85.compass_x( GY85.readFromCompass() );
  int cy = GY85.compass_y( GY85.readFromCompass() );
  int cz = GY85.compass_z( GY85.readFromCompass() );

  float gyroX = GY85.gyro_x( GY85.readGyro() );
  float gyroY = GY85.gyro_y( GY85.readGyro() );
  float gyroZ = GY85.gyro_z( GY85.readGyro() );
  float gt = GY85.temp  ( GY85.readGyro() );

  /* Calculate the angls based on the different sensors and algorithm */
  accYangle = (atan2(accX,accZ)+PI)*RAD_TO_DEG;
  accXangle = (atan2(accY,accZ)+PI)*RAD_TO_DEG;    

  unsigned long microsval = micros();
  double gyroXrate = (double)gyroX/131.0;
  double gyroYrate = -((double)gyroY/131.0);
  gyroXangle += gyroXrate*((double)(microsval-timer)/1000000); // Calculate gyro angle without any filter  
  gyroYangle += gyroYrate*((double)(microsval-timer)/1000000);
  //gyroXangle += kalmanX.getRate()*((double)(micros()-timer)/1000000); // Calculate gyro angle using the unbiased rate
  //gyroYangle += kalmanY.getRate()*((double)(micros()-timer)/1000000);

  compAngleX = (0.93*(compAngleX+(gyroXrate*(double)(microsval-timer)/1000000)))+(0.07*accXangle); // Calculate the angle using a Complimentary filter
  compAngleY = (0.93*(compAngleY+(gyroYrate*(double)(microsval-timer)/1000000)))+(0.07*accYangle);  

  kalAngleX = kalmanX.getAngle(accXangle, gyroXrate, (double)(microsval-timer)/1000000); // Calculate the angle using a Kalman filter
  kalAngleY = kalmanY.getAngle(accYangle, gyroYrate, (double)(microsval-timer)/1000000);
  //static double dk = kalAngleY0-kalAngleY;
  static double k = 0.03;
  static double kX = 0.01;
  static double dt;
  dt = (double)(microsval-timer)/1000000;
  //sumkalAngleY += kalAngleY * dt;
  //cureS = cureS + k*sumkalAngleY;
  cureS -= (setCoordY-kalAngleY)*k;
  cureSX -= (setCoordX-kalAngleX)*kX;
  //cureS -= cureS -(int)kalAngleY;
  //cureS -= k*dk;
  //kalAngleY0 = kalAngleY;
  int cureS_int = (int)cureS;
  int cureSX_int = (int)cureSX;
  if (cureS_int<70) cureS_int = 70;
  if (cureS_int>150) cureS_int = 150;
  if (cureSX_int<30) cureSX_int = 30;
  if (cureSX_int>65) cureSX_int = 65;
  if (abs(last_cureS_int-cureS_int)>1){
    myservoY.attach(9);
    myservoY.write(cureS_int);
    last_cureS_int = cureS_int;
  }
  if (abs(last_cureSX_int-cureSX_int)>1){
    myservoX.attach(10);
    myservoX.write(cureSX_int);
    last_cureSX_int = cureSX_int;
  }
  if (++i >= 100) {
    i=0;
    //
    int uS = sonar.ping(); //получение отклика датчика в микросекундах
    uS_cm = sonar.convert_cm(uS);
    //
    myservoY.detach();
    myservoX.detach();
    //Serial.print(accXangle);
    //Serial.print("\t");
    //Serial.print(accYangle);
    //Serial.print("\t"); 

    //Serial.print(gyroXangle);
    //Serial.print("\t");
    //Serial.print(gyroYangle);
    //Serial.print("\t");

    //Serial.print(compAngleX);
    //Serial.print("\t");
    //Serial.print(compAngleY); 
    //Serial.print("\t");
    /*Serial.print(uS_cm*10); 
    Serial.print(" ");
    Serial.print(!digitalRead(IR_Pin)); 
    Serial.print(" ");
    Serial.print(sensor.readRangeContinuousMillimeters());
    Serial.print(" ");
    
    Serial.print(kalAngleX);
    Serial.print(" ");
    Serial.print(kalAngleY);
    Serial.print(" ");
    Serial.print(cureS);*/
    //Serial.print(" ");

    //Serial.print(temp);Serial.print("\t");

    //Serial.print("\n");
    //static int flaser=0;
       //myservoY.attach(9);
       //myservoY.write(x);
       //myservoY.detach();          
    //----------------------обмен с ПК------------------
    cmd_proc();
    //--------------------------------------------------
  }
  
  timer = micros();
  delay(1); // The accelerometer's maximum samples rate is 1kHz
  
  /*gx2 += (gx-delta)*dt;
   gy2 += (gy-delta)*dt;
   gz2 += (gz-delta)*dt;
   
   if (++i >= 100) {
   i=0;
   Serial.print  ( "accelerometer" );
   Serial.print  ( " x:" );
   Serial.print  ( ax );
   Serial.print  ( " y:" );
   Serial.print  ( ay );
   Serial.print  ( " z:" );
   Serial.print  ( az );
   
   Serial.print  ( "  compass" );
   Serial.print  ( " x:" );
   Serial.print  ( cx );
   Serial.print  ( " y:" );
   Serial.print  ( cy );
   Serial.print  (" z:");
   Serial.print  ( cz );
   
   Serial.print  ( "  gyro" );
   Serial.print  ( " x:" );
   Serial.print  ( gx );
   Serial.print  ( " y:" );
   Serial.print  ( gy );
   Serial.print  ( " z:" );
   Serial.print  ( gz );
   Serial.print  ( " gyro temp:" );
   Serial.println( gt );
   
   Serial.print  ( "  gyro2" );
   Serial.print  ( " x:" );
   Serial.print  ( gx2 );
   Serial.print  ( " y:" );
   Serial.print  ( gy2 );
   Serial.print  ( " z:" );
   Serial.println  ( gz2 );
   cureS = (150-(int)az);
   myservoY.write(cureS);
   }
   delay(dt*1000);             // only read every 0,5 seconds, 10ms for 100Hz, 20ms for 50Hz
   */
}

