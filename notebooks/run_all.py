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
        print(f"\n{'='*50}")
        print(message)
        print(f"{'='*50}")
        
        script_path = str(folder / script_name)
        
        try:
            # We remove capture_output so you see the prints live in the terminal
            subprocess.run([python_path, script_path], check=True)
            print(f"\n✅ {script_name} completed successfully!")
            
        except subprocess.CalledProcessError:
            print(f"\n❌ ERROR: {script_name} failed.")
            print("Check the traceback above to see exactly why it crashed.")
            sys.exit(1)

    print(f"\n{'*'*50}")
    print("ALL TASKS COMPLETED SUCCESSFULLY!")
    print(f"{'*'*50}")

if __name__ == "__main__":
    run_scripts()