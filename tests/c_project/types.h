#ifndef TEST_HEADER_H
#define TEST_HEADER_H

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

#endif /* TEST_HEADER_H */
