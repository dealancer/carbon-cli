import json
import os
from dotenv import load_dotenv
import boto3
import openai

# Global settings
GLOBAL_INSTRUCTIONS = (
    "You are the developer. I am providing a zipped file that contains code. "
    "I will ask you to modify this code according to my request. "
    "Provide a brief commit message and extended details of changes you made. "
    "Attach two output files in your response so I can download them: "
    "1. A zipped output file with the same name as the input file, containing the modified code. "
    "2. A JSON file named 'output_metadata.json' containing the following attributes: 'commit_message', 'extended_details'. "
    "Both files should be **explicitly attached** in your response, not just referenced in text."
)
DEFAULT_MODEL = "gpt-4o"

# Load environment variables from .env file
load_dotenv()

# AWS credentials
AWS_ACCESS_KEY          = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY          = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET              = os.getenv("AWS_BUCKET")

# OpenAI credentials
OPENAI_API_KEY          = os.getenv("OPENAI_API_KEY")

# Carbon settings
CARBON_PROJECT          = os.getenv("CARBON_PROJECT")
CARBON_MODEL            = os.getenv("CARBON_MODEL") or DEFAULT_MODEL
CARBON_INSTRUCTIONS     = os.getenv("CARBON_INSTRUCTIONS") + GLOBAL_INSTRUCTIONS
CARBON_WORK_DIR         = os.getenv("CARBON_WORK_DIR")
CARBON_META_FILENAME    = os.getenv("CARBON_META_FILENAME")
CARBON_PROJECT_FILENAME = os.getenv("CARBON_PROJECT_FILENAME")

# Request settings
CARBON_REQUEST          = os.getenv("CARBON_REQUEST")
CARBON_ISSUE_ID         = os.getenv("CARBON_ISSUE_ID")
CARBON_PR_ID            = os.getenv("CARBON_PR_ID")



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

    if not os.path.exists(CARBON_WORK_DIR):
        try:
            os.makedirs(CARBON_WORK_DIR)
        except Exception as e:
            raise ValueError(f"Could not create directory {CARBON_WORK_DIR}: {e}")

    file_path = os.path.join(CARBON_WORK_DIR, CARBON_PROJECT_FILENAME)
    if not os.path.exists(file_path):
        raise ValueError(f"File {CARBON_PROJECT_FILENAME} does not exist in {CARBON_WORK_DIR} directory.")

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
