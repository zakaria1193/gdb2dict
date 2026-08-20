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

# Types that hold a nested object we can descend into (struct and C++ class
# share TYPE_CODE_STRUCT in gdb, there is no separate code for a class).
COMPOSITE_TYPE_CODES = (
    gdb.TYPE_CODE_STRUCT,
    gdb.TYPE_CODE_UNION,
)

# gdb.TYPE_CODE_RVALUE_REF only exists on newer gdb versions
REFERENCE_TYPE_CODES = tuple(
    code for code in (gdb.TYPE_CODE_REF,
                      getattr(gdb, "TYPE_CODE_RVALUE_REF", None))
    if code is not None
)

# Guards against structures that point back at themselves. Cycles are
# detected exactly, this is only a backstop for pathologically deep data.
DEFAULT_MAX_DEPTH = 64


def gdb_value_to_dict(gdb_value: gdb.Value,
                      follow_pointers: bool = False,
                      max_depth: int = DEFAULT_MAX_DEPTH):
    """
    Converts a gdb.Value to a dict.

    Handles C structs/unions/arrays as well as C++ classes, inheritance,
    polymorphism and static data members.

    If gdb_value is a pointer or a reference it is dereferenced first, and
    the dynamic (most derived) type of the pointee is used, so a `Base *`
    that actually points at a `Derived` is dumped as a `Derived`.

    :param gdb_value: gdb.Value -> Must be a struct, class, union or array,
                      or a pointer/reference to one
    :param follow_pointers: bool -> If True, pointer members pointing at a
                            struct/class/union are dereferenced and dumped
                            as nested dicts. If False (default) they are
                            rendered as their address, as they always were.
    :param max_depth: int -> Maximum nesting depth before the dump stops
    :return: data: dict -> The data of the gdb.Value as a dict
    """

    data: dict = {}

    value = gdb_value
    type_code = value.type.strip_typedefs().code

    if type_code == gdb.TYPE_CODE_PTR or type_code in REFERENCE_TYPE_CODES:
        if _is_null_pointer(value):
            raise Exception("gdb_value_to_dict called on a null pointer")
        value = _dereference(value)
        if value is None:
            raise Exception("gdb_value_to_dict could not dereference "
                            "{}".format(gdb_value.type))

    if value.type.strip_typedefs().code not in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        raise Exception("gdb_value_to_dict called on a primitive type")

    context = _Context(follow_pointers=follow_pointers, max_depth=max_depth)
    append_gdb_value_to_dict(value, data, context)
    return data


class _Context:
    """
    Traversal state shared by the recursive helpers.

    `path` holds the objects currently being expanded, so a member that
    points back at one of its own ancestors is reported instead of being
    followed forever.
    """

    def __init__(self, follow_pointers: bool, max_depth: int):
        self.follow_pointers = follow_pointers
        self.max_depth = max_depth
        self.path = []

    def enter(self, gdb_value: gdb.Value):
        key = _identity_of(gdb_value)
        if key is not None and key in self.path:
            return None
        self.path.append(key)
        return key

    def leave(self):
        self.path.pop()


def _identity_of(gdb_value: gdb.Value):
    """
    Address + type of a value, used to recognise a cycle. Values that have
    no address (registers, optimized out) return None and are never
    considered cyclic.
    """

    try:
        address = gdb_value.address
        if address is None:
            return None
        return (int(address), str(gdb_value.type.strip_typedefs()))
    except Exception:
        return None


def _is_null_pointer(gdb_value: gdb.Value):
    """
    True if gdb_value is a pointer holding NULL. Dereferencing such a value
    succeeds in gdb and only fails later, when the memory is read, so it has
    to be checked up front.
    """

    if gdb_value.type.strip_typedefs().code != gdb.TYPE_CODE_PTR:
        return False

    try:
        return int(gdb_value) == 0
    except Exception:
        return False


def _dynamic_cast(gdb_value: gdb.Value):
    """
    Casts gdb_value to its dynamic type when it has one, so a base class
    pointer/reference is dumped as the derived object it really points at.
    Non polymorphic values are returned untouched.
    """

    try:
        dynamic_type = gdb_value.dynamic_type
    except Exception:
        return gdb_value

    if dynamic_type is None or dynamic_type == gdb_value.type:
        return gdb_value

    try:
        return gdb_value.cast(dynamic_type)
    except Exception:
        return gdb_value


def _dereference(gdb_value: gdb.Value):
    """
    Dereferences a pointer or reference and resolves the dynamic type of
    the result, so a `Base *` holding a `Derived` yields a `Derived`.

    :return: the pointee as a gdb.Value, or None if it cannot be read
    """

    try:
        if gdb_value.type.strip_typedefs().code in REFERENCE_TYPE_CODES:
            # gdb rejects dereference() on a reference, it wants
            # referenced_value() instead
            value = gdb_value.referenced_value()
        else:
            value = gdb_value.dereference()

        value = _dynamic_cast(value)

        # Force a read now so unreadable memory fails here rather than
        # halfway through the dump.
        value.fetch_lazy()
        return value
    except Exception as e:
        print_debug("Cannot dereference {}: {}".format(gdb_value.type, e))
        return None


