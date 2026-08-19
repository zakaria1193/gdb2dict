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
    gdb.TYPE_CODE_ARRAY,
    gdb.TYPE_CODE_CLASS # Added for C++ classes
]


def gdb_value_to_dict(gdb_value: gdb.Value):
    """
    Converts a gdb.Value to a dictionary.
    Handles basic C types as well as C++ classes, including polymorphism.

    :param gdb_value: gdb.Value -> The GDB value to convert.
    :return: data: dict -> The data of the gdb_value as a dict.
    """
    data: dict = {}

    val_to_process = gdb_value
    type_to_check = gdb_value.type

    # Handle pointers/references and prefer dynamic type for the actual object
    if gdb_value.type.code == gdb.TYPE_CODE_PTR or gdb_value.type.code == gdb.TYPE_CODE_REF:
        try:
            deref_val = gdb_value.dereference()
            # After dereferencing, check the dynamic type of the object itself
            if hasattr(deref_val, 'dynamic_type') and deref_val.dynamic_type:
                val_to_process = deref_val
                type_to_check = deref_val.dynamic_type
            else:
                val_to_process = deref_val
                type_to_check = deref_val.type
        except gdb.error:
            # Cannot dereference (e.g., void*, null pointer, or points to incomplete type)
            # In this case, we can't do much more, so we'll just represent the pointer itself.
            # Or, if it's a known non-composite type, it might be handled as primitive later.
             print_debug(f"Cannot dereference pointer: {gdb_value}, type: {gdb_value.type}")
             # Fall through to let append_gdb_value_to_dict handle it or raise exception if needed.
             # If it's a pointer to a primitive, it won't be in OBJ_TYPE_NEEDS_RECURSIVE_CALL.
             pass # Keep original val_to_process and type_to_check for now
    elif hasattr(gdb_value, 'dynamic_type') and gdb_value.dynamic_type:
        # This handles cases where gdb_value is a direct class instance (not a pointer)
        # and has a dynamic type different from its static type (though less common for non-pointers).
        val_to_process = gdb_value # Or should it be gdb_value.dynamic_value? Test this.
                                  # For now, assume gdb_value itself is what we operate on,
                                  # but field resolution will use its dynamic_type.
        type_to_check = gdb_value.dynamic_type

    type_to_check = type_to_check.strip_typedefs()

    if type_to_check.code not in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        # This path is for types that are not structs, unions, arrays, or classes.
        # It implies that the top-level item itself is a primitive or an unhandled pointer.
        # The original script raised an exception. Let's refine this:
        # If it's a pointer that couldn't be dereferenced to a composite type,
        # we might want to represent it as a primitive (its address).
        if val_to_process.type.strip_typedefs().code == gdb.TYPE_CODE_PTR:
             data[str(val_to_process.type)] = gdb_value_primitive_to_str(val_to_process)
             return data
        raise Exception(f"gdb_value_to_dict called on a non-composite type: {type_to_check.name} (code: {type_to_check.code})")

    append_gdb_value_to_dict(val_to_process, data)
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

    gdb_value_type = gdb_value.type.strip_typedefs()
    gdb_value_type_code = gdb_value_type.code

    if gdb_value_type_code in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        # This can happen if a non-dereferenceable pointer to a composite type is passed.
        # Represent it as its address.
        if gdb_value_type.code == gdb.TYPE_CODE_PTR:
            return str(gdb_value)
        raise Exception("gdb_value_primitive_to_str called on a non-primitive type: {}".format(gdb_value_type.name))

    if gdb_value_type_code == gdb.TYPE_CODE_INT:
        try:
            return hex(int(gdb_value))
        except gdb.error: # e.g. for <optimized out>
            return str(gdb_value)


    # For enums, gdb.Value.__str__ usually gives "enum_name::enum_value" or just "enum_value"
    # which is desirable.
    return str(gdb_value)


