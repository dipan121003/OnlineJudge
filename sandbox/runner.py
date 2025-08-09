# In /sandbox/runner.py
import sys
import subprocess
from pathlib import Path

def main():
    try:
        # Read language, code, and input from the data piped into this script
        language = sys.stdin.readline().strip()
        code_and_input = sys.stdin.read()
        parts = code_and_input.split('---!!!INPUT_DELIMITER!!!---')
        code = parts[0]
        input_data = parts[1] if len(parts) > 1 else ''

        if language == "py":
            filename = "main.py"
        elif language == "cpp":
            filename = "main.cpp"
        elif language == "java":
            filename = "Main.java"
        else:
            print("Unsupported language.", file=sys.stderr)
            return

        Path(filename).write_text(code)

        if language == "py":
            command = ['python', filename]
        elif language == "cpp":
            compile_cmd = ['g++', filename, '-o', 'main']
            subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
            command = ['./main']
        elif language == "java":
            compile_cmd = ['javac', filename]
            subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
            command = ['java', 'Main']

        # Run the compiled/interpreted code
        result = subprocess.run(command, input=input_data, capture_output=True, text=True, timeout=10)

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

    except subprocess.CalledProcessError as e:
        print("Compilation Error:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("Execution Timed Out (10 seconds)", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()