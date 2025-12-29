import subprocess
import sys
from pathlib import Path

def run_scripts():
    folder = Path(__file__).parent
    python_path = sys.executable
    print("Step 1: Cleaning and Merging Data...")
    subprocess.run([python_path, str(folder / "qb_cleaning.py")], check=True)
    print("\nStep 2: Calculating QB Grades...")
    subprocess.run([python_path, str(folder / "qb_grading.py")], check=True)
    print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    run_scripts()