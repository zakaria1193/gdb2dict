"""
C++ coverage: plain classes, inheritance, static members and polymorphism.

Every breakpoint receives a pointer, which gdb_value_to_dict dereferences
on its own, resolving the dynamic type on the way.
"""

import gdb
from gdb_init import init, test_function_wrapper

import gdb2dict


class PrintOnBreakpoint(gdb.Breakpoint):
    """
    Dumps the pointer argument `obj` when the breakpoint is hit.
    """

    def __init__(self, location, test_name_suffix, unstable_keys=(),
                 **dump_kwargs):
        super().__init__(location)
        self.test_name_suffix = test_name_suffix
        self.unstable_keys = unstable_keys
        self.dump_kwargs = dump_kwargs

    def stop(self):
        print("💥 Breakpoint hit at: " + self.location)

        value = gdb.parse_and_eval("obj")
        print("👁️GDB value grabbed from executable: " + str(value))

        test_function_wrapper(gdb2dict.gdb_value_to_dict,
                              function_args=(value,),
                              function_kwargs=self.dump_kwargs,
                              test_name_suffix=self.test_name_suffix,
                              unstable_keys=self.unstable_keys)

        return False


# A plain class: primitives, char array, C enum and scoped enum
PrintOnBreakpoint("printBasicClass", "cpp_basic_class")

# Inheritance: base subobject, static members, and a derived member that
# hides a base member of the same name
PrintOnBreakpoint("printDerived", "cpp_derived_class")

# Polymorphism: the argument is a Base*, the object is a MostDerived
PrintOnBreakpoint("printBasePtr", "cpp_base_ptr_to_derived")

# Aggregates: nested objects, arrays of objects, references, and pointers
# left as addresses (the default)
PrintOnBreakpoint("printContainer", "cpp_container",
                  unstable_keys=("base_ptr_to_derived", "node_ptr"))

# Same object with pointer following enabled: exercises cycle detection,
# null pointers and dynamic type resolution behind a pointer member
PrintOnBreakpoint("printContainer", "cpp_container_follow_pointers",
                  follow_pointers=True)

init()
