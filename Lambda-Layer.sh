#!/bin/bash

# ==================================================
# ============= VARIABLES INITIATION ===============
# ==================================================

echo '========= INITIATING LOCAL VARIABLES =========='
AWS_REGION="YOUR_AWS_REGION_HERE"
LAMBDA_LAYER_S3BUCKET_NAME="YOUR_LAMBDA_S3_BUCKET_NAME" #https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html
AWS_PROFILE="NAME_OF_LOCAL_AWS_PROFILE" #https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html


# ==================================================
# ======== LAMBDA LAYER S3 BUCKET CREATION =========
# ==================================================

echo '======== CREATING LAMBDA LAYER S3 BUCKET ========'
aws s3api create-bucket --bucket $LAMBDA_LAYER_S3BUCKET_NAME --region $AWS_REGION --profile $AWS_PROFILE 


# ==================================================
# ========= PREPING THE PYTHON FOLDER ==============
# ==================================================
echo '======== INSTALLING DEPENDENCIES TO TEMPORARY PYTHON FOLDER ========'
mkdir -p python  # Create the python folder if it doesn't exist  
cd python # Access the python 
pip3 install --platform manylinux2014_x86_64 --target . --python-version 3.12 --only-binary=:all: fastapi fastapi-mail mangum pytz python-jose[cryptography] simplekml openai fastapi-mail ics langchain langchain-openai 
# The above pip install command installs the following dependencies for the pupose of this example, feel free to update the list to fit your use case.
### fastapi 
### fastapi-mail 
### mangum 
### pytz 
### python-jose[cryptography] 
### simplekml 
### openai 
### fastapi-mail 
### ics 
### langchain 
### langchain-openai

cd .. # Exit the python folder 

# Write A Code To Check Python Folder Size In Megabytes (MB)
# The following code has not fully tested. 
directory_path="./python"
threshold_size_mb=260
directory_size_mb=$(du -sm "$directory_path" | cut -f1)


# ==================================================
# ================ ZIP PYTHON FOLDER ===============
# ==================================================

echo '========= INITIATING LOCAL VARIABLES =========='
LAMBDA_LAYER_ZIP_NAME="python312_v1" # We use format PYTHON___PYTHON-VERSION___LAMBDA-LAYER-VERSION, Note this name must match the name of the layer LayerVersion > ContentUri of the apigw.json template.

echo '======== ZIP PYTHON FOLDER ========'
zip -r -q $LAMBDA_LAYER_ZIP_NAME.zip python # We use tool called ZiP but feel free to use ZiP tool of your choice. https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html#python-layer-packaging

# echo '======== (OPTIONAL) DELETING PRE-EXISTING LAMBDA LAYER ========'
# aws s3 rm s3://$LAMBDA_LAYER_S3BUCKET_NAME/ --recursive --region $AWS_REGION --profile $AWS_PROFILE # (Optional) Delete all pre-existing lamba layer 

echo '======== UPLADING LAMBA TO LAMBDA_LAYER_S3BUCKET_NAME ========'
aws s3 cp $LAMBDA_LAYER_ZIP_NAME.zip "s3://$LAMBDA_LAYER_S3BUCKET_NAME/" --storage-class STANDARD --region $AWS_REGION --profile $AWS_PROFILE 

# echo '======== (OPTIONAL) COPY LAMBDA LAYER ACCROSS TO ANOTHER BUCKET ========'
# aws s3 sync s3://$LAMBDA_LAYER_S3BUCKET_NAME s3://$LAMBDA_LAYER_S3BUCKET_NAME_ANOTHER_BUCKET --region $AWS_REGION --profile $AWS_PROFILE # (Optional) Copy the lambda layer to another bucket 


# ===================================================================
# ============== DELETE ZIP PYTHON FOLDER AND ZIP FILE ==============
# ===================================================================

# echo '========Delete ZIP File========'
rm -rf $LAMBDA_LAYER_ZIP_NAME.zip
rm -rf python
