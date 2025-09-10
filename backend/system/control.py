import os

def run_system_command(command):
    try:
        os.system(command)
        return f"Executed: {command}"
    except Exception as e:
        return f"Error: {e}"
