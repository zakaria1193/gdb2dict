## Changelog

# V1.3.0

Released 2026-08-20. A packaging-only release: no library code changed.

- Drop the claim of support for Python versions that have reached end of life.
  `requires-python` is now `>=3.10` (was `>=3.7`) and the classifiers list
  3.10 through 3.14, matching the versions the test matrix runs on
- CI now tests every currently supported Python: 3.10, 3.11, 3.12, 3.13 and
  3.14 (3.9 reached end of life in October 2025)
- Link this changelog from the project metadata, so it is reachable from the
  PyPI sidebar instead of only from GitHub
- Correct the licence copyright holder, which still named the Python Packaging
  Authority from the sample project this was scaffolded from
- Drop the `Funding` and `Say Thanks!` sample-project URLs, which pointed at
  placeholder addresses

# V1.2.0

Released 2026-08-20. The C++ support, the `follow_pointers` mode and the
array off-by-one fix in this release were developed with Claude Opus 5
(via Claude Code).

- Add C++ support: base class subobjects are dumped under `BaseName##base`,
  the dynamic type of a polymorphic pointer/reference is resolved, static
  data members are included, and vtable pointers are skipped
- `gdb_value_to_dict` now accepts a pointer or a reference and dereferences
  it, instead of raising
- References are resolved to the object they refer to
- New opt-in `follow_pointers` argument to dump pointed-to structs inline,
  with cycle detection and a `max_depth` guard. Off by default, so the
  output of existing callers does not change
- Fix an off-by-one that dropped the last element of every array (issue #1).
  `gdb.Type.range()` is inclusive on both ends, so arrays now contain their
  whole declared range and a dump has one more element per array than before.
  Covered by a `struct Arrays` regression test
- Tests now cover C++ and a failing comparison fails the build

# V0.1.1

- Only documentation is updated

# V0.1.0

- Changed API completely. Now the only way to use the library is to call `gdb_value_to_dict`

# V0.0.3

- Fix dump of anonymous struct/union fields (C11 feature)

# V0.0.2

- Initial release
