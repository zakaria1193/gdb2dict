# GDB to JSON converter

This tool extends GDB python scripting capabilities.

Using gdb (GNU Debugger) use a specific format to print structures and unions, this format is not easy to parse, so this tool converts the output of gdb to a JSON format.

## Use cases

Imagine you are trying to automatize the debugging of a meauring, and you want to parse the output of a measure function that returns a structure, you can use this tool to convert the output of gdb to a JSON format,
you can do that manually by reading field by and field and making your own python dictionary, but this tool does that for you.

It comes handy when you have a lot of structures and unions to parse, and you don't want to write a lot of code to parse them, since gdb already knows how to parse them.

The printer can be used in your custom breakpoints, or your custom commands, or in your custom pretty printers.

If you don't know how to make those, refer to the [GDB documentation](https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html#Python-API).

Or this article from [Memfault](https://interrupt.memfault.com/blog/automate-debugging-with-gdb-python-api)

## Examples

### Simple example

```python my_script.py

import gdb2json

OUTPUT_DICT = {}

class MyCustomBreakpoint(gdb.Breakpoint):
    def stop(self):
        # Access arguments
        arg1 = gdb.parse_and_eval("arg1")

        # Convert to json
        gdb_value_json = {}
        gdb_value_to_json_obj(arg1, gdb_value_json)

        # Set in output dict
        OUTPUT_DICT[str(type_id)].append(gdb_value_json)

        # Return False to not halt (Automatically continue)
        return False


MyCustomBreakpoint("my_function")

# Run the program
gdb.execute("run")

# Write the output to a file
with open("output.json", "w") as f:
    json.dump(OUTPUT_DICT, f, indent=4)

```
Source this script in gdb will set the breakpoint and fill the output file with the parsed values.

```bash
$ gdb -x my_script.py
```

Then you can post process the output file with your favorite language.


## Example with cast

Cast any void pointer to a structure pointer, and print the structure is a powerful gdb feature
for parsing binary data. This tool makes it better by making the output as JSON.

```python my_script.py

import gdb2json

OUTPUT_DICT = {}

class MyCustomBreakpoint(gdb.Breakpoint):
    def stop(self):
        # Access arguments
        arg1 = gdb.parse_and_eval("arg1")

        # Cast to a structure pointer
        arg1 = arg1.cast("my_struct*"")

        arg1 = gdb.parse_and_eval("*arg1")

        # Convert to json
        gdb_value_json = {}
        gdb_value_to_json_obj(arg1, gdb_value_json)

        # Set in output dict
        OUTPUT_DICT[str(type_id)].append(gdb_value_json)

        # Return False to not halt (Automatically continue)
        return False

```





