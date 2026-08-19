#include "types.hpp"

#include <iostream>

// Out of line definitions for the static data members
int Base::static_base_public_int = 101;
int Derived::static_derived_public_int = 201;

// Empty printer functions for GDB to catch.
// Do not optimize them so GDB can catch them.
__attribute__((optimize("O0")))
void printBasicClass(BasicClass* obj) {
    // Empty function for GDB to catch
    (void)obj;
}

__attribute__((optimize("O0")))
void printDerived(Derived* obj) {
    // Empty function for GDB to catch
    (void)obj;
}

__attribute__((optimize("O0")))
void printBasePtr(Base* obj) {
    // Empty function for GDB to catch
    (void)obj;
}

__attribute__((optimize("O0")))
void printContainer(Container* obj) {
    // Empty function for GDB to catch
    (void)obj;
}

__attribute__((optimize("O0")))
void printWithStdString(WithStdString* obj) {
    // Empty function for GDB to catch
    (void)obj;
}

int main() {
    BasicClass basic_instance;
    basic_instance.public_int = 123;
    basic_instance.public_float = 2.5f;
    basic_instance.public_bool = false;
    basic_instance.public_char = 'Z';
    basic_instance.color = BLUE;
    basic_instance.shape = Shape::TRIANGLE;

    Derived derived_instance;
    MostDerived most_derived_instance;

    Node node_a = {1, nullptr, nullptr, nullptr};
    Node node_b = {2, nullptr, nullptr, nullptr};
    node_a.self = &node_a;
    node_a.neighbour = &node_b;
    node_b.self = &node_b;
    node_b.neighbour = &node_a;

    Container container(&most_derived_instance, &node_a);

    WithStdString with_std_string;

    printBasicClass(&basic_instance);
    printDerived(&derived_instance);
    // Base pointer that really points at a MostDerived
    printBasePtr(&most_derived_instance);
    printContainer(&container);
    printWithStdString(&with_std_string);

    std::cout << "done" << std::endl;
    return 0;
}
