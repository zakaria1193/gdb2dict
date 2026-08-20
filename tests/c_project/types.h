#ifndef TEST_HEADER_H
#define TEST_HEADER_H

#include <stdint.h>

enum Color {
    RED,
    GREEN,
    BLUE
};

union Data {
    int intValue;
    float floatValue;
    char stringValue[20];
};

struct Point {
    int x;
    int y;
};

struct Shape {
    int id;
    enum Color color;
    union {
        int intValue;
        float floatValue;
    };
    struct {
        int x;
        int y;
    } center;
    union Data data;
};

struct ComplexObject {
    int value;
    struct {
        float x;
        float y;
    }; // unnamed struct member (C11)
    union {
        int intValue;
        char stringValue[10];
        struct Shape shape;
    }; // unnamed union member (C11)
};

/*
 * Regression coverage for issue #1: a gdb array type reports an inclusive
 * range, so the last element used to be dropped. Every array below is filled
 * with distinct values, and the last element of each is non-zero, so a
 * truncated dump changes the fixture instead of hiding in a tail of zeros.
 */
struct Arrays {
    int16_t int16_array[10];
    struct Point point_array[3];
    int matrix[2][3];
    enum Color color_array[3];
    char text[6];
};

#endif /* TEST_HEADER_H */
