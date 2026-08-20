import json
import os
from pprint import pprint
from typing import Callable

import gdb


def init():
    """
    Init gdb using common config
    """

    # Config gdb pytrhon full stack trace
    gdb.execute("set python print-stack full")

    # Pretty print
    gdb.execute("set print pretty on")

    # Print in hex
    gdb.execute("set output-radix 16")

    # Paging off
    gdb.execute("set pagination off")

    print("🏁 GDB script initialized")

    # Run the executable
    gdb.execute("run")

    # Exit GDB
    gdb.execute("quit")


def mask_unstable_values(obj, unstable_keys):
    """
    Replace the values of the named keys with a placeholder.

    Addresses move between runs (ASLR, loader layout), so a test that dumps
    a pointer has to say so explicitly. Masking is driven by an explicit key
    list rather than by guessing from the text of a value: a union member or
    an int can look exactly like an address, and silently rewriting those
    would make the fixtures stop checking the data.
    """

    if not unstable_keys:
        return obj

    if isinstance(obj, dict):
        return {key: ("0xADDR" if key in unstable_keys
                      else mask_unstable_values(value, unstable_keys))
                for key, value in obj.items()}

    if isinstance(obj, list):
        return [mask_unstable_values(value, unstable_keys) for value in obj]

    return obj


def save_as_expected_test_result(name: str,
                                 obj: [dict, list]):
    """
    Save the result of a script run to a file
    """

    if not os.environ.get("SAVE_TEST_RESULTS"):
        return

    try:
        output_dir = os.environ.get("EXPECTED_OUTPUT_DIR")
    except KeyError:
        print("❌ Expected output dir not set")
        return

    if not name:
        print("❌ Test name not set, writing test result failed")
        return

    output_path = os.path.join(output_dir, name + ".json")

    print("💾 Saving test results under {} as reference".format(output_path))

    if type(obj) is list:
        output = {"gdb2dict_output_list": None}
        output["gdb2dict_output_list"] = obj
    elif type(obj) is dict:
        output = obj

    with open(output_path, "w") as file_handle:
        json.dump(output, file_handle, indent=4)


def process_test_result(name: str,
                        output_dict: dict):
    """
    Process the result of a script run

    Either compare to the expected result or save the result as the
    expected result
    """

    if not os.environ.get("EXPECTED_OUTPUT_DIR"):
        raise Exception("❌ Expected output dir not set")

    if os.environ.get("SAVE_TEST_RESULTS"):
        save_as_expected_test_result(name, output_dict)
        return

    test_result_path = os.path.join(os.environ.get("EXPECTED_OUTPUT_DIR"),
                                    name + ".json")
    print("🔍 Loading test result from {}".format(test_result_path))

    with open(test_result_path, "r") as file_handle:
        expected_result = json.load(file_handle)

    try:
        if type(output_dict) is dict:
            assert output_dict == expected_result

        else:
            raise Exception("Unexpected type: {}".format(type(output_dict)))

    except AssertionError as e:
        print("❌ Test failed: " + name)
        print("Expected: " + str(expected_result))
        print("Got: " + str(output_dict))
        raise Exception("Test failed: " + name + " because " + str(e))
    else:
        print("✅ Test passed: " + name)


def non_gdb_args_only(function_args):
    non_gdb_args = []

    for arg in function_args:
        if not isinstance(arg, gdb.Value):
            non_gdb_args.append(arg)

    return non_gdb_args


def test_function_wrapper(function: Callable,
                          function_args: tuple,
                          test_name_suffix: str,
                          function_kwargs: dict = None,
                          unstable_keys: tuple = ()):
    """
    Wrapper for test functions

    :param unstable_keys: names of keys whose value is an address and can
                          therefore not be compared between runs
    """

    print("🔍 Testing function: " + function.__name__)

    if function_kwargs is None:
        function_kwargs = {}

    # Run the test function
    output = mask_unstable_values(function(*function_args,
                                           **function_kwargs),
                                  unstable_keys)

    print("⏩Output: ")
    pprint(output)

    process_test_result(function.__name__ + '_' + test_name_suffix,
                        output)