def _target_type_code(gdb_value: gdb.Value):
    """
    Type code of what a pointer/reference points at, or None if unknown.
    """

    try:
        return gdb_value.type.strip_typedefs().target().strip_typedefs().code
    except Exception:
        return None


def _composite_suffix(type_code):
    if type_code == gdb.TYPE_CODE_UNION:
        return "##union"
    return "##struct"


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
        try:
            return hex(int(gdb_value))
        except (gdb.error, gdb.MemoryError, ValueError):
            # e.g. <optimized out>
            return str(gdb_value)

    return str(gdb_value)


def _fields_of(gdb_value: gdb.Value):
    """
    Fields of a value's own type. The static type is used on purpose: the
    caller resolves the dynamic type when it enters an object, so a base
    class subobject is iterated with the base class' own field list.
    """

    return gdb_value.type.strip_typedefs().fields()


def _is_static_field(field):
    """
    Static data members carry no offset inside the object.
    """

    if field.is_base_class:
        return False

    return getattr(field, "bitpos", None) is None


def _read_field(gdb_value: gdb.Value, field, field_name: str):
    """
    Reads a member out of a value.

    :return: the member as a gdb.Value, or None if it cannot be read
    """

    try:
        return gdb_value[field]
    except Exception:
        pass

    # Static members are not addressable through the field object on every
    # gdb version, look them up by name instead.
    if field_name is not None:
        try:
            return gdb_value[field_name]
        except Exception as e:
            print_debug("Could not read field {}: {}".format(field_name, e))

    return None


def append_gdb_value_to_dict(gdb_value: gdb.Value,
                             data: dict,
                             context: "_Context" = None):
    """
    Recursive function to convert gdb.Value object to dict key/values
    and add them into given dict.

    //!\\ Function is recursive

    :param gdb_value: gdb.Value to be appended (Can be any C or C++ type)
    :param data: dict to be filled
    :param context: internal traversal state, created on the fly when the
                    function is called directly
    :return: None
    """

    print_debug("append_gdb_value_to_dict: {}".format(gdb_value))

    assert isinstance(data, dict), f"data must be a dict, not {type(data)}"

    if context is None:
        context = _Context(follow_pointers=False,
                           max_depth=DEFAULT_MAX_DEPTH)

    gdb_value_type = gdb_value.type.strip_typedefs()
    gdb_value_type_code = gdb_value_type.code

    print_debug("-- struct_type: {} code: {}".format(gdb_value.type,
                                                     gdb_value.type.code))

    if gdb_value_type_code not in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        raise Exception("obj_value_to_dict called on a primitive type")

    if len(context.path) >= context.max_depth:
        data["##max_depth_reached"] = str(gdb_value.type)
        return

    if context.enter(gdb_value) is None:
        data["##cycle"] = str(gdb_value.type)
        return

    try:
        if gdb_value_type_code == gdb.TYPE_CODE_ARRAY:
            data["##array"] = _array_to_list(gdb_value,
                                             gdb_value_type,
                                             context)
        else:
            _append_fields_to_dict(gdb_value, data, context)
    finally:
        context.leave()


def _append_fields_to_dict(gdb_value: gdb.Value,
                           data: dict,
                           context: "_Context"):
    """
    Walks the members of a struct/class/union value and fills data with
    them. Split out of append_gdb_value_to_dict so the cycle bookkeeping
    stays in one place.
    """

    fields = _fields_of(gdb_value)

    for i, field in enumerate(fields):
        field_name = field.name

        # A base class subobject. Cast to the base type rather than looking
        # the name up: looking up "Base" on a value resolves to the base
        # class constructor, not to the inherited data.
        if field.is_base_class:
            if field.name:
                base_name = field.name
            else:
                base_name = "##base_class_{}".format(i)
            try:
                base_value = gdb_value.cast(field.type)
            except Exception as e:
                data[base_name + "##unreadable"] = str(e)
                continue
            base_data: dict = {}
            append_gdb_value_to_dict(base_value, base_data, context)
            data[base_name + "##base"] = base_data
            continue

        # The vtable pointer and other compiler generated members are not
        # part of the program's data.
        if getattr(field, "artificial", False):
            print_debug("Skipping artificial field {}".format(field_name))
            continue

        if field.type is not None \
                and field.type.strip_typedefs().code == gdb.TYPE_CODE_FUNC:
            print_debug("Skipping method field {}".format(field_name))
            continue

        if field_name is None:
            # This happens with anonymous struct field (C11)
            # https://gcc.gnu.org/onlinedocs/gcc/Unnamed-Fields.html
            field_name = "##unnamed_field_{}".format(i)
            # Field value should not be accessed by field_name
            # This is documented in:
            # https://sourceware.org/bugzilla/show_bug.cgi?id=15464

        field_value = _read_field(gdb_value, field, field.name)

        if field_value is None:
            if _is_static_field(field):
                # A static with no out of line definition has no storage to
                # read, it simply is not part of the dump.
                print_debug("Skipping unreadable static {}".format(field_name))
                continue
            data[field_name + "##unreadable"] = str(field.type)
            continue

        _append_member(field_name, field_value, data, context)


