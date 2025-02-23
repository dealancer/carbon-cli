# Project Carbon

Project Carbon is an experimental AI CLI agent to be used with GitHub. It is supposed to by called by GitHub Actions.

## Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| create issue | CARBON_ISSUE_ID<br/>CARBON_REQUEST | Creates a new thread for an issue, uploads the specified file, and runs the initial request through the AI. |
| map pr | CARBON_ISSUE_ID<br/>CARBON_PR_ID | Maps an existing issue thread to a pull request for continued conversation. |
| update issue | CARBON_ISSUE_ID<br/>CARBON_REQUEST | Updates an existing issue thread with a new request and runs it through the AI. |
| update pr | CARBON_PR_ID<br/>CARBON_REQUEST | Updates an existing pull request thread with a new request and runs it through the AI. |
| retrieve issue | CARBON_ISSUE_ID | Retrieves and displays all messages from an issue's thread. |
| retrieve pr | CARBON_PR_ID | Retrieves and displays all messages from a pull request's thread. |
| delete issue | CARBON_ISSUE_ID | Deletes issue's data. |
| delete pr | CARBON_PR_ID | Deletes PR's datas. |


## Setup

1. Clone this project into `carbon` directory:
   ```bash
   git clone git@github.com:dealancer/carbon.git .
   cd carbon
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Clone a project you would like to work with into `work` directory:
   ```bash
   git clone git@github.com:dealancer/flask-docker-boilerplate.git work/flask-docker-boilerplate
   ```

6. Prepare `.env` file by copying one from template:
   ```bash
   cp .env.example .env
   ```
   Then fill in the required values for AWS, OpenAI and Carbon settings in the `.env` file.

## Examples

### Create an issue

1. Zip `flask-docker-boilerplate` removing extra directories:
   ```bash
   zip -r work/flask-docker-boilerplate.zip work/flask-docker-boilerplate -x '*.git*' -x '*__pycache__*'
   ```

2. Run `carbon`:
   ```bash
   CARBON_ISSUE_ID=2 \
   CARBON_REQUEST="Add new route /example to output 'Hello World!' message." \
   python run.py create issue
   ```

3. Unzip `flask-docker-boilerplate.zip`:
   ```
   unzip -o work/flask-docker-boilerplate.zip
   ```

4. Check out changes:
   ```
   git -C work/flask-docker-boilerplate diff
   ```

5. Check out commit message:
   ```
   cat work/output.json
   ```

### Update an issue

1. Run `carbon`:
   ```bash
   CARBON_ISSUE_ID=2 \
   CARBON_REQUEST="Also add another route /name/{name} and output 'Hello {name}!'. Keep in mind that {name} is a parameter." \
   python run.py update issue
   ```

2. Unzip `flask-docker-boilerplate.zip`:
   ```
   unzip -o work/flask-docker-boilerplate.zip
   ```

3. Check out changes:
   ```
   git -C work/flask-docker-boilerplate diff
   ```

4. Check out commit message:
   ```
   cat work/output.json
   ```

### Asssociate an issue with a PR

1. Run `carbon`:
   ```bash
   CARBON_ISSUE_ID=2 \
   CARBON_PR_ID=123 \
   python run.py map pr
   ```

###  Update a PR

1. Run `carbon`:
   ```bash
   CARBON_PR_ID=123 \
   CARBON_REQUEST="Add another route /name/{age} and output 'Are you {age} years old?'. Keep in mind that {age} is a parameter." \
   python run.py update pr
   ```

2. Unzip `flask-docker-boilerplate.zip`:
   ```
   unzip -o work/flask-docker-boilerplate.zip
   ```

3. Check out changes:
   ```
   git -C work/flask-docker-boilerplate diff
   ```

4. Check out commit message:
   ```
   cat work/output.json
   ```
### Delete issue

1. Run `carbon`:
   ```bash
   CARBON_ISSUE_ID=2 \
   python run.py delete issue
   ```

### Delete PR

1. Run `carbon`:
   ```bash
   CARBON_PR_ID=123 \
   python run.py delete pr
   ```
