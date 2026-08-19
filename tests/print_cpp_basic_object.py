import gdb
import json
import sys

# Assuming gdb_init.py adds src to the path
# If not, uncomment and adjust:
# sys.path.insert(0, '/app/src')
from gdb2dict import gdb_value_to_dict

# GDB setup commands
gdb.execute("set confirm off")
gdb.execute("set width 0")
gdb.execute("set height 0")
gdb.execute("set verbose off")

# Set a breakpoint
gdb.Breakpoint("inspectBasicObject", temporary=True)

# Run the program
# Arguments to "run" are passed to the program being debugged.
# test_program_cpp does not expect any arguments.
gdb.execute("run")

# Check if the program has exited (e.g. breakpoint not hit)
if gdb.selected_inferior().pid == 0:
    print("Program did not run or breakpoint not hit.")
    gdb.execute("quit 1") # Exit GDB with an error code

try:
    # Get the frame where the breakpoint was hit
    frame = gdb.selected_frame()
    if frame is None:
        print("Error: Could not get selected frame. Breakpoint might not have been hit.")
        gdb.execute("quit 1")

    # Get the 'obj' argument from the frame
    # Note: GDB's frame.read_var() gets the gdb.Value representation of the variable.
    # For a pointer 'BasicClass* obj', this will be a gdb.Value of type pointer.
    # gdb_value_to_dict expects the object itself, or a pointer it can dereference.
    basic_obj_ptr = frame.read_var("obj")

    if basic_obj_ptr is None:
        print("Error: Could not read variable 'obj'.")
        gdb.execute("quit 1")

    # Convert the gdb.Value to a dictionary
    # gdb_value_to_dict will handle dereferencing if basic_obj_ptr is a pointer
    result_dict = gdb_value_to_dict(basic_obj_ptr)

    # Print the dictionary as a JSON string
    print(json.dumps(result_dict, indent=4, sort_keys=True))

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
    gdb.execute("quit 1") # Exit GDB with an error code

# Quit GDB
gdb.execute("quit")
