# ---------------------------------------------------------------------------- #
#                    CMP408 IoT and Cloud Secure Development                   #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
#                             Adam Board - 2005335                             #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
#              Mini Project - Passwordless 2-Factor Authentication             #
# ---------------------------------------------------------------------------- #



import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from picamera import PiCamera
import subprocess
from PIL import Image
import os
import subprocess as sub
import csv
import boto3


# ------------------------- Grab AWS Creds from file ------------------------- #
with open("loginDetails.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        accessKeyID = row[2]
        secretAccessKey = row[3]


# ------------------------- Grab RFID code from file ------------------------- #
with open("Authentication.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        Auth = row[1]


# ----------------------- Setting up Rekognition client ---------------------- #
clientRek = boto3.client("rekognition", region_name="eu-west-2", 
aws_Access_key_id=accessKeyID, aws_secret_access_key=secretAccessKey)



# ------------------------- setting up the S3 client ------------------------- #
clientS3 = boto3.client('s3', aws_access_key_id=accessKeyID, 
aws_secret_access_key=secretAccessKey)

bucketName = "AdamStorageBucket"

# -------------------- Initialisation of Global Variables -------------------- #
Phase1Validation = False
Phase2Validation = False
begin = False

# ----------------- Basic initialisation of Devices on System ---------------- #
text = "Incorrect"
Buzzer = 21 #pin40
Reader = SimpleMFRC522
CamLight = 13 #pin33
Button = 15
Camera = PiCamera()

# ----------------------- inital setup of all the pins ----------------------- #
def InitialSetup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(Buzzer, GPIO.OUT)
    GPIO.setup(CamLight, GPIO.OUT)

    #Sets button GPIO to input and set initial value to be off (low)
    GPIO.setup(Button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



# --------- RFID Card authentication as initial authentication stage --------- #
def RFIDValidation():
    print("Beginning RF Validation, Please Present Card...")
    try:
        id, text = Reader.read()
        print(id)
        print(text)
    except:
        print("An error has occured")
        exit()
    if text == Auth:
        Phase1Validation == True
    else:
        Phase1Validation == False
    

# --------- Validation using facial recognition from Rekognition API --------- #
def PhotoValidation():
    print("Beginning Photo, Please Point Camera Towards You!")
    time.sleep(3)
    print("Light will start flashing, after three flashes, camera will take photo!")
    time.sleep(5)
    for i in range (3):
        GPIO.output(CamLight, 1)
        time.sleep(2)
        GPIO.output(CamLight, 0)
        time.sleep(2)
    Camera.capture('./photos/img_Valid.jpg')
    photoTaken = Image.open('./photos/img_Valid.jpg')
    photoTaken.save('./photos/img_Valid.jpg')
    matchAuth = compareFaces(photoTaken)
    if matchAuth = True:
       Phase2Validation = True 
       return

    else:
        Phase2Validation = False
        incorrectID()


def compareFaces(targetFile):
    
    imageSource = open("./photos/img_Valid.jpg", "rb")
    imageTarget = s3.open()

    response = clientRek.compare_faces(SimilarityThreshold=99, SourceImage={"Bytes": imageSource.read()}, TargetImage={"Bytes": imageTarget.read()})

    for faceMatch in response["FaceMatches"]:
        similarity = str(faceMatch["similarity"])
        print("face matches with " + similarity + "% confidence")
        if faceMatch["similarity"] > 99:
            print("Face Matches!")
            imageSource.close()
            imageTarget.close()
            return True
            
        else:
            print("Faces do not match!")
            imageSource.close()
            imageTarget.close()
            return False
            
            
            


    
    

# ------- Uploads the randomly generated code to allow the user access ------- #
def UnlockAWS():

    print("Here is The Code to your Personal Information, Enjoy!")
    

# ------------------ Alerts user of incorrect authentication ----------------- #
def IncorrectID():
    print("Wrong ID/Photo, Please Try again!")
    GPIO.output(Buzzer, 0)
    time.sleep(2)
    for i in range (4):
        GPIO.output(Buzzer, 1)
        time.sleep(2)
        GPIO.output(Buzzer, 0)
        time.sleep(2)
    begin == False
    Phase1Validation = False
    Phase2Validation = False
    RFIDValidation()



# ---------------------------------------------------------------------------- #
#                             ^Function code above^                            #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#                           Starting point of program                          #
# ---------------------------------------------------------------------------- #

print("ready to begin Authentication process, please press the button!")


#will keep the user here until they press the button to continue to the authentication
while begin == False:
    time.sleep(5)
    #Runs 'cat /proc/kmsg' and redirects output to a pipe
    p = sub.Popen(('cat', '/proc/kmsg'), stdout=sub.PIPE)



    for row in iter(p.stdout.readline, b''):
        row = row.decode()
        if "button_press" in row:
            begin = True



#used through an LKM for security purposes to setup the pins being used
InitialSetup()

# ---------------- initiates the validation process with RFID ---------------- #
RFIDValidation()

#If the correct card is used, will begin second validation with photo 
#Which will be uploaded to AWS for analysis with Rekognition
if Phase1Validation == True:
    print("Passed Phase 1, Commencing Phase 2...")
    PhotoValidation()


#if incorrect then it will play incorrect noise and require a rescan of the card
elif Phase1Validation == False:
    IncorrectID()

if Phase2Validation == True & Phase1Validation == True:
    GPIO.output(CamLight, 1)
    time.sleep(5)
    GPIO.output(CamLight, 0)
    UnlockAWS()
    GPIO.cleanup()