def _append_member(field_name: str,
                   field_value: gdb.Value,
                   data: dict,
                   context: "_Context"):
    """
    Adds one already read member to data, under the key convention
    documented in the README.
    """

    field_type = field_value.type.strip_typedefs()
    field_type_code = field_type.code

    print_debug("---- subfield_name: {} type_: {} {}".format(
        field_name, field_type, field_type_code))

    if field_type_code in COMPOSITE_TYPE_CODES:
        key_ = field_name + _composite_suffix(field_type_code)
        struct_data: dict = {}
        append_gdb_value_to_dict(field_value, struct_data, context)
        data[key_] = struct_data
        return

    if field_type_code == gdb.TYPE_CODE_ARRAY:
        key_ = field_name + "##array"
        data[key_] = _array_to_list(field_value, field_type, context)
        return

    if field_type_code in REFERENCE_TYPE_CODES:
        # References cannot be null in a valid program, and printing one
        # yields "@0xaddr: {...}", so always resolve them.
        referent = _dereference(field_value)
        if referent is not None:
            referent_code = referent.type.strip_typedefs().code
            if referent_code in COMPOSITE_TYPE_CODES:
                key_ = field_name + _composite_suffix(referent_code)
                ref_data: dict = {}
                append_gdb_value_to_dict(referent, ref_data, context)
                data[key_] = ref_data
                return
            data[field_name] = gdb_value_primitive_to_str(referent)
            return

    if field_type_code == gdb.TYPE_CODE_PTR and context.follow_pointers:
        if not _is_null_pointer(field_value) \
                and _target_type_code(field_value) in COMPOSITE_TYPE_CODES:
            pointee = _dereference(field_value)
            if pointee is not None:
                pointee_code = pointee.type.strip_typedefs().code
                key_ = field_name + _composite_suffix(pointee_code)
                ptr_data: dict = {}
                append_gdb_value_to_dict(pointee, ptr_data, context)
                data[key_] = ptr_data
                return

    # Primitives, enums, and pointers we are not following
    try:
        data[field_name] = gdb_value_primitive_to_str(field_value)
    except (gdb.error, gdb.MemoryError) as e:
        data[field_name + "##unreadable"] = str(e)


def _array_to_list(field_value: gdb.Value,
                   field_type: gdb.Type,
                   context: "_Context"):
    """
    Converts an array member to a list, covering the whole declared range.
    """

    items: list = []

    try:
        low, high = field_type.range()
    except Exception as e:
        print_debug("Cannot get range of array: {}".format(e))
        return items

    # range() is inclusive on both ends
    for index in range(low, high + 1):
        append_gdb_value_to_list(field_value[index], items, context)

    return items


def append_gdb_value_to_list(gdb_value: gdb.Value,
                             list_to_fill: list,
                             context: "_Context" = None):
    """
    Recursive function to convert gdb.Value object to dict key/values and adds
    them into given dict

    //!\\ Function is recursive (indirectly through append_gdb_value_to_dict)

    :param gdb_value: gdb.Value to be appended (Can be any C or C++ type)
    :param list_to_fill: list to be filled
    :param context: internal traversal state, created on the fly when the
                    function is called directly
    :return: None
    """

    print_debug("append_gdb_value_to_list: {}".format(gdb_value))

    assert isinstance(list_to_fill, list), "list_to_fill must be a list, "\
                                           f"not {type(list_to_fill)}"

    if context is None:
        context = _Context(follow_pointers=False,
                           max_depth=DEFAULT_MAX_DEPTH)

    obj_value_code = gdb_value.type.strip_typedefs().code

    # If the object is a struct, union, array...
    # put it in a dict then append it
    if obj_value_code in OBJ_TYPE_NEEDS_RECURSIVE_CALL:
        item: dict = {}
        append_gdb_value_to_dict(gdb_value, item, context)
        list_to_fill.append(item)

    # Primitive type (int, char, enum, etc) append it directly
    else:
        list_to_fill.append(gdb_value_primitive_to_str(gdb_value))

    print_debug("Returning data: {}".format(json.dumps(list_to_fill,
                                                       indent=4)))
