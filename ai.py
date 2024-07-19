from config import *


def get_assistant_id(config):
    return config["assistant_id"] if "assistant_id" in config else None


def create_assistant():
    assistant_id = get_assistant_id(config)

    if not assistant_id:
        new_assistant = ai_client.beta.assistants.create(
            model=CARBON_MODEL,
            instructions=CARBON_INSTRUCTIONS,
            name=CARBON_PROJECT,
            tools=[
                {
                    "type": "code_interpreter",
                }
            ]
        )
        config = get_config()
        config["assistant_id"] = new_assistant.id
        save_config(config)
    else:
        ai_client.beta.assistants.update(
            assistant_id=assistant_id, instructions=CARBON_INSTRUCTIONS
        )


def upload_file():
    with open(CARBON_FILE_PATH, 'rb') as file:
        file_object = ai_client.files.create(
            file=(os.path.basename(CARBON_FILE_PATH), file),
            purpose="assistants"
        )
    return file_object.id


def create_thread_for_issue():
    config = get_config()
    if not "threads_by_issue" in config:
        config["threads_by_issue"] = {}
    
    if CARBON_ISSUE_ID in config["threads_by_issue"]:
        raise ValueError(f"Thread for issue {CARBON_ISSUE_ID} already exists.")

    file_id = upload_file()

    thread = ai_client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": CARBON_REQUEST,
                "attachments": [
                    {"file_id": file_id, "tools": [{"type": "code_interpreter"}]}
                ],
            }
        ]
    )

    config["threads_by_issue"][CARBON_ISSUE_ID] = thread.id
    save_config(config)

    return thread.id


def update_thread_for_issue():
    config = get_config()

    if "threads_by_issue" not in config or CARBON_ISSUE_ID not in config["threads_by_issue"]:
        raise ValueError(f"Thread for issue {CARBON_ISSUE_ID} does not exist.")

    thread_id = config["threads_by_issue"][CARBON_ISSUE_ID]

    ai_client.beta.threads.update(
        config["threads_by_issue"][CARBON_ISSUE_ID],
        messages=[
            {
                "role": "user",
                "content": CARBON_REQUEST
            }
        ]
    )

    return thread_id


def map_thread_to_pr_out_of_issue():
    config = get_config()

    if "threads_by_issue" not in config or CARBON_ISSUE_ID not in config["threads_by_issue"]:
        raise ValueError(f"Thread for issue {CARBON_ISSUE_ID} does not exist.")

    if not "threads_by_pr" in config:
        config["threads_by_pr"] = {}

    config["threads_by_pr"][CARBON_PR_ID] = config["threads_by_issue"][CARBON_ISSUE_ID]
    save_config(config)


def update_thread_for_pr():
    config = get_config()

    if "threads_by_pr" not in config or CARBON_PR_ID not in config["threads_by_pr"]:
        raise ValueError(f"Thread for PR {CARBON_PR_ID} does not exist.")

    thread_id = config["threads_by_pr"][CARBON_PR_ID]

    ai_client.beta.threads.update(
        thread_id,
        messages=[
            {
                "role": "user",
                "content": CARBON_REQUEST
            }
        ]
    )

    return thread_id


def run_thread(thread_id) -> list[dict]:
    assistant_id = get_assistant_id()

    run = ai_client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    answer = []

    if run.status == "completed":
        messages = ai_client.beta.threads.messages.list(
            thread_id=thread_id, run_id=run.id
        )
        for message in messages:
            if message.role == "assistant":
                for block in message.content:
                    if block.type == "text":
                        answer.append({"type": "text", "text": block.text.value})
                    elif block.type == "code":
                        answer.append({"type": "code", "code": block.code.value})
                    elif block.type == "file":
                        answer.insert(
                            0,
                            {
                                "type": "image",
                                "file": save_file(block.file.file_id),
                            },
                        )

    return answer

def save_file(file_id: str) -> str:
    base_filename = os.path.basename(CARBON_FILE_PATH)
    file_path = os.path.join(CARBON_OUTPUT_DIR, base_filename)

    file_content = ai_client.files.download(file_id=file_id)

    if not os.path.exists(CARBON_OUTPUT_DIR):
        os.makedirs(CARBON_OUTPUT_DIR)

    with open(file_path, "wb") as file:
        file.write(file_content)

    return file_path
