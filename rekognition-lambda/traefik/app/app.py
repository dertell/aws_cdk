from flask import Flask, request
from flask import render_template
import boto3
import requests
import time
import os

app = Flask(__name__)

apiId = os.environ.get("apiid")
usagePlanId = os.environ.get("usageplanid")
endpoint = os.environ.get("endpoint")

@app.route("/keygen", methods=["POST"])
def keygen():
    #session = boto3.Session(profile_name="account2")
    client = boto3.client("apigateway", region_name='eu-central-1')
    name = request.form["keygen"]

    response = client.create_api_key(
            name=name+'key',
            description='key for image search',
            enabled=True,
            stageKeys=[{'restApiId':apiId,
                        'stageName':'neuefische'}])
    id = response["id"]
    value = response["value"]
    response = client.create_usage_plan_key(
            usagePlanId=usagePlanId,
            keyId=id,
            keyType='API_KEY')
    time.sleep(7)
    return render_template("/search.html", value=value)


@app.route("/search", methods=["POST"])
def search():
    key = request.form["apikey"]
    url=endpoint
    value = request.form["search"]
    params = {"search":value.lower()}
    headers = {'X-API-Key': key}
    r = requests.get(url+"images", params=params, headers=headers)
    z = r.json()
    b = z["message"]
    return render_template('/result.html', results=b) 
     
     
@app.route("/", methods=["GET", "POST"])
def index():    
    return render_template('/index.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)