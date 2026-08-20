"""
Smoke test for a class holding a std::string.

The layout of std::string belongs to the standard library, so the dump is
checked structurally rather than compared against a stored fixture, which
would break on a different libstdc++.
"""

import gdb
from gdb_init import init

import gdb2dict


class CheckStdString(gdb.Breakpoint):

    def stop(self):
        print("💥 Breakpoint hit at: " + self.location)

        value = gdb.parse_and_eval("obj")
        output = gdb2dict.gdb_value_to_dict(value)

        print("⏩Output keys: " + str(sorted(output.keys())))

        assert output["id"] == hex(9), \
            "Expected id 0x9, got {}".format(output.get("id"))

        # std::string is a class, so it lands under the ##struct key and
        # must have been walked without blowing up
        assert "text##struct" in output, \
            "Expected a text##struct key, got {}".format(sorted(output))
        assert isinstance(output["text##struct"], dict), \
            "Expected text##struct to be a dict"
        assert output["text##struct"], \
            "Expected text##struct to have members"

        print("✅ Test passed: gdb_value_to_dict_cpp_std_string")

        return False


CheckStdString("printWithStdString")

init()
