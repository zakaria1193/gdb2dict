#ifndef TEST_TYPES_HPP
#define TEST_TYPES_HPP

#include <string>

// C style enum
enum Color { RED, GREEN, BLUE };

// C++ scoped enum
enum class Shape { CIRCLE, SQUARE, TRIANGLE };

// Plain class with only primitive members.
//
// Fixed size char arrays are used instead of std::string on purpose: the
// layout of std::string is an implementation detail of the standard library
// and would make the expected output depend on the toolchain version.
class BasicClass {
public:
    int public_int;
    float public_float;
    bool public_bool;
    char public_char;
    char name[8];
    Color color;
    Shape shape;

    BasicClass()
        : public_int(10), public_float(1.5f), public_bool(true),
          public_char('A'), name("basic"), color(RED),
          shape(Shape::CIRCLE) {}
};

// Base class of a polymorphic hierarchy
class Base {
public:
    int base_public_int;
    static int static_base_public_int;
    static const int static_const_base_public_int = 100;

    Base() : base_public_int(1), base_protected_int(2), base_private_int(3) {}
    virtual ~Base() {}

    virtual int virtual_func() { return 10; }

protected:
    int base_protected_int;

private:
    int base_private_int;
};

// Derived class, hides one of the base members on purpose
class Derived : public Base {
public:
    int derived_public_int;
    // Hides Base::base_public_int
    int base_public_int;
    static int static_derived_public_int;

    Derived()
        : derived_public_int(4), base_public_int(40),
          derived_protected_int(5), derived_private_int(6) {}

    int virtual_func() override { return 20; }

protected:
    int derived_protected_int;

private:
    int derived_private_int;
};

// Second level of inheritance
class MostDerived : public Derived {
public:
    int most_derived_int;

    MostDerived() : most_derived_int(7) {}

    int virtual_func() override { return 30; }
};

// Node that points at itself and at its neighbour, to exercise cycle
// detection when pointers are followed.
struct Node {
    int id;
    Node* self;
    Node* neighbour;
    Node* null_ptr;
};

// Aggregate holding nested objects, an array of objects and a reference
class Container {
public:
    int container_id;
    BasicClass embedded;
    BasicClass array_of_objects[3];
    int array_of_ints[4];
    Base* base_ptr_to_derived;
    Node* node_ptr;
    BasicClass& reference_to_embedded;
    void* void_ptr;
    Base* null_base_ptr;

    Container(Base* base_ptr, Node* node)
        : container_id(77), base_ptr_to_derived(base_ptr), node_ptr(node),
          reference_to_embedded(embedded), void_ptr(nullptr),
          null_base_ptr(nullptr) {
        array_of_ints[0] = 1;
        array_of_ints[1] = 2;
        array_of_ints[2] = 3;
        array_of_ints[3] = 4;
        for (int i = 0; i < 3; ++i) {
            array_of_objects[i].public_int = 100 + i;
        }
    }
};

// Only used by the smoke test, never byte compared against a fixture
class WithStdString {
public:
    int id;
    std::string text;

    WithStdString() : id(9), text("hello") {}
};

#endif /* TEST_TYPES_HPP */
