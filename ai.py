from config import *


def get_assistant():
    config = get_config()

    if "assistant_id" in config:
        ai_client.beta.assistants.update(
            assistant_id=config["assistant_id"], instructions=CARBON_INSTRUCTIONS
        )
        return config["assistant_id"]

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

    config["assistant_id"] = new_assistant.id
    save_config(config)

    return new_assistant.id


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
    
    # if CARBON_ISSUE_ID in config["threads_by_issue"]:
    #    raise ValueError(f"Thread for issue {CARBON_ISSUE_ID} already exists.")

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


def get_thread_by_issue():
    config = get_config()

    if CARBON_ISSUE_ID not in config["threads_by_issue"]:
        raise ValueError(f"Thread for issue {CARBON_ISSUE_ID} does not exist.")

    return config["threads_by_issue"][CARBON_ISSUE_ID]


def get_thread_by_pr():
    config = get_config()

    if CARBON_PR_ID not in config["threads_by_pr"]:
        raise ValueError(f"Thread for PR {CARBON_PR_ID} does not exist.")

    return config["threads_by_pr"][CARBON_PR_ID]


def run_thread(thread_id):
    assistant_id = get_assistant()

    run = ai_client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    if run.status == "completed":
        process_thread(thread_id, run.id)


def retrieve_thread(thread_id):
    #ai_client.beta.threads.retrieve(thread_id)
    process_thread(thread_id)


def process_thread(thread_id, run_id = None):
    if run_id is None:
        messages = ai_client.beta.threads.messages.list(
            thread_id=thread_id
        )
    else:
        messages = ai_client.beta.threads.messages.list(
            thread_id=thread_id,
            run_id=run_id
        )

    answer = []

    for message in messages:
        if message.role == "assistant":
            print(message)
            for block in message.content:
                if block.type == "text":
                    answer.append({"type": "text", "text": block.text.value})
                    if block.text.annotations:
                        for annotation in block.text.annotations:
                            if annotation.type == "file_path":
                                answer.append(
                                    {
                                        "type": "file",
                                        "file": save_file(
                                            annotation.file_path.file_id
                                        ),
                                        "filename": os.path.basename(
                                            annotation.text.split(":")[-1]
                                        ),
                                    },
                            )
                elif block.type == "file":
                    answer.insert(
                        0,
                        {
                            "type": "file",
                            "file": save_file(block.file.file_id),
                        },
                    )

    save_messages_to_file(answer)


def save_file(file_id: str) -> str:
    base_filename = os.path.basename(CARBON_FILE_PATH)
    file_path = os.path.join(CARBON_OUTPUT_DIR, base_filename)
    file_content = ai_client.files.download(file_id=file_id)

    with open(file_path, "wb") as file:
        file.write(file_content)

    return file_path


def save_messages_to_file(messages: list[dict]):
    file_path = os.path.join(CARBON_OUTPUT_DIR, "messages.txt")

    if not os.path.exists(CARBON_OUTPUT_DIR):
        os.makedirs(CARBON_OUTPUT_DIR)

    with open(file_path, "w") as file:
        for message in messages:
            if message["type"] == "text":
                file.write(f"Text: {message['text']}\n")
            elif message["type"] == "code":
                file.write(f"Code: {message['code']}\n")
            elif message["type"] == "file":
                file.write(f"File Path: {message['file']}\n")

