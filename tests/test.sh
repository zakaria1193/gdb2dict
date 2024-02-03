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

function run_test_program_with_gdb_script() {
  gdb_script=$1
  # Run program with gdb
  # The added options are recommended for automated GDB testing, without using user's .gdbinit
  gdb c_project/test_program -x "$gdb_script" --batch --nx --nw --return-child-result
}

GDB_TEST_SCRIPTS=(
  ./print_after_cast.py
  ./print_without_cast.py
)

for gdb_script in "${GDB_TEST_SCRIPTS[@]}"; do
  echo "Running test $gdb_script"
  run_test_program_with_gdb_script "$gdb_script" || exit 1
done


popd || exit 1
