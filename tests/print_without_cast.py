import json
import os

import gdb
from gdb_init import init, test_function_wrapper

import gdb2json


class CustomBreakpointNoCast(gdb.Breakpoint):
    def stop(self):
        print("💥 Breakpoint hit at address: " +(self.location))
        value = gdb.parse_and_eval("*point")

        # Check that the type is correct
        assert str(value.type) == "struct Point"

        test_function_wrapper(gdb2json.gdb_value_to_dict,
                              function_args=(value, ),
                              test_name_suffix="no_cast")
        return False


# Initialize the GDB Python script
CustomBreakpointNoCast("printPoint")
init()
