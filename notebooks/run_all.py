import subprocess
import sys
from pathlib import Path

def run_scripts():
    # Get the path to this folder
    folder = Path(__file__).parent
    
    # sys.executable finds the path to YOUR python.exe or python3 binary
    python_path = sys.executable

    # 1. Run the cleaning script
    print("Step 1: Cleaning and Merging Data...")
    subprocess.run([python_path, str(folder / "qb_cleaning.py")], check=True)
    
    # 2. Run the grading script
    print("\nStep 2: Calculating QB Grades...")
    subprocess.run([python_path, str(folder / "qb_grading.py")], check=True)
    
    print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    run_scripts()