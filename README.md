# Project Carbon

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Clone `flask-docker-boilerplate` into parent directory (it could really be any project you want to work with):
   ```bash
   git clone git@github.com:dealancer/flask-docker-boilerplate.git
   ```

5. Zip `flask-docker-boilerplate` project removing extra directories:
   ```bash
   zip -r flask-docker-boilerplate.zip flask-docker-boilerplate -x '*.git*' -x '*__pycache__*'
   ```

6. Create `carbon-output` directory in the parent directory.

7. Copy `.env.example` to `.env` in the root directory:
   ```bash
   cp .env.example .env
   ```
   Then fill in the required values for AWS, OpenAI and Carbon settings in the `.env` file.

## Run

1. Set Request settings in `.env` file (`CARBON_REQUEST`, `CARBON_ISSUE_ID`).
2. Run `python run.py create issue`.
