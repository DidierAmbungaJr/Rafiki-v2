#include <Servo.h>
#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();
Servo leftLeg;
Servo rightLeg;

String currentExpression = "neutral";
String currentPosture = "idle";

const int leftPin = 8;
const int rightPin = 9;

void drawFace(const String &expr) {
  tft.fillScreen(TFT_BLACK);
  tft.drawRoundRect(10, 10, tft.width() - 20, tft.height() - 20, 8, TFT_DARKGREY);

  int cx = tft.width() / 2;
  int cy = tft.height() / 2;
  int eyeY = cy - 25;
  int mouthY = cy + 20;

  uint16_t eyeColor = TFT_WHITE;
  uint16_t mouthColor = TFT_WHITE;

  if (expr == "happy") {
    eyeColor = TFT_YELLOW;
    mouthColor = TFT_YELLOW;
  } else if (expr == "curious") {
    eyeColor = TFT_CYAN;
    mouthColor = TFT_CYAN;
  } else if (expr == "excited") {
    eyeColor = TFT_GREENYELLOW;
    mouthColor = TFT_GREENYELLOW;
  } else if (expr == "sleepy") {
    eyeColor = TFT_BLUE;
    mouthColor = TFT_BLUE;
  } else if (expr == "angry") {
    eyeColor = TFT_RED;
    mouthColor = TFT_RED;
  }

  tft.fillCircle(cx - 22, eyeY, 6, eyeColor);
  tft.fillCircle(cx + 22, eyeY, 6, eyeColor);

  if (expr == "happy") {
    tft.drawArc(cx, mouthY + 5, 46, 24, 200, 340, mouthColor);
  } else if (expr == "excited") {
    tft.drawArc(cx, mouthY, 60, 30, 200, 340, mouthColor);
  } else if (expr == "sleepy") {
    tft.drawLine(cx - 18, mouthY, cx + 18, mouthY, mouthColor);
  } else if (expr == "curious") {
    tft.drawLine(cx - 15, mouthY, cx + 15, mouthY, mouthColor);
    tft.drawLine(cx, mouthY + 8, cx, mouthY + 20, mouthColor);
  } else if (expr == "angry") {
    tft.drawLine(cx - 18, mouthY + 8, cx + 18, mouthY - 8, mouthColor);
  } else {
    tft.drawLine(cx - 18, mouthY, cx + 18, mouthY, mouthColor);
  }

  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextDatum(MC_DATUM);
  tft.drawString(expr, cx, tft.height() - 20, 2);
}

void setServoAngles(int leftAngle, int rightAngle) {
  leftLeg.write(constrain(leftAngle, 0, 180));
  rightLeg.write(constrain(rightAngle, 0, 180));
}

void doIdle() {
  currentPosture = "idle";
  setServoAngles(90, 90);
  drawFace(currentExpression);
}

void doDance() {
  for (int i = 0; i < 3; i++) {
    setServoAngles(25, 155);
    delay(180);
    setServoAngles(155, 25);
    delay(180);
  }
  doIdle();
}

void doLookLeft() {
  setServoAngles(50, 130);
  delay(200);
  doIdle();
}

void doLookRight() {
  setServoAngles(130, 50);
  delay(200);
  doIdle();
}

void applyCommand(String input) {
  String cmd = input;
  cmd.trim();

  if (cmd.length() == 0) {
    return;
  }

  if (cmd.indexOf("EXPRESSION") >= 0 || cmd.indexOf("expression") >= 0) {
    if (cmd.indexOf("happy") >= 0) currentExpression = "happy";
    else if (cmd.indexOf("curious") >= 0) currentExpression = "curious";
    else if (cmd.indexOf("excited") >= 0) currentExpression = "excited";
    else if (cmd.indexOf("sleepy") >= 0) currentExpression = "sleepy";
    else if (cmd.indexOf("angry") >= 0) currentExpression = "angry";
    else currentExpression = "neutral";

    drawFace(currentExpression);
    return;
  }

  if (cmd.indexOf("POSTURE") >= 0 || cmd.indexOf("posture") >= 0) {
    if (cmd.indexOf("dance") >= 0) {
      doDance();
    } else if (cmd.indexOf("left") >= 0) {
      doLookLeft();
    } else if (cmd.indexOf("right") >= 0) {
      doLookRight();
    } else {
      doIdle();
    }
    return;
  }

  if (cmd.indexOf("SERVO") >= 0 || cmd.indexOf("servo") >= 0) {
    int leftPos = 90;
    int rightPos = 90;

    int leftIndex = cmd.indexOf("left");
    int rightIndex = cmd.indexOf("right");

    if (leftIndex >= 0) {
      leftPos = cmd.substring(leftIndex + 4).toInt();
    }
    if (rightIndex >= 0) {
      rightPos = cmd.substring(rightIndex + 5).toInt();
    }

    setServoAngles(leftPos, rightPos);
    return;
  }

  if (cmd.indexOf("IDLE") >= 0 || cmd.indexOf("idle") >= 0) {
    doIdle();
    return;
  }

  if (cmd.indexOf("DANCE") >= 0 || cmd.indexOf("dance") >= 0) {
    doDance();
    return;
  }
}

void setup() {
  Serial.begin(115200);
  leftLeg.attach(leftPin);
  rightLeg.attach(rightPin);

  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);

  currentExpression = "neutral";
  drawFace(currentExpression);
  doIdle();
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.length() > 0) {
      applyCommand(command);
      Serial.println("{\"status\":\"ok\"}");
    }
  }

  delay(20);
}