def append_gdb_value_to_dict(gdb_value: gdb.Value, data: dict):
    """
    Recursive function to convert gdb.Value object (struct, class, union)
    to dict key/values and add them into the given dict.

    Handles C++ classes, including base class members and dynamic types.

    :param gdb_value: gdb.Value to be appended (Must be a struct, class, or union)
    :param data: dict to be filled
    :return: None
    """
    print_debug(f"append_gdb_value_to_dict processing: {gdb_value} type: {gdb_value.type}")
    assert isinstance(data, dict), f"data must be a dict, not {type(data)}"

    # Determine the type to use for field iteration (static vs dynamic)
    val_type = gdb_value.type
    if hasattr(gdb_value, 'dynamic_type') and gdb_value.dynamic_type and gdb_value.dynamic_type != val_type:
        val_type = gdb_value.dynamic_type

    val_type = val_type.strip_typedefs() # Ensure we have the base type

    # This function should only be called for types that have fields.
    if val_type.code not in [gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION, gdb.TYPE_CODE_CLASS]:
        raise Exception(f"append_gdb_value_to_dict called on a non-struct/class/union type: {val_type.name} (code: {val_type.code}) for gdb_value: {gdb_value}")

    fields = []
    try:
        fields = val_type.fields()
    except gdb.error as e:
        print_debug(f"Error getting fields for {val_type.name}: {e}. This might be an opaque type or template not fully instantiated.")
        data["##error_getting_fields"] = str(e)
        return


    for i, field in enumerate(fields):
        field_name = field.name
        is_base_class_field = field.is_base_class

        if field_name is None:
            # Handle anonymous/unnamed fields (e.g. anonymous unions/structs)
            # or potentially base class subobjects if GDB presents them without a direct name here.
            # If it's a base class subobject, its fields will be processed recursively.
            if is_base_class_field and field.type and field.type.code in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
                 # This is a base class sub-object. Recursively add its fields.
                 # GDB often flattens the hierarchy, but if it provides a base class "field",
                 # we should process it. The `gdb_value[field]` should give the base part.
                try:
                    base_obj_value = gdb_value.cast(field.type) # Cast to the base type
                    # Use a name that indicates it's from a base class
                    base_class_name = field.type.name if field.type.name else f"##base_class_{i}"
                    # Ensure no ## in base_class_name if it's used as key directly.
                    base_class_name_key = base_class_name.replace(":", "_").replace("<", "_").replace(">", "_").replace(" ", "")

                    print_debug(f"Processing unnamed base class field: {base_class_name_key} of type {field.type.name}")
                    nested_data: dict = {}
                    # The gdb_value itself contains the base class part, so we pass it casted.
                    append_gdb_value_to_dict(base_obj_value, nested_data)
                    data[f"{base_class_name_key}##base_class_members"] = nested_data
                    continue
                except gdb.error as e:
                    print_debug(f"Error casting to base class {field.type.name}: {e}")
                    data[f"##error_accessing_unnamed_base_field_{i}"] = str(e)
                    continue
            else:
                field_name = f"##unnamed_field_{i}"

        # Skip fields that are functions/methods or artificial (like vtable)
        if field.type is not None and field.type.code == gdb.TYPE_CODE_FUNC:
            print_debug(f"Skipping function/method field: {field_name}")
            continue
        if field.artificial:
            print_debug(f"Skipping artificial field: {field_name}")
            continue

        # GDB may qualify names of members from base classes e.g. "Base::member"
        # Or it might provide them directly if the hierarchy is flattened.
        # If is_base_class is true, field_name might already be qualified.
        # We don't need special handling for field_name itself here based on is_base_class,
        # as gdb_value[field_name] or gdb_value[field] should work.

        try:
            # Try accessing by the field object itself first, then by name.
            # Using gdb_value[field] is generally safer, especially for unnamed/anonymous fields.
            field_value = gdb_value[field]
        except gdb.error:
            try:
                field_value = gdb_value[field_name]
            except gdb.error as e:
                print_debug(f"Could not access field {field_name} (type: {field.type}): {e}")
                data[f"{field_name}##error"] = f"Error accessing field: {e}"
                continue

        # Determine the actual type of the field's value, considering dynamic type for pointers/references
        field_val_to_process = field_value
        field_actual_type = field_value.type.strip_typedefs()

        if field_actual_type.code == gdb.TYPE_CODE_PTR or field_actual_type.code == gdb.TYPE_CODE_REF:
            try:
                deref_val = field_value.dereference()
                # Check dynamic type of the dereferenced object
                if hasattr(deref_val, 'dynamic_type') and deref_val.dynamic_type:
                    field_actual_type = deref_val.dynamic_type.strip_typedefs()
                    field_val_to_process = deref_val # Process the dereferenced object itself
                else:
                    field_actual_type = deref_val.type.strip_typedefs()
                    field_val_to_process = deref_val
            except gdb.error: # Cannot dereference (e.g. void*, null pointer)
                # Keep pointer type, field_val_to_process remains the pointer itself
                print_debug(f"Field {field_name} is a pointer/ref that cannot be dereferenced: {field_value}")
                pass
        elif hasattr(field_value, 'dynamic_type') and field_value.dynamic_type:
             # Field is a direct object (not ptr/ref) but has a dynamic type (e.g. embedded polymorphic obj)
            field_actual_type = field_value.dynamic_type.strip_typedefs()
            # field_val_to_process is already field_value

        field_actual_type_code = field_actual_type.code

        print_debug(f"---- subfield_name: {field_name} (is_base: {is_base_class_field}), "
                    f"static_type: {field.type}, actual_type: {field_actual_type} (code: {field_actual_type_code}), "
                    f"value to process: {field_val_to_process}")

        if field_actual_type_code == gdb.TYPE_CODE_STRUCT:
            print_debug(f"Creating struct under data [{field_name}]")
            nested_data: dict = {}
            append_gdb_value_to_dict(field_val_to_process, nested_data)
            key_ = f"{field_name}##struct"
            data[key_] = nested_data
        elif field_actual_type_code == gdb.TYPE_CODE_CLASS:
            print_debug(f"Creating class instance under data [{field_name}]")
            nested_data: dict = {}
            append_gdb_value_to_dict(field_val_to_process, nested_data)
            key_ = f"{field_name}##class"
            data[key_] = nested_data
        elif field_actual_type_code == gdb.TYPE_CODE_UNION:
            print_debug(f"Creating union under data [{field_name}]")
            # For unions, GDB usually shows the "currently active" field if discernible,
            # or all fields. Our recursive call will list all members of the union type.
            # This might not always be what a user wants for a union (they might want only the active field),
            # but gdb.Value for a union doesn't directly tell which field is active.
            nested_data: dict = {}
            append_gdb_value_to_dict(field_val_to_process, nested_data) # field_val_to_process is the union itself
            key_ = f"{field_name}##union"
            data[key_] = nested_data
        elif field_actual_type_code == gdb.TYPE_CODE_ARRAY:
            print_debug(f"Creating array under data [{field_name}]")
            key_ = f"{field_name}##array"
            data[key_] = []
            # field_val_to_process is the array itself. Iterate its elements.
            # Need to handle array range correctly. field_actual_type should have .range()
            try:
                # For dynamically sized arrays or arrays where range is not obvious,
                # gdb might not return a full range, or range()[1] might be large for VLA.
                # Let's assume fixed-size arrays primarily.
                array_range = field_actual_type.range()
                num_elements = array_range[1] - array_range[0] + 1

                # Check for C-strings (char arrays) to avoid huge lists for long strings
                # TYPE_CODE_CHAR is not a direct type, but element type can be checked
                # A common convention is to stop at null terminator for char arrays.
                # However, for general array display, showing all declared elements is better.
                # For now, process all elements as per declared range.

                print_debug(f"Array {field_name} range: {array_range}, num_elements: {num_elements}")


                for j in range(num_elements):
                     # Access element using array_range[0] + j if range doesn't start at 0
                    element_val = field_val_to_process[array_range[0] + j]
                    append_gdb_value_to_list(element_val, data[key_])

            except gdb.error as e:
                print_debug(f"Error processing array {field_name}: {e}")
                data[key_] = f"Error processing array: {e}"
            except Exception as e: # Catch any other errors during array processing
                print_debug(f"Unexpected error processing array {field_name}: {e}")
                data[key_] = f"Unexpected error processing array: {e}"


        else: # Primitive types, enums, pointers that weren't dereferenced to composite types
            print_debug(f"Creating primitive under [{field_name}] value: {field_val_to_process}")
            data[field_name] = gdb_value_primitive_to_str(field_val_to_process)


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

    print_debug(f"append_gdb_value_to_list processing: {gdb_value} into list: {list_to_fill}")

    assert isinstance(list_to_fill, list), f"list_to_fill must be a list, not {type(list_to_fill)}"

    # Determine the actual value and type to process, especially for pointers/references
    val_to_process = gdb_value
    actual_type = gdb_value.type.strip_typedefs()

    if actual_type.code == gdb.TYPE_CODE_PTR or actual_type.code == gdb.TYPE_CODE_REF:
        try:
            deref_val = gdb_value.dereference()
            # Check dynamic type of the dereferenced object
            if hasattr(deref_val, 'dynamic_type') and deref_val.dynamic_type:
                actual_type = deref_val.dynamic_type.strip_typedefs()
                val_to_process = deref_val
            else:
                actual_type = deref_val.type.strip_typedefs()
                val_to_process = deref_val
        except gdb.error:
            # Cannot dereference (e.g. void*, null pointer, points to incomplete type)
            # Keep pointer type, val_to_process remains the pointer itself
            print_debug(f"List element {gdb_value} is a pointer/ref that cannot be dereferenced.")
            pass # actual_type and val_to_process are already set to the pointer itself

    actual_type_code = actual_type.code

    # If the object is a struct, class, union, or array...
    # put it in a dict then append it
    if actual_type_code in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        item_data: dict = {}
        # Pass val_to_process which might be the dereferenced object
        append_gdb_value_to_dict(val_to_process, item_data)
        list_to_fill.append(item_data)
    # Primitive type (int, char, enum, pointer to primitive, etc.) append it directly
    else:
        # val_to_process here will be the primitive value itself, or a non-dereferenceable pointer
        list_to_fill.append(gdb_value_primitive_to_str(val_to_process))

    if DEBUG: # Conditional print_debug for potentially large structures
        try:
            # Attempt to serialize for debugging, but catch errors if it's too complex or fails
            debug_output = json.dumps(list_to_fill, indent=4, default=str) # Use default=str for non-serializable
            print_debug(f"List after appending: {debug_output}")
        except TypeError:
            print_debug(f"List after appending contains non-serializable data (length: {len(list_to_fill)})")
        except Exception as e:
            print_debug(f"Error serializing list for debug: {e} (length: {len(list_to_fill)})")
