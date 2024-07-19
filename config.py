import json
import os
from dotenv import load_dotenv
import boto3
import openai

# Global settings
GLOBAL_INSTRUCTIONS = (
    "You are the developer. I am providing a zipped file which contains code. "
    "I will ask you to modify this code according to my request. "
    "Provide a brief commit message and extended details of changes you made. "
    "Attach an output file to your response so I can download it. "
    "An output file should be a zipped file with the same name as the input file. "
    "Also attach a file in JSON format with the follwoing attributes: 'commit_message', 'extended_details'. "
)
DEFAULT_MODEL = "gpt-4o"

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
CARBON_MODEL         = os.getenv("CARBON_MODEL") or DEFAULT_MODEL
CARBON_INSTRUCTIONS  = os.getenv("CARBON_INSTRUCTIONS") + GLOBAL_INSTRUCTIONS
CARBON_FILE_PATH     = os.getenv("CARBON_FILE_PATH")
CARBON_REQUEST       = os.getenv("CARBON_REQUEST")
CARBON_ISSUE_ID      = os.getenv("CARBON_ISSUE_ID")
CARBON_PR_ID         = os.getenv("CARBON_PR_ID")
CARBON_OUTPUT_DIR    = os.getenv("CARBON_OUTPUT_DIR")


# Validate env variables
def validate_vars(extra_vars: list = None):
    required_vars = [
        "AWS_ACCESS_KEY",
        "AWS_SECRET_KEY",
        "AWS_BUCKET",
        "OPENAI_API_KEY",
        "CARBON_PROJECT",
        "CARBON_MODEL",
        "CARBON_INSTRUCTIONS"
    ]

    if extra_vars:
        required_vars.extend(extra_vars)

    params = {param: globals().get(param) for param in required_vars}

    for param, value in params.items():
        if not value:
            raise ValueError(f"Parameter {param} is missing or empty.")
        
    if not os.path.exists(CARBON_FILE_PATH):
        raise ValueError(f"File {CARBON_FILE_PATH} does not exist.")

    if not os.path.exists(CARBON_OUTPUT_DIR):
        try:
            os.makedirs(CARBON_OUTPUT_DIR)
        except Exception as e:
            raise ValueError(f"Could not create directory {CARBON_OUTPUT_DIR}: {e}")


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
