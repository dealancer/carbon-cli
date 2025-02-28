import sys
from config import *
from ai import *

def main():
    if len(sys.argv) < 3:
        raise ValueError("No command or object provided. Please provide a command and an object.")

    command = sys.argv[1]
    object = sys.argv[2]

    if command == "create" and object == "issue":
        validate_vars([
            "CARBON_PROJECT_FILENAME",
            "CARBON_REQUEST",
            "CARBON_ISSUE_ID",
        ])
        create_thread_for_issue()

    elif command == "map" and object == "pr":
        validate_vars([
            "CARBON_ISSUE_ID",
            "CARBON_PR_ID",
        ])
        map_thread_to_pr_out_of_issue()

    elif command == "update" and object == "issue":
        validate_vars([
            "CARBON_ISSUE_ID",
            "CARBON_REQUEST",
        ])
        update_thread_for_issue()

    elif command == "update" and object == "pr":
        validate_vars([
            "CARBON_PR_ID",
            "CARBON_REQUEST",
        ])
        update_thread_for_pr()

    elif command == "retrieve" and object == "issue":
        validate_vars([
            "CARBON_ISSUE_ID",
        ])
        get_thread_by_issue()

    elif command == "retrieve" and object == "pr":
        validate_vars([
            "CARBON_PR_ID",
        ])
        get_thread_by_pr()

    elif command == "delete" and object == "issue":
        validate_vars([
            "CARBON_ISSUE_ID",
        ])
        delete_thread_for_issue()

    elif command == "delete" and object == "pr":
        validate_vars([
            "CARBON_PR_ID",
        ])
        delete_thread_for_pr()

    else:
        raise ValueError(f"Invalid command '{command}' or object '{object}' provided.")
    
if __name__ == "__main__":
    main()
