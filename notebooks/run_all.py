import subprocess
import sys
from pathlib import Path

def run_scripts():
    folder = Path(__file__).parent
    python_path = sys.executable
    
    scripts = [
        ("Step 1: Cleaning and Merging Data...", "qb_cleaning.py"),
        ("Step 2: Calculating QB Grades...", "qb_grading.py")
    ]

    for message, script_name in scripts:
        print(message)
        script_path = str(folder / script_name)
        
        try:
            # check=True: Raises an error if the script fails
            # capture_output=True: Grabs the error message text
            # text=True: Makes sure the output is a readable string, not bytes
            subprocess.run([python_path, script_path], check=True, capture_output=True, text=True)
            print(f"--- {script_name} completed successfully! ---\n")
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ ERROR in {script_name}:")
            # This 'e.stderr' is the key—it contains the actual Traceback/NaN error
            print("-" * 50)
            print(e.stderr) 
            print("-" * 50)
            print("Stopping execution due to error.")
            sys.exit(1) # Stop the rest of the scripts from running

if __name__ == "__main__":
    run_scripts()