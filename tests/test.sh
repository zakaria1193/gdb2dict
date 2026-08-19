#!/bin/bash
# Shell

SCRIPT_DIR=$(cd "$(dirname $0)"; pwd)

# Export to python path
export PYTHONPATH=$SCRIPT_DIR:$PYTHONPATH

MODE=$1

# Mode can be either "test" or "save_output"

# Export expected output dir that holds the expected output files
export EXPECTED_OUTPUT_DIR=$SCRIPT_DIR/expected_output

if [ "$MODE" = "test" ]; then
    # Run program with gdb
    echo "Running program in test mode"
elif [ "$MODE" = "save_output" ]; then
    # Run program with gdb
    export SAVE_TEST_RESULTS=1
    mkdir -p "$EXPECTED_OUTPUT_DIR"
    rm -f "$EXPECTED_OUTPUT_DIR"/*
    echo "Running program with gdb in order to save output to $EXPECTED_OUTPUT_DIR as reference"
else
    echo "Invalid mode, please use either 'test' or 'save_output'"
    exit 1
fi

pushd "$SCRIPT_DIR" || exit 1

# Compile
make -C c_project
make -C cpp_project

function run_test_program_with_gdb_script() {
  test_program=$1
  gdb_script=$2
  # Run program with gdb
  # The added options are recommended for automated GDB testing, without using user's .gdbinit
  gdb "$test_program" -x "$gdb_script" --batch --nx --nw --return-child-result
}

C_TEST_SCRIPTS=(
  ./print_after_cast.py
  ./print_without_cast.py
)

CPP_TEST_SCRIPTS=(
  ./print_cpp_objects.py
  ./print_cpp_std_string.py
)

for gdb_script in "${C_TEST_SCRIPTS[@]}"; do
  echo "Running C test $gdb_script"
  run_test_program_with_gdb_script c_project/test_program "$gdb_script" || exit 1
done

for gdb_script in "${CPP_TEST_SCRIPTS[@]}"; do
  echo "Running C++ test $gdb_script"
  run_test_program_with_gdb_script cpp_project/test_program_cpp "$gdb_script" || exit 1
done


popd || exit 1
