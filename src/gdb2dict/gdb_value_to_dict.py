import json

import gdb

DEBUG = False

if DEBUG:
    def print_debug(msg):
        print(msg)
else:
    def print_debug(msg):
        pass


OBJ_TYPE_NEEDS_RECURSIVE_CALL = [
    gdb.TYPE_CODE_STRUCT,
    gdb.TYPE_CODE_UNION,
    gdb.TYPE_CODE_ARRAY
]


def gdb_value_to_dict(gdb_value: gdb.Value):
    """
    Converts a gdb.Value to a json string

    :param gdb_value: gdb.Value -> Must be a struct or union
    :return: data: dict -> The data of the gdb.Value as a dict
    """

    data: dict = {}
    append_gdb_value_to_dict(gdb_value, data)
    return data


def gdb_value_primitive_to_str(gdb_value: gdb.Value):
    """
    Converts a primitive gdb.Value to a str or hex

    A primitive gdb.Value is a value that is not of the types listed in
    OBJ_TYPE_NEEDS_RECURSIVE_CALL (struct, union, array, etc...)

    :param gdb_value: gdb.Value to be converted
    :return: str or hex of the gdb.Value
    """

    print_debug("gdb_value_primitive_to_str: {}".format(gdb_value))

    gdb_value_type_code = gdb_value.type.strip_typedefs().code

    if gdb_value_type_code in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        raise Exception("obj_value_to_value called on a non primitive type")

    if gdb_value_type_code == gdb.TYPE_CODE_INT:
        return hex(int(gdb_value))

    return str(gdb_value)


def append_gdb_value_to_dict(gdb_value: gdb.Value, data: dict):
    """
    Recursive function to convert gdb.Value object to dict key/values
    and add them into given dict.

    //!\\ Function is recursive

    :param gdb_value: gdb.Value to be appended (Can be any C type)
    :param data: dict to be filled
    :return: None
    """

    print_debug("append_gdb_value_to_dict: {}".format(gdb_value))

    assert isinstance(data, dict), f"data must be a dict, not {type(data)}"

    gdb_value_type_code = gdb_value.type.strip_typedefs().code

    print_debug("-- struct_type: {} code: {}".format(gdb_value.type,
                                                     gdb_value.type.code))

    if gdb_value_type_code not in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        raise Exception("obj_value_to_dict called on a primitive type")

    # Recursively extract data from nested structs/unions/arrays
    fields = gdb_value.type.fields()

    for i, field in enumerate(fields):
        field_name = field.name

        if field_name is None:
            # This happens with anonymous struct field (C11)
            # https://gcc.gnu.org/onlinedocs/gcc/Unnamed-Fields.html
            field_name = "::unnamed_field_{}".format(i)
            # Field value should not be accessed by field_name
            # This is documented in:
            # https://sourceware.org/bugzilla/show_bug.cgi?id=15464

        field_value = gdb_value[field]

        field_value = gdb_value[field]

        field_type = field_value.type.strip_typedefs()
        field_type_code = field_type.code

        print_debug("---- subfield_name: {} "
                    "type_raw: {} {} "
                    "type_: {} {} ".format(
                        field_name,
                        field.type,
                        field.type.code,
                        field_type, field_type.code))

        if field_type_code in (gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION):
            print_debug("Creating struct under data [{}]".format(field_name))

            # If the field is a nested struct, recursively extract its data
            struct_data: dict = {}
            append_gdb_value_to_dict(field_value, struct_data)
            if field_type_code == gdb.TYPE_CODE_STRUCT:
                key_ = field_name + "::struct"
            else:  # gdb.TYPE_CODE_UNION
                key_ = field_name + "::union"
            data[key_] = struct_data

        elif field_type_code == gdb.TYPE_CODE_ARRAY:
            print_debug("Creating array under data [{}]".format(field_name))
            # Initialize it as a list
            key_ = field_name + "::array"
            data[key_] = []

            # For each item in the array, recursively extract its data and
            # append it to the list
            for j in range(field_type.range()[1]):
                append_gdb_value_to_list(field_value[j], data[key_])

        else:
            print_debug("Creating primitive under [{}]".format(field_name))
            data[field_name] = gdb_value_primitive_to_str(field_value)


def append_gdb_value_to_list(gdb_value: gdb.Value,
                             list_to_fill: list):
    """
    Recursive function to convert gdb.Value object to dict key/values and adds
    them into given dict

    //!\\ Function is recursive (indirectly through append_gdb_value_to_dict)

    :param gdb_value: gdb.Value to be appended (Can be any C type)
    :param data: dict to be filled
    :return: None
    """

    print_debug("append_gdb_value_to_list: {}".format(gdb_value))

    assert isinstance(list_to_fill, list), "list_to_fill must be a list, "\
                                           f"not {type(list_to_fill)}"

    obj_value_code = gdb_value.type.strip_typedefs().code
    # If the object is a struct, union, array...
    # put it in a dict then append it
    if obj_value_code in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        item: dict = {}
        append_gdb_value_to_dict(gdb_value, item)
        list_to_fill.append(item)

    # Primitive type (int, char, enum, etc) append it directly
    else:
        list_to_fill.append(gdb_value_primitive_to_str(gdb_value))

    print_debug("Returning data: {}".format(json.dumps(list_to_fill,
                                                       indent=4)))
