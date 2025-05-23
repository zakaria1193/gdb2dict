#ifndef TYPES_HPP
#define TYPES_HPP

#include <string>
#include <vector> // Required for std::vector, even if not directly used in this file

// Forward declaration for Container class
class Container;

// C-style enum
enum Color { RED, GREEN, BLUE };

// C++ scoped enum
enum class Shape { CIRCLE, SQUARE, TRIANGLE };

// Basic Class
class BasicClass {
public:
    int public_int = 10;
    float public_float = 3.14f;
    bool public_bool = true;
    char public_char = 'A';
    std::string public_string = "Hello";
};

// Base Class for Inheritance and Polymorphism
class Base {
public:
    int base_public_int = 1;
    static int static_base_public_int;
    static const int static_const_base_public_int = 100;

    Base() : base_protected_int(2), base_private_int(3) {}
    virtual ~Base() {} // Virtual destructor for proper cleanup

    virtual std::string getClassName() { return "Base"; }
    virtual int virtual_func() { return 10; }

    void public_base_method() {}

protected:
    int base_protected_int;
    std::string base_protected_string = "BaseProtected";
    static int static_base_protected_int;


private:
    int base_private_int;
    std::string base_private_string = "BasePrivate";
    static int static_base_private_int;

};

// Derived Class
class Derived : public Base {
public:
    int derived_public_int = 4;
    // Hiding Base members
    int base_public_int = 40; // Hides Base::base_public_int

    static int static_derived_public_int;
    static const int static_const_derived_public_int = 200;


    Derived() : derived_protected_int(5), derived_private_int(6) {}

    std::string getClassName() override { return "Derived"; }
    int virtual_func() override { return 20; }

    void public_derived_method() {}

protected:
    int derived_protected_int;
    std::string derived_protected_string = "DerivedProtected";
    // Hiding Base protected member
    std::string base_protected_string = "DerivedProtectedHiding";
    static int static_derived_protected_int;


private:
    int derived_private_int;
    std::string derived_private_string = "DerivedPrivate";
    static int static_derived_private_int;

};

// Class for Composition
class Contained {
public:
    int id = 0;
    std::string data = "ContainedData";
    Contained() = default;
    Contained(int i, std::string s) : id(i), data(s) {}
};

class Container {
public:
    BasicClass basic_obj;
    Derived derived_obj;
    Contained contained_obj{1, "InitialContained"};
    Contained* pointer_to_contained = nullptr;
    Contained& reference_to_contained;

    // Arrays
    int primitive_array[5] = {1, 2, 3, 4, 5};
    Contained object_array[3];

    // Pointers
    int* int_ptr = nullptr;
    int* uninit_int_ptr;
    BasicClass* basic_ptr = nullptr;
    BasicClass* uninit_basic_ptr;


    // Enums
    Color color_member = RED;
    Shape shape_member = Shape::CIRCLE;

    Container(Contained& ref_contained) : reference_to_contained(ref_contained) {
        pointer_to_contained = new Contained(2, "PointedToContained");
        int_ptr = new int(123);
        basic_ptr = new BasicClass();
        object_array[0] = Contained(10, "ArrayElem0");
        object_array[1] = Contained(11, "ArrayElem1");
        object_array[2] = Contained(12, "ArrayElem2");
    }

    ~Container() {
        delete pointer_to_contained;
        delete int_ptr;
        delete basic_ptr;
    }
};

#endif // TYPES_HPP
