#!/usr/bin/env python3

"""
tasks1: A simple prototype command-line task manager.

Features:
- Stores tasks in 'tasks.json'
- Adds tasks
- Lists all tasks
- Searches tasks
"""

import sys
import json
from typing import List, Dict, Any

# The file where tasks will be stored
DATA_FILE = "tasks.json"

# --- Data Handling Functions ---

def load_tasks() -> List[Dict[str, Any]]:
    """
    Loads tasks from the DATA_FILE.
    Returns an empty list if the file doesn't exist or is empty.
    """
    try:
        with open(DATA_FILE, 'r') as f:
            tasks = json.load(f)
            return tasks if isinstance(tasks, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Warning: '{DATA_FILE}' contains invalid JSON. Starting with an empty list.")
        return []

def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    """Saves the given list of tasks to the DATA_FILE."""
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

# --- Core Feature Functions ---

def add_task(tasks: List[Dict[str, Any]], description: str) -> None:
    """Adds a new task to the list and prints a confirmation."""
    new_id = max([task.get('id', 0) for task in tasks] + [0]) + 1
    new_task = {
        "id": new_id,
        "description": description,
        "status": "pending"
    }
    tasks.append(new_task)
    print(f'Added task {new_id}: "{description}"')

def list_tasks(tasks: List[Dict[str, Any]]) -> None:
    """Prints all tasks in a formatted list."""
    if not tasks:
        print("No tasks found.")
        return
    print("--- Task List ---")
    for task in tasks:
        print(f"  [{task.get('id', 'N/A')}] {task.get('description', 'No description')} ({task.get('status', 'unknown')})")
    print("-----------------")

def search_tasks(tasks: List[Dict[str, Any]], search_term: str) -> None:
    """Searches for tasks containing the search term (case-insensitive) and lists them."""
    found_tasks = [
        task for task in tasks
        if search_term.lower() in task.get('description', '').lower()
    ]
    if not found_tasks:
        print(f'No tasks found matching "{search_term}".')
        return
    print(f'--- Search Results for "{search_term}" ---')
    for task in found_tasks:
        print(f"  [{task.get('id', 'N/A')}] {task.get('description', 'No description')} ({task.get('status', 'unknown')})")
    print("-----------------")

def print_help() -> None:
    """Prints the help message showing valid commands."""
    print("\nUsage: python tasks.py [command] [arguments]")
    print("\nCommands:")
    print("  add [description]  - Adds a new task")
    print("  list               - Lists all tasks")
    print("  search [term]      - Searches for tasks containing [term]")
    print("  help               - Shows this help message\n")

# --- Main Execution ---

def main():
    """Main entry point for the CLI application."""
    args = sys.argv[1:]
    all_tasks = load_tasks()

    if not args:
        print("No command provided.")
        print_help()
        return

    command = args[0]

    if command == "add":
        if len(args) < 2:
            print("Error: No description provided for 'add' command.")
            print_help()
        else:
            description = " ".join(args[1:])
            add_task(all_tasks, description)
            save_tasks(all_tasks)
    elif command == "list":
        list_tasks(all_tasks)
    elif command == "search":
        if len(args) < 2:
            print("Error: No search term provided for 'search' command.")
            print_help()
        else:
            search_term = " ".join(args[1:])
            search_tasks(all_tasks, search_term)
    elif command == "help":
        print_help()
    else:
        print(f'Error: Unknown command "{command}"')
        print_help()

if __name__ == "__main__":
    main()
