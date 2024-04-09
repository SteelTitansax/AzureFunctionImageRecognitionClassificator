import requests
import azure.functions as func
import logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image
from io import BytesIO
from azure.storage.blob import BlobServiceClient
app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="images/inputFiles/{name}.jpeg",
                               connection="imageblobstoragedemo_STORAGE") 

def imageClassificatorFunctionApp(myblob: func.InputStream):

    logging.info(f"Python blob trigger function Activated : Blob to process"
                f"Blob: {myblob.name}"
                f"Blob Size: {myblob.length} bytes"
                )

    logging.info("Processing image ...")


    # Setting up variables

    key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    strEndpoint = "https://imagerecognitionIaName.cognitiveservices.azure.com/"
    
    # Starting Image Recognition Ai client

    credentials = CognitiveServicesCredentials(key)
    client = ComputerVisionClient(
        endpoint=strEndpoint,
        credentials=credentials)    

    url = "https://imageblobstoragedemo.blob.core.windows.net/" + str(myblob.name)
    
    
    # Analizing Image 

    image_analysis = client.analyze_image(url,visual_features=[VisualFeatureTypes.tags])

    logging.info("Image analized!!!")
    logging.info("Classifying Image...")
       
    booleanCat = False

    for tag in image_analysis.tags:

        logging.info(tag.name + " " + str(tag.confidence)) 

        if tag.name == "cat" and tag.confidence > 0.9:
            booleanCat = True

    # Classificating Image
    
    if booleanCat == True :

        logging.info("The image it's a cat, classifyng in cat's blob")

        # Code snippet for non-public blob storage

        '''
        from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_account_sas, BlobServiceClient
        from datetime import datetime, timedelta
        source_key = ''
        des_key = ''
        source_account_name = ''
        des_account_name = '23storage23'
        # genearte account sas token for source account
        sas_token = generate_account_sas(account_name=source_account_name, account_key=source_key,
                                        resource_types=ResourceTypes(
                                            service=True, container=True, object=True),
                                        permission=AccountSasPermissions(read=True),
                                        expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob_service_client = BlobServiceClient(
            account_url=f'https://{source_account_name}.blob.core.windows.net/', credential=source_key)
        des_blob_service_client = BlobServiceClient(
            account_url=f'https://{des_account_name}.blob.core.windows.net/', credential=des_key)

        source_container_client = source_blob_service_client.get_container_client(
            'copy')

        source_blob = source_container_client.get_blob_client('Capture.PNG')
        source_url = source_blob.url+'?'+sas_token
        # copy
        des_blob_service_client.get_blob_client(
            'test', source_blob.blob_name).start_copy_from_url(source_url)
        '''


        # Code snippet for public blob storage
        source_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        des_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        source_account_name = 'imageblobstoragedemo'
        des_account_name = 'imageblobstoragedemo'

        source_blob_service_client = BlobServiceClient(
            account_url=f'https://{source_account_name}.blob.core.windows.net/', credential=source_key)

        des_blob_service_client = BlobServiceClient(
            account_url=f'https://{des_account_name}.blob.core.windows.net/', credential=des_key)

        source_container_client = source_blob_service_client.get_container_client(
            'images/inputFiles')

        source_blob = source_container_client.get_blob_client(myblob.name.split("/")[2])
        source_url = source_blob.url
        
        # Copy file to cats classification blob storage

        des_blob_service_client.get_blob_client(
            'cats', myblob.name.split("/")[2]).start_copy_from_url(source_url)            

        logging.info("Python blob trigger function finished successfully!!!")

    else :
        logging.info("The file is not a cat!!! Skipping file...")
        logging.info("Python blob trigger function finished successfully!!!")





