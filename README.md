# Project Carbon

Project Carbon is an experimental AI agent CLI to be used with GitHub. It is supposed to by called by GitHub Actions.

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
   CARBON_REQUEST="Also add another route /name/{NAME} and output 'Hello {NAME}!'. Keep in mind that {name} is a parameter." \
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

### Asssociate an issue with PR

1. Run `carbon`:
   ```bash
   CARBON_ISSUE_ID=2 \
   CARBON_PR_ID=52 \
   python run.py map pr
   ```
