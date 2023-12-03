from flask import Flask, render_template, request, redirect, send_file
import boto3
import re

app = Flask(__name__)


# ------------------------- Grab AWS Creds from file ------------------------- #

print("Accessing Login Details")
with open("Flask_accessKeys.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        accessKeyID = row[0]
        secretAccessKey = row[1]



# ------------------------- setting up the S3 client ------------------------- #
s3Client = boto3.client('s3', aws_access_key_id=accessKeyID, 
aws_secret_access_key=secretAccessKey)

bucket = "adamstorage"


if __name__ == '__main__':
    app.run(debug=True)

# ----------------- Function to gain access to personal data ----------------- #

def AccessInfo(bucket, accessCode):

#Initialising the variable before using it   
    generateURLAccess = 1

#Using presigned URLs gives secure access to the information within the S3 Bucket which expires to ensure it cannot be kept open longer than 5 minutes

    try:
        generateURLAccess = s3Client.generate_presigned_url("get_object", Params = 
    {"Bucket": bucket, "Key": accessCode + ".txt" }, ExpiresIn = 300)
    except Exception as e:
        pass

    try:
        generateURLImage = s3Client.generate_presigned_url("get_object", Params = 
    {"Bucket": bucket, "Key": "personalInfo.txt" }, ExpiresIn = 300)
    
    except Exception as e:
        pass


    try:
        generateURLInfo = s3Client.generate_presigned_url("get_object", Params = 
    {"Bucket": bucket, "Key": "masterImage.jpg" }, ExpiresIn = 300)

    except Exception as e:
        pass

    return generateURLAccess, generateURLImage, generateURLInfo

# ---------------------- Function and route for homepage --------------------- #

@app.route("/")
def index():
    return render_template("index.html")

# ------------------ Function and route for data processing ------------------ #

@app.route("/dataProcess", methods=["POST"])
def DataProcess():

    #Gathering the code from the input
    accessCode = request.form.get("insertCode")

    #Pattern for matching validation for code that has been inserted to ensure other files are not grabbed
    validation = r'^[a-zA-Z0-9]{8}$'

    #Checks to ensure the access code meets the requirements and isn't a injection attempt
    if re.match(validation, accessCode):
        matchResult = s3Client.list_objects_v2(Bucket=bucket, prefix=accessCode)
        information = 0
        image = 0

        if 'Contents' in matchResult:
            #if the code exists
            contents, masterImage, info = AccessInfo(bucket, accessCode)
        else:
            #tell user that their input does not exist
            text = "Input is not valid and this does not exist"
            return render_template('index.html', text=text)

        if contents == 0:
            text = "cannot find anything, please insert something"
            return render_template('index.html', text=text)
        else:
            #display the user's information on different page
            return render_template('DataDisplay.html', image = image, information = information)
    else:
        #informs the user that the code entered is invalid
        text = "The code inserted is invalid"
        return render_template('index.html', text=text)