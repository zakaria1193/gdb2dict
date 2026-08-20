## Changelog

# Unreleased

- Add C++ support: base class subobjects are dumped under `BaseName##base`,
  the dynamic type of a polymorphic pointer/reference is resolved, static
  data members are included, and vtable pointers are skipped
- `gdb_value_to_dict` now accepts a pointer or a reference and dereferences
  it, instead of raising
- References are resolved to the object they refer to
- New opt-in `follow_pointers` argument to dump pointed-to structs inline,
  with cycle detection and a `max_depth` guard. Off by default, so the
  output of existing callers does not change
- Fix an off-by-one that dropped the last element of every array. Arrays now
  contain their whole declared range, so a dump has one more element per
  array than before
- Tests now cover C++ and a failing comparison fails the build

# V0.1.1

- Only documentation is updated

# V0.1.0

- Changed API completely. Now the only way to use the library is to call `gdb_value_to_dict`

# V0.0.3

- Fix dump of anonymous struct/union fields (C11 feature)

# V0.0.2

- Initial release
