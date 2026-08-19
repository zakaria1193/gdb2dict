#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variables
TEST_PROGRAM_DIR="tests/cpp_project"
TEST_PROGRAM_NAME="test_program_cpp"
TEST_PROGRAM_PATH="${TEST_PROGRAM_DIR}/${TEST_PROGRAM_NAME}"
EXPECTED_OUTPUT_DIR="tests/expected_output/cpp"
GDB_INIT_SCRIPT="tests/gdb_init.py" # gdb_init.py is used by the individual test scripts now.

# Compile the C++ test program
echo "Compiling C++ test program..."
make -C ${TEST_PROGRAM_DIR} clean
make -C ${TEST_PROGRAM_DIR}
echo "Compilation finished."
echo ""

# Counter for failed tests
failed_tests=0
total_tests=0

# Function to run a single test case
run_test() {
    local test_script_name=$1
    local expected_json_name=$2
    local test_description=$3
    local gdb_test_script="tests/${test_script_name}.py"
    local expected_output_file="${EXPECTED_OUTPUT_DIR}/${expected_json_name}.json"
    local actual_output_file="actual_${expected_json_name}.json"

    total_tests=$((total_tests + 1))
    echo "Running test: ${test_description}"
    echo "  GDB Script: ${gdb_test_script}"
    echo "  Expected JSON: ${expected_output_file}"

    # Run GDB with the Python script and capture output
    # Ensure that gdb_init.py is sourced by the test script itself to set up Python paths
    # The test scripts (e.g. print_cpp_basic_object.py) will call gdb.execute("run") and gdb.execute("quit")
    if gdb -batch \
           -ex "source ${GDB_INIT_SCRIPT}" \
           -ex "py import sys; print(sys.path)" \
           -x "${gdb_test_script}" \
           --args "${TEST_PROGRAM_PATH}" > "${actual_output_file}" 2>&1; then
        # GDB executed successfully, now compare the output
        # The Python scripts print JSON to stdout.
        # Need to clean up GDB messages if any (e.g., "Reading symbols from...")
        # However, the Python scripts are designed to print only JSON.
        # Let's assume the output file contains only the JSON.

        # Compare the actual output with the expected output
        if diff -q "${actual_output_file}" "${expected_output_file}"; then
            echo -e "${GREEN}PASS${NC}: ${test_description}"
        else
            echo -e "${RED}FAIL${NC}: ${test_description}. Output differs."
            echo "To see the difference, run: diff \"${actual_output_file}\" \"${expected_output_file}\""
            failed_tests=$((failed_tests + 1))
        fi
    else
        echo -e "${RED}FAIL${NC}: ${test_description}. GDB execution failed."
        echo "GDB output/error was:"
        cat "${actual_output_file}" # Show GDB's output/error
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
}

# Define C++ test cases
# Format: run_test "gdb_script_name_no_extension" "expected_json_name_no_extension" "Description"
run_test "print_cpp_basic_object" "gdb_value_to_dict_cpp_basic_object" "Basic C++ Object (BasicClass)"
run_test "print_cpp_derived_object" "gdb_value_to_dict_cpp_derived_object" "Derived C++ Object (Derived)"
run_test "print_cpp_base_ptr_to_derived" "gdb_value_to_dict_cpp_base_ptr_to_derived" "Base Pointer to Derived Object (Polymorphism)"
run_test "print_cpp_container_object" "gdb_value_to_dict_cpp_container_object" "Complex C++ Container Object"

# Summary
echo "--------------------"
echo "C++ Test Summary:"
if [ ${failed_tests} -eq 0 ]; then
    echo -e "${GREEN}All ${total_tests} tests passed!${NC}"
    exit 0
else
    echo -e "${RED}${failed_tests} out of ${total_tests} tests failed.${NC}"
    exit 1
fi
