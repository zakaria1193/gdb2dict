import enum
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

    print (output_dir, name)

    output_path = os.path.join(output_dir, name + ".json")

    print("💾 Saving test results under {} as reference".format(output_path))

    if type(obj) is list:
        output = {"gdb2json_output_list": None}
        output["gdb2json_output_list"] = obj
    elif type(obj) is dict:
        output = obj

    with open(output_path, "w") as file_handle:
        json.dump(output, file_handle, indent=4)


def process_test_result(name: str,
                        output_dict: dict):
    """
    Process the result of a script run

    Either compare to the expected result or save the result as the expected result
    """

    if not os.environ.get("EXPECTED_OUTPUT_DIR"):
        raise Exception("❌ Expected output dir not set")

    if os.environ.get("SAVE_TEST_RESULTS"):
        save_as_expected_test_result(name, output_dict)
        return

    test_result_path = os.path.join(os.environ.get("EXPECTED_OUTPUT_DIR"), name + ".json")
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
        raise Exception("Test failed: " + name + " because " + e)
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
                          test_name_suffix: str):
    """
    Wrapper for test functions
    """

    print("🔍 Testing function: " + function.__name__)

    # Run the test function
    output = function(*function_args)

    print("⏩Output: ")
    pprint(output)

    process_test_result(function.__name__ + '_' + test_name_suffix,
                        output)
