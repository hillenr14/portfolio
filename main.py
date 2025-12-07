import sys
import os

# Ensure src is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("Portfolio Manager Initialized")
    print("To run the UI, use: streamlit run src/ui/app.py")
