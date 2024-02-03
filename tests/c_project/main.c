#include "types.h"
#include <stdio.h>

enum types {
  TYPE_PRIMITIVE,
  TYPE_STRUCT_POINT,
  TYPE_STRUCT_SHAPE,
  TYPE_STRUCT_COMPLEX
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

    return 0;
}
