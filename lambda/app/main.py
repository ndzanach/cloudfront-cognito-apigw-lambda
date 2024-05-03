"""
Simple Serverless FastAPI with AWS Lambda
https://www.deadbear.io/simple-serverless-fastapi-with-aws-lambda/
"""

import json
from .routes.api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from fastapi import FastAPI
from app.src.v1.models.engine import (
    AuthMethod,
)

AuthMethodInstance = AuthMethod()

app = FastAPI()

origins = ["http://localhost:PORT_NUMBER", "https://localhost", "https://PROJECT_NAME_.com"]
# Replace PORT_NUMBER and PROJECT_NAME_ above as per your use case

allow_headers = [
    "Content-Type",
    "X-Amz-Date",
    "Authorization",
    "X-Api-Key",
    "X-Amz-Security-Token",
    "TOKEN_NAME",
]
# Update the above headers as per your use case, Note: TOKEN_NAME

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600,
)
# Update the above values as per your use case 


app.include_router(api_router)



# https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html

'''
The code below validates the TOKEN_NAME sent from the user on every request through the API Gateway for requests coming from the query methods only. All requests coming through the api-gateway auth methods (login, sign-up, etc.) are open.
'''
def generatePolicy(principalId, effect, resource):
    authResponse = {}
    authResponse["principalId"] = principalId
    if effect and resource:
        policyDocument = {}
        policyDocument["Version"] = "2012-10-17"
        policyDocument["Statement"] = []
        statementOne = {}
        statementOne["Action"] = "execute-api:Invoke"
        statementOne["Effect"] = effect
        statementOne["Resource"] = resource
        policyDocument["Statement"] = [statementOne]
        authResponse["policyDocument"] = policyDocument
        authResponse["context"] = {
            "stringKey": "stringval",
            "numberKey": 123,
            "booleanKey": True,
        }
    authResponse_JSON = json.dumps(authResponse)
    return authResponse_JSON


def handler(event, context):
    # print(event)
    # print(context)

    if event.get("authorizationToken") or event.get("TOKEN_NAME"):
        # Do something or return, etc.
        token = event.get("authorizationToken") or event.get("TOKEN_NAME")
        # print(f"TOKEN IS:  {token}")
        access = AuthMethodInstance.verify_token(token)
        if access == "allow":
            # print("authorized")
            response = generatePolicy("user", "Allow", event["methodArn"])
        elif access == "deny":
            # print("unauthorized")
            response = generatePolicy("user", "Deny", event["methodArn"])
        elif access == "unauthorized":
            # print("unauthorized")
            raise Exception("Unauthorized")  # Return a 401 Unauthorized response
            # return "unauthorized"
        try:
            return json.loads(response)
        except BaseException:
            # print("unauthorized")
            return "unauthorized"

    asgi_handler = Mangum(app)
    response = asgi_handler(
        event, context
    )  # Call the instance with the event arguments

    return response
