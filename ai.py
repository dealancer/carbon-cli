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
    with open(CARBON_FILENAME, 'rb') as file:
        file_object = ai_client.files.create(
            file=(CARBON_FILENAME, file),
            purpose="assistants"
        )
    return file_object.id

def create_thread_for_issue():
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

    config = get_config()
    if not "threads_by_issue" in config:
        config["threads_by_issue"] = {}

    config["threads_by_issue"][CARBON_ISSUE_ID] = thread.id
    save_config(config)


def map_thread_to_pr_out_of_issue():
    config = get_config()
    if not "threads_by_pr" in config:
        config["threads_by_pr"] = {}

    config["threads_by_pr"][CARBON_PR_ID] = config["threads_by_issue"][CARBON_ISSUE_ID]
    save_config(config)


def update_thread_for_pr():
    config = get_config()

    ai_client.beta.threads.update(
        config["threads_by_pr"][CARBON_PR_ID],
        messages=[
            {
                "role": "user",
                "content": CARBON_REQUEST
            }
        ]
    )
