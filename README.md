[![Build](https://github.com/zakaria1193/gdb2dict/actions/workflows/release.yml/badge.svg)](https://github.com/zakaria1193/gdb2dict/actions/workflows/release.yml)
[![Tests](https://github.com/zakaria1193/gdb2dict/actions/workflows/test.yml/badge.svg)](https://github.com/zakaria1193/gdb2dict/actions/workflows/test.yml)

# GDB.value to python dict converter

This tool extends GDB python scripting capabilities.

gdb (GNU Debugger) use a specific format to print C/C++ programs data, this format is not easy to parse, so this tool converts the output of gdb to python dictionaries.

So it can also be used to serialize C data structures to JSON objects, or to any other format.

Example of conversion:

If you have a structure like this in you C code:

```c
struct Shape {
    int id;
    enum {
        RED,
        GREEN,
        BLUE
    } color;
    union {
        int intValue;
        float floatValue;
    }; // unnamed union (C11)
    struct {
        int x;
        int y;
    } center;
    union {
        int intValue;
        float floatValue;
    } data;
};
```

When you print an instance of this struct in python gdb script (or in the classic gdb console),
both will give this printable string that is not a native python object

```gdb
(gdb) p my_struct
OR
(gdb) python print(gdb.parse_and_eval("my_struct"))
{
  id = 0x1,
  color = RED,
  {
    intValue = 0x2a,
    floatValue = 5.88545355e-44
  },
  center = {
    x = 0x1e,
    y = 0x28
  },
  data = {
    intValue = 0x6c6c6548,
    floatValue = 1.14313912e+27,
  }
}
```

gdb2dict lets convert the output of gdb to a python dictionary.

```python
import gdb2dict
```

Simply call the function `gdb_value_to_dict` with the value to convert,
and it will return a python dictionary.

```python
> output_dict = gdb2dict.gdb_value_to_dict(gdb.parse_and_eval("my_struct"))

output_dict =
{
    'id': '0x1',
    'color': 'RED',
    '##unnamed_field_1##union':
    {
        'floatValue': '5.88545355e-44',
        'intValue': '0x2a'
    },
    'center##struct': {'x': '0x1e', 'y': '0x28'},
    'data##union':
    {
        'floatValue': '1.14313912e+27',
        'intValue': '0x6c6c6548'
    },
}

```

### Metatada

As you can see some field names (keys after conversion) have added metadata `##struct`, `##union`
That's needed to differentiate between fields that are structs and fields that are unions.

Another metadata can be added to the keys, it's `##unnamed_field_1##struct`,
`##unnamed_field_2##union` etc...

That's to cover for [ C11's unnanmed fields ](https://gcc.gnu.org/onlinedocs/gcc/Unnamed-Fields.html)
that can be sub-structs or sub-unions without a name.

## Use cases

Imagine you are trying to automatize the debugging of a measuring, and you want to parse the output of a measure function that returns a structure, you can use this tool to convert the output of gdb to a JSON format,
you can do that manually by reading field by and field and making your own python dictionary, but this tool does that for you.

It comes handy when you have a lot of structures and unions to parse, and you don't want to write a lot of code to parse them, since gdb already knows how to parse them.

The printer can be used in your custom breakpoints, or your custom commands, or in your custom pretty printers.

If you don't know how to make those, refer to the [GDB documentation](https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html#Python-API).

Or this article from [Memfault](https://interrupt.memfault.com/blog/automate-debugging-with-gdb-python-api)

## Usage example: Parse TLV data from breakpoint and write to file

Let's use it in a python scripted gdb breakpoint handler.
The idea is catch the functions that identifies the TLV type and value,
then cast to a structure and write to a file in JSON format.

```python my_script.py

import gdb2dict

OUTPUT_LIST = []

class MyCustomBreakpoint(gdb.Breakpoint):
    def stop(self):
        # Access arguments
        arg1_payload = gdb.parse_and_eval("arg1_payload")
        arg2_payload_type = gdb.parse_and_eval("arg2_paytload_type")
        arg3_payload_size = gdb.parse_and_eval("arg3_payload_size") # Not needed here

        # Convert the payload type to a structure using some custom mapping function
        type_to_cast = my_custom_payload_type_to_struct(arg2_payload_type)

        # Cast to a structure pointer
        arg1_payload = arg1_payload.cast(type_to_cast)

        OUTPUT_LIST.append(gdb2dict.gdb_value_to_dict(arg1_payload))

        # Return False to not halt (Automatically continue)
        return False

with open("output.json", "w") as f:
    f.write("{\"output\": [\n")
    f.write(",\n".join(OUTPUT_LIST))
    f.write("]}")

```

Source this script in gdb will set the breakpoint and fill the output file with the parsed values.

```bash
$ gdb -x my_script.py --batch --nw --nx --return-child-result
```

`--batch --nw --nx --return-child-result` are recommended for automated gdb scripting,
see `gdb --help` for more information.

Then you can post process the output file with your favorite language.
