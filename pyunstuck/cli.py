"""
PyUnstuck - Python Script Debugging and Interruption Tool
A debugging tool that helps you analyze and terminate frozen Python scripts.

@Version: 1.0.0
@Platform: Windows (primary) / Linux / MacOS
@Python: >= 3.11
"""

import sys
import threading
import runpy
import time
import ctypes
import sys
import os

def ask_script_path():
    """
    Get the target script path from user input and return absolute path
    """
    script_path = input("Enter the script path to monitor: ").strip()
    if not script_path:
        print("Script path cannot be empty!")
        sys.exit(1)
    
    # Convert to absolute path
    script_path = os.path.abspath(script_path)
    if not os.path.exists(script_path):
        print(f"Script path does not exist: {script_path}")
        sys.exit(1)
    return script_path

def setup_script_environment(script_path):
    """
    Setup script runtime environment
    - Add script directory to Python path
    - Change working directory to script directory
    """
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(script_path))
    
    # Add to Python path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Change working directory
    original_dir = os.getcwd()
    os.chdir(script_dir)
    
    return original_dir

def run_script_in_thread(script_path):
    """
    Execute target script in a new thread
    """
    original_dir = setup_script_environment(script_path)
    try:
        runpy.run_path(script_path, run_name="__main__")
    finally:
        # Restore original working directory
        os.chdir(original_dir)

def get_file_context(filename, lineno, context_lines=2):
    """
    Get code context around specified line number
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        start = max(0, lineno - context_lines - 1)
        end = min(len(lines), lineno + context_lines)
        
        context = []
        for i in range(start, end):
            line_num = i + 1
            prefix = '  > ' if line_num == lineno else '    '
            if line_num == lineno:
                context.append(f"\033[1;90m{prefix}{line_num:4d}|\033[0m \033[48;2;100;181;246m\033[38;2;227;242;253m{lines[i].rstrip()}\033[0m")
            else:
                context.append(f"\033[1;90m{prefix}{line_num:4d}|\033[0m {lines[i].rstrip()}")
        return '\n'.join(context)
    except:
        return None

def print_stack(thread_id):
    """
    Print call stack of specified thread (accurate to line number),
    using Rust compiler-like format, and show source code context
    """
    frames_map = sys._current_frames()
    if thread_id not in frames_map:
        print("\033[1;31merror\033[0m: Thread stack not found, thread may have exited.")
        return

    stack = frames_map[thread_id]
    print("\n\033[1;34m╔═══ Stack Trace Captured (thread_id = {}) ═══╗\033[0m".format(thread_id))
    frame_count = 0
    
    while stack:
        frame = stack
        code = frame.f_code
        lineno = frame.f_lineno
        filename = code.co_filename
        funcname = code.co_name
        
        # Add frame number and arrow indicator
        frame_prefix = f"\033[1;36m{frame_count:>2}\033[0m: "
        location = f"\033[1;33m{filename}:{lineno}\033[0m"
        func_info = f"\033[1;32m{funcname}\033[0m"
        
        print(f"\n{frame_prefix}at {location}")
        print(f"     \033[1;90m└─\033[0m in {func_info}")
        
        # Show local variables
        if frame.f_locals:
            print("     \033[1;90m└─\033[0m Local Variables:")
            for key, value in frame.f_locals.items():
                if not key.startswith('__'):
                    try:
                        val_str = str(value)
                        if len(val_str) > 50:  # Truncate long values
                            val_str = val_str[:47] + "..."
                        print(f"       \033[1;90m|\033[0m \033[1;35m{key}\033[0m = {val_str}")
                    except:
                        print(f"       \033[1;90m|\033[0m \033[1;35m{key}\033[0m = <unable to display>")
        
        # Show source code context
        if os.path.exists(filename) and filename.endswith('.py'):
            print("     \033[1;90m└─\033[0m Source Context:")
            context = get_file_context(filename, lineno)
            if context:
                print("       \033[1;90m|\033[0m")
                for line in context.split('\n'):
                    print(f"       \033[1;90m|\033[0m {line}")
                print("       \033[1;90m|\033[0m")
        
        frame_count += 1
        stack = stack.f_back
    
    print("\033[1;34m╚════════════════════════════════════╝\033[0m\n")

def kill_thread(thread, exc_type=SystemExit):
    """
    Force terminate target thread by raising specified exception using ctypes.
    exc_type can be SystemExit, KeyboardInterrupt, etc.
    """
    tid = threading.get_native_id()  # Changed to no parameters
    if not tid:
        print("Unable to get thread ID, this Python version may not support threading.get_native_id().")
        return

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_ulong(tid),
        ctypes.py_object(exc_type)
    )
    if res == 0:
        print("Force termination failed: Thread ID not found.")
    elif res > 1:
        # If return value > 1, something went wrong, need to call again to recover
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(tid), None)
        print("Force termination error: Multiple threads affected, recovered.")

def main():
    script_path = ask_script_path()

    # Start target script in child thread
    worker = threading.Thread(target=run_script_in_thread, args=(script_path,))
    worker.daemon = True  # Ensure child thread exits when main program exits
    worker.start()
    print(f"\033[1;34m[INFO]\033[0m Script started in child thread (thread_id = {worker.ident}), press Ctrl+C to interrupt.")

    try:
        while worker.is_alive():
            time.sleep(1)  # Keep main thread waiting
    except KeyboardInterrupt:
        # After catching Ctrl+C, start force debug/terminate logic
        print("\n\033[1;33m[WARN]\033[0m Ctrl+C detected, attempting to get target script's stack info...")
        # Print child thread stack first
        print_stack(worker.ident)

        print("\033[1;31m[ALERT]\033[0m About to force terminate child thread running target script...")
        kill_thread(worker)

        # Wait for child thread to fully exit
        worker.join(timeout=2)
        if worker.is_alive():
            print("\033[1;31m[ERROR]\033[0m Child thread failed to exit.")
        else:
            print("\033[1;32m[SUCCESS]\033[0m Child thread has exited.")

        input("\nPress Enter to exit program...")

    print("\033[1;34m[INFO]\033[0m Main script ended.")

if __name__ == "__main__":
    main()
