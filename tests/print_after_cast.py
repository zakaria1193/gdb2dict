import gdb
from gdb_init import init, test_function_wrapper

import gdb2json

MAP_TYPE_ENUM_TO_TYPE = {
    "TYPE_STRUCT_POINT": "struct Point",
    "TYPE_STRUCT_SHAPE": "struct Shape",
    "TYPE_STRUCT_COMPLEX": "struct ComplexObject",
}


# Custom breakpoint stop implementation
class CustomBreakpointWithCast(gdb.Breakpoint):

    def stop(self):
        """
        Stop the program at the breakpoint and print the struct or union as dict/list
        """
        print("💥 Breakpoint hit at address: " + (self.location))

        # Get the type to cast the pointer to from the argument "type_enum"
        type_to_cast = gdb.parse_and_eval("type_enum")
        type_to_cast = str(type_to_cast)
        type_to_cast = MAP_TYPE_ENUM_TO_TYPE[type_to_cast]

        print(f"💫 Casting to type: {type_to_cast}")

        # Cast the pointer to a struct or union
        value = gdb.parse_and_eval(f"*({type_to_cast}*)ptr")
        print("👁️GDB value grabbed from executable: " + str(value))

        # Test appending to a list
        test_function_wrapper(gdb2json.gdb_value_to_dict,
                              function_args=(value,),
                              test_name_suffix='after_cast_to_' + type_to_cast)

        return False


# Initialize and run the script
CustomBreakpointWithCast("printStructure")
init()
