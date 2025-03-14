from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    print("Hello from openai-agents-sdk!")


if __name__ == "__main__":
    main()
