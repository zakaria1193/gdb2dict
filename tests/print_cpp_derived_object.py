import gdb
import json
import sys

# Assuming gdb_init.py adds src to the path
from gdb2dict import gdb_value_to_dict

# GDB setup commands
gdb.execute("set confirm off")
gdb.execute("set width 0")
gdb.execute("set height 0")
gdb.execute("set verbose off")

# Set a breakpoint
gdb.Breakpoint("inspectDerivedObject", temporary=True)

# Run the program
gdb.execute("run")

# Check if the program has exited
if gdb.selected_inferior().pid == 0:
    print("Program did not run or breakpoint not hit.")
    gdb.execute("quit 1")

try:
    # Get the frame where the breakpoint was hit
    frame = gdb.selected_frame()
    if frame is None:
        print("Error: Could not get selected frame. Breakpoint might not have been hit.")
        gdb.execute("quit 1")

    # Get the 'obj' argument from the frame
    derived_obj_ptr = frame.read_var("obj")

    if derived_obj_ptr is None:
        print("Error: Could not read variable 'obj'.")
        gdb.execute("quit 1")

    # Convert the gdb.Value to a dictionary
    result_dict = gdb_value_to_dict(derived_obj_ptr)

    # Print the dictionary as a JSON string
    print(json.dumps(result_dict, indent=4, sort_keys=True))

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
    gdb.execute("quit 1")

# Quit GDB
gdb.execute("quit")
