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
    file_path = os.path.join(CARBON_WORK_DIR, CARBON_PROJECT_FILENAME)
    with open(file_path, 'rb') as file:
        file_object = ai_client.files.create(
            file=(os.path.basename(file_path), file),
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
                ]
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

    ai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=CARBON_REQUEST
    )

    return thread_id


def map_thread_to_pr_out_of_issue():
    config = get_config()

    if "threads_by_issue" not in config or CARBON_ISSUE_ID not in config["threads_by_issue"]:
        raise ValueError(f"Thread for issue {CARBON_ISSUE_ID} does not exist.")

    if CARBON_PR_ID in config["threads_by_pr"]:
        raise ValueError(f"Thread for PR {CARBON_PR_ID} already exists.")

    if not "threads_by_pr" in config:
        config["threads_by_pr"] = {}

    config["threads_by_pr"][CARBON_PR_ID] = config["threads_by_issue"][CARBON_ISSUE_ID]
    save_config(config)


def update_thread_for_pr():
    config = get_config()

    if "threads_by_pr" not in config or CARBON_PR_ID not in config["threads_by_pr"]:
        raise ValueError(f"Thread for PR {CARBON_PR_ID} does not exist.")

    thread_id = config["threads_by_pr"][CARBON_PR_ID]

    ai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=CARBON_REQUEST
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


def delete_thread_for_issue():
    config = get_config()

    if "threads_by_issue" not in config or CARBON_ISSUE_ID not in config["threads_by_issue"]:
        raise ValueError(f"Thread for issue {CARBON_ISSUE_ID} does not exist.")

    del config["threads_by_issue"][CARBON_ISSUE_ID]

    save_config(config)


def delete_thread_for_pr():
    config = get_config()

    if "threads_by_pr" not in config or CARBON_PR_ID not in config["threads_by_pr"]:
        raise ValueError(f"Thread for PR {CARBON_PR_ID} does not exist.")

    del config["threads_by_pr"][CARBON_PR_ID]

    save_config(config)


def run_thread(thread_id):
    assistant_id = get_assistant()

    run = ai_client.beta.threads.runs.create_and_poll(
        assistant_id=assistant_id,
        thread_id=thread_id,
    )

    if run.status == "completed":
        process_thread(thread_id, run.id)


def retrieve_thread(thread_id):
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

    print ("=== Received messages from AI ===\n")
    print (messages)
    print("\n")

    for message in messages:
        if message.role == "assistant":
            for attachment in message.attachments:
                save_file(attachment.file_id, attachment.file_id)

            for block in message.content:
                if block.type == "text":
                    print ("=== Received a message from AI ===")
                    print (block.text.value)
                    print ("\n\n")

                    if block.text.annotations:
                        for annotation in block.text.annotations:
                            if annotation.type == "file_path":
                                file_name = os.path.basename(annotation.text)

                                if file_name.endswith(".zip"):
                                    save_file(annotation.file_path.file_id, os.path.basename(CARBON_PROJECT_FILENAME))
                                elif file_name.endswith(".json"):
                                    save_file(annotation.file_path.file_id, os.path.basename(CARBON_META_FILENAME))
                                else:
                                    save_file(annotation.file_path.file_id, file_name)

def save_file(file_id: str, filename: str) -> str:
    print (f"=== Saving the file {file_id} ===")

    try:
        file_path = os.path.join(CARBON_WORK_DIR, filename)
        file_content = ai_client.files.content(file_id=file_id)
        file_data_bytes = file_content.read()

        with open(file_path, "wb") as file:
            file.write(file_data_bytes)
            file.close

        print(f"The file has been saved successfully.")
        print ("\n")

        return file_path

    except Exception as e:
        print(f"Could not save the file: {e}.")
        print ("\n")

        return None 
