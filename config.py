import json
import os
from dotenv import load_dotenv
import boto3
import openai

# Load environment variables from .env file
load_dotenv()

# AWS credentials
AWS_ACCESS_KEY       = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY       = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET           = os.getenv("AWS_BUCKET")

# OpenAI credentials
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")

# Carbon settings
CARBON_PROJECT       = os.getenv("CARBON_PROJECT")
CARBON_MODEL         = os.getenv("CARBON_MODEL")
CARBON_INSTRUCTIONS  = os.getenv("CARBON_INSTRUCTIONS")
CARBON_FILENAME      = os.getenv("CARBON_FILENAME")
CARBON_REQUEST       = os.getenv("CARBON_REQUEST")
CARBON_ISSUE_ID      = os.getenv("CARBON_ISSUE_ID")
CARBON_PR_ID         = os.getenv("CARBON_PR_ID")

# Get S3 client using AWS credentials
def get_s3_client():
    session = boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    return session.client("s3")

# Get configuration from S3 bucket
def get_config() -> dict:
    s3client = get_s3_client()

    try:
        response = s3client.get_object(
            Bucket=AWS_BUCKET,
            Key=f"{CARBON_PROJECT}.json"
        )
        return json.loads(response["Body"].read())
    except:
        return {}

# Save configuration to S3 bucket
def save_config(new_config: dict):
    s3client = get_s3_client()
    s3client.put_object(
        Bucket=AWS_BUCKET,
        Key=f"{CARBON_PROJECT}.json",
        Body=json.dumps(new_config)
    )

ai_client = openai.Client(
    api_key=OPENAI_API_KEY
)
