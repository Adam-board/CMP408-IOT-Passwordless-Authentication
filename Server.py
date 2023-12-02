from flask import Flask, render_template, request, redirect, send_file
import boto3
import re

app = Flask(__name__)


s3Client = boto3.client("S3")
bucket = "adamStorageBucket"


if __name__ == '__main__':
    app.run(debug=True)

# ----------------- Function to gain access to personal data ----------------- #

def AccessInfo(bucket, accessCode):

#Initialising the variable before using it   
    generateURL = 1

    try:
        generateURL = s3Client.generate_presigned_url("get_object", Params = 
    {"Bucket": bucket, "Key": accessCode + ".txt" }, ExpiresIn = 200)
    except Exception as e:
        pass

    return generateURL

# ---------------------- Function and route for homepage --------------------- #

@app.route("/")
def index():
    return render_template("index.html")

# ------------------ Function and route for data processing ------------------ #

@app.route("/DataProcess", methods=["POST"])
def DataProcess():

    info = "PersonalInfo"
    masterImage = "MasterImg"

    #Gathering the code from the input
    accessCode = request.form.get("codeInput")

    #Pattern for matching validation for code that has been inserted to ensure other files are not grabbed
    validation = r'^[a-zA-Z0-9]{8}$'

    #Checks to ensure the access code meets the requirements and isn't a injection attempt
    if re.match(validation, accessCode):
        matchResult = s3Client.list_objects_v2(Bucket=bucket, prefix=accessCode)
        information = s3Client.list_objects_v2(Bucket=bucket, prefix=info)
        image = s3Client.list_objects_v2(Bucket=bucket, prefix=masterImage)

        if 'Contents' in matchResult:
            #if the code exists
            contents = AccessInfo(bucket, accessCode)
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