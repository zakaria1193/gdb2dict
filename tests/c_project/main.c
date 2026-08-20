#include "types.h"
#include <stdio.h>

enum types {
  TYPE_PRIMITIVE,
  TYPE_STRUCT_POINT,
  TYPE_STRUCT_SHAPE,
  TYPE_STRUCT_COMPLEX,
  TYPE_STRUCT_ARRAYS
};

struct Point point_ = {
  .x = 10,
  .y = 20
};
struct Shape shape_ = {
  .id = 1,
  .color = RED,
  .intValue = 42,
  .center = {30, 40},
  .data = { .stringValue = "Hello" }
};

// Distinct, non-zero-terminated values so that dropping the last element of
// any array (issue #1) is visible in the dumped output.
struct Arrays arrays_ = {
  .int16_array = {100, 101, 102, 103, 104, 105, 106, 107, 108, 109},
  .point_array = {{1, 2}, {3, 4}, {5, 6}},
  .matrix = {{11, 12, 13}, {14, 15, 16}},
  .color_array = {RED, GREEN, BLUE},
  .text = {'g', 'd', 'b', '2', 'd', '!'}
};

struct ComplexObject complexObj_ = {
  .value = 999,
  .x = 1.5,
  .y = 2.5,
  .intValue = 123
};


// Empty printer function for GDB to catch
// Do not optimize this function so GDB can catch it
__attribute__((optimize("O0")))
void printPoint(struct Point *point) {
  // Empty function for GDB to catch
}

// Empty printer function for GDB to catch
// Do not optimize this function So GDB can catch it
__attribute__((optimize("O0")))
void printStructure(void *ptr, enum types type_enum)
{
  // Empty function for GDB to catch
}

int main() {
    printPoint(&point_);

    printStructure(&point_, TYPE_STRUCT_POINT);
    printStructure(&shape_, TYPE_STRUCT_SHAPE);
    printStructure(&complexObj_, TYPE_STRUCT_COMPLEX);
    printStructure(&arrays_, TYPE_STRUCT_ARRAYS);

    return 0;
}
