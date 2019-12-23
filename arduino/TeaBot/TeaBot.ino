#define lsensor A0
#define rsensor A1

#define lmotordir 12
#define lmotorspeed 5
#define rmotordir 13
#define rmotorspeed 6

#define buzz 1
int lw, lb, lm, rw, rb, rm, l, r, per = 0;
unsigned long perav = 0;

void rul(int speed, int dir) {
  int rr = constrain(speed - dir, 0, 255);
  int ll = constrain(speed + dir, 0, 255) - 0;
  analogWrite(lmotorspeed, ll);
  digitalWrite(lmotordir, LOW);
  analogWrite(rmotorspeed, rr);
  digitalWrite(rmotordir, LOW);

//  Serial.print(dir);
//  Serial.print(" ");
//  Serial.print(ll);
//  Serial.print(" ");
//  Serial.print(rr);
//  Serial.println();
}

void setup() {
  Serial.begin(9600);
  
  pinMode(lsensor, INPUT);
  pinMode(rsensor, INPUT);

  pinMode(lmotordir, OUTPUT);
  pinMode(lmotorspeed, OUTPUT);
  pinMode(rmotordir, OUTPUT);
  pinMode(rmotorspeed, OUTPUT);

  pinMode(buzz, OUTPUT);  
}

void loop() {
  // put your main code here, to run repeatedly:
  l = analogRead(lsensor);
  r = analogRead(rsensor);

//  Serial.print(l);
//  Serial.print(" ");
//  Serial.print(r);
//  Serial.print(" ");
//  Serial.print((l-r) * (-0.8));
//  Serial.println();
  if (l > 400 && r > 400) {
    if (millis() - perav > 500) {
      per++;
      
      perav = millis();
    } 
  }
  Serial.println(per); 

  rul(100, (l-r) * (-0.8) + (l-r)*(l-r)*(l-r) * (-0.0008));
//  rul(200, 0);
}
