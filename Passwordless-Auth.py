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
from PIL import Image
import os
import subprocess as sub
import csv
import boto3
import uuid

# -------------------- Initialisation of Global Variables -------------------- #
Phase1Validation = False
Phase2Validation = False
begin = False

# ----------------- Basic initialisation of Devices on System ---------------- #
text = 0
Buzzer = 21
Scanner = SimpleMFRC522()
CamLight = 13 
Button = 15
Camera = PiCamera() #csi connector



# ------------------ Cleanup to ensure the text are the same ----------------- #

def CleanText(unclean):
    nospaces = unclean.replace(" ", "")
    clean = nospaces.lower()
    return clean

# ------------------------- Grab AWS Creds from file ------------------------- #

print("Accessing Login Details")
with open("Pi_accessKeys.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        accessKeyID = row[0]
        secretAccessKey = row[1]


# ------------------------- Grab RFID code from file ------------------------- #
print("Accessting RFID Code")
with open("Authentication.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        Auth = row[0]
        Auth = CleanText(Auth)
        break


# ----------------------- Setting up Rekognition client ---------------------- #
print("initialising access to Rekognition client")
clientRek = boto3.client("rekognition", region_name="eu-west-2", 
aws_access_key_id=accessKeyID, aws_secret_access_key=secretAccessKey)
print("Rekognition connected")


# ------------------------- setting up the S3 client ------------------------- #
print("Initialising access to S3 Bucket client")
clientS3 = boto3.client('s3', aws_access_key_id=accessKeyID, 
aws_secret_access_key=secretAccessKey)

bucket = "adamstorage"

print("S3 Connected!")




# --------- RFID Card authentication as initial authentication stage --------- #
def RFIDValidation():
    print("Beginning RF Validation, Please Present Card... will take about 5 seconds")
    id, text = Scanner.read()
    print("Here is our details")
    print(text)
    text = CleanText(text)
    if text == Auth:
        authentication = True
        GPIO.cleanup()
        return authentication

    else:
        authentication = False
        GPIO.cleanup()
        return authentication
    
    

# --------- Validation using facial recognition from Rekognition API --------- #
def PhotoValidation():
    print("Beginning Photo, Please Point Camera Towards You!")
    time.sleep(3)
    print("Light will start flashing, after three flashes, camera will take photo!")
    for i in range (3):
        os.system("./piiotest writepin 13 1")
        time.sleep(1)
        os.system("./piiotest writepin 13 0")
        time.sleep(1)
    Camera.capture('img_Valid.jpg')
    print("photo is being taken")
    photoTaken = Image.open('img_Valid.jpg')
    photoTaken.save('img_Valid.jpg')
    matchAuth = CompareFaces()
    if matchAuth == True:
       authentication = True 
       print("True has been chosen!")
       return authentication

    else:
        authentication = False
        print("False has been chosen")
        return authentication

# ------------ Function for comparing faces using Rekognition API ------------ #
def CompareFaces():
    
    clientS3.download_file(bucket,"masterImage.jpg","masterImage.jpg")
    print("master iamge downloaded, beginning to open files")
    time.sleep(2)
    imageSource = open("masterImage.jpg", "rb")
    imageTarget = open("lsimg_Valid.jpg", "rb")

    print("both files have been opened, beginning comparison")
    time.sleep(2)
    response = clientRek.compare_faces(SimilarityThreshold=99, SourceImage={"Bytes": imageSource.read()}, TargetImage={"Bytes": imageTarget.read()})

    for faceMatch in response["FaceMatches"]:
        similarity = (faceMatch["similarity"])
        print("face matches with " + similarity + "% confidence")
        time.sleep(4)
        if faceMatch["similarity"] >= 99:
            print("Face Matches!")
            imageSource.close()
            imageTarget.close()
            os.remove("masterImage.jpg")
            return True
            
        else:
            print("Faces do not match!")
            imageSource.close()
            imageTarget.close()
            os.remove("masterImage.jpg")
            return False
            
            
            

# ------- Uploads the randomly generated code to allow the user access ------- #
def UnlockAWS():
    code = uuid.uuid4().hex.upper()[0:8]
    codeFile = open("staging.txt", "w")
    codeFile.write("Access Granted")
    codeFile.close()
    print(str(code))
    clientS3.upload_file("staging.txt", bucket, str(code) + ".txt")

    print("Here is The Code to your Personal Information, Enjoy!")
    time.sleep(20)
    CleanUp()

    

# ------------------ Alerts user of incorrect authentication ----------------- #
def IncorrectID():
    print("Wrong ID/Photo, Please Try again!")
    os.system("./piiotest writepin 21 0")
    time.sleep(2)
    for i in range (3):
        os.system("./piiotest writepin 21 1")
        time.sleep(0.5)
        os.system("./piiotest writepin 21 0")
        time.sleep(0.5)
    Phase1Validation = False
    Phase2Validation = False


def CleanUp():
        
        os.system("./piiotest writepin 13 0")
        os.system("./piiotest writepin 21 0")
        os.remove("img_Valid.jpg")
        print("System Cleanup Complete! Have a Nice Day!")
        GPIO.cleanup()
        



# ---------------------------------------------------------------------------- #
#                             ^Function code above^                            #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#                           Starting point of program                          #
# ---------------------------------------------------------------------------- #

print("ready to begin Authentication process, please press the button!")


#will keep the user here until they press the button to continue to the authentication
while begin == False:
    #Runs 'cat /proc/kmsg' and redirects output to a pipe
    p = sub.Popen(('cat', '/proc/kmsg'), stdout=sub.PIPE)



    for row in iter(p.stdout.readline, b''):
        row = row.decode()
        if "button_press" in row:
            print("button pressed! be ready to scan")
            begin = True
            break

while Phase1Validation == False and Phase2Validation == False:
# ---------------- initiates the validation process with RFID ---------------- #

#if incorrect then it will play incorrect noise and require a rescan of the card
    while Phase1Validation == False:
      Phase1Validation = RFIDValidation()
      print(Phase1Validation)
      if Phase1Validation == False:
          IncorrectID()

# ---------------- Initiates the validation process with face ---------------- #

#If the correct card is used, will begin second validation with photo 
#Which will be uploaded to AWS for analysis with Rekognition
    print("Passed Phase 1, Commencing Phase 2...")
    while Phase2Validation == False:
        Phase2Validation = PhotoValidation()
        print(Phase2Validation)
        if Phase2Validation == False:
            IncorrectID()



os.system("./piiotest writepin 13 1")
time.sleep(5)
os.system("./piiotest writepin 13 0")
UnlockAWS()
CleanUp()