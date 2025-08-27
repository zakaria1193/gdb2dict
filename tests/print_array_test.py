import json
import os
import sys

# Add current directory to Python path for gdb_init
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gdb
from gdb_init import init, test_function_wrapper

import gdb2dict


class ArrayTest(gdb.Breakpoint):
    def stop(self):
        print("💥 Array test breakpoint hit at address: " + (self.location))
        
        # Test Shape struct which has char stringValue[20] in the data union
        shape_value = gdb.parse_and_eval("shape_")
        
        print("🧪 Testing array indexing fix")
        result = gdb2dict.gdb_value_to_dict(shape_value)
        
        # Check that stringValue array has correct number of elements
        string_array = result['data##union']['stringValue##array']
        
        # Before fix: would have 19 elements 
        # After fix: should have 20 elements
        assert len(string_array) == 20, f"Expected 20 elements but got {len(string_array)}"
        
        print(f"✅ Array has correct size: {len(string_array)} elements")
        
        test_function_wrapper(gdb2dict.gdb_value_to_dict,
                              function_args=(shape_value, ),
                              test_name_suffix="array_test")
        return False


# Initialize the GDB Python script  
ArrayTest("printStructure")
init()