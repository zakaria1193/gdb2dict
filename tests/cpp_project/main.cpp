#include "types.hpp"
#include <iostream>
#include <string>
#include <vector>

// Initialize static members
int Base::static_base_public_int = 101;
int Base::static_base_protected_int = 102;
// int Base::static_base_private_int = 103; // Cannot access private static member directly

int Derived::static_derived_public_int = 201;
int Derived::static_derived_protected_int = 202;
// int Derived::static_derived_private_int = 203; // Cannot access private static member directly


// Inspection functions
__attribute__((optimize("O0")))
void inspectBasicObject(BasicClass* obj) {
    // Breakpoint here to inspect obj
    std::cout << "Inspecting BasicClass object at " << obj << std::endl;
}

__attribute__((optimize("O0")))
void inspectBaseObject(Base* obj) {
    // Breakpoint here to inspect obj
    std::cout << "Inspecting Base object at " << obj << std::endl;
}

__attribute__((optimize("O0")))
void inspectDerivedObject(Derived* obj) {
    // Breakpoint here to inspect obj
    std::cout << "Inspecting Derived object at " << obj << std::endl;
}

__attribute__((optimize("O0")))
void inspectBasePtrToDerived(Base* obj) {
    // Breakpoint here to inspect obj (should show Derived specific data)
    std::cout << "Inspecting Base* (pointing to Derived) at " << obj << std::endl;
}

__attribute__((optimize("O0")))
void inspectContainerObject(Container* obj) {
    // Breakpoint here to inspect obj
    std::cout << "Inspecting Container object at " << obj << std::endl;
}

__attribute__((optimize("O0")))
void inspectGlobalVariables() {
    // Breakpoint here to inspect global/static variables
    std::cout << "Inspecting global and static variables." << std::endl;
}


int main() {
    // Instantiate BasicClass
    BasicClass basic_instance;
    basic_instance.public_int = 123;
    basic_instance.public_float = 45.67f;
    basic_instance.public_bool = false;
    basic_instance.public_char = 'Z';
    basic_instance.public_string = "Modified Hello";

    // Instantiate Base
    Base base_instance;
    base_instance.base_public_int = 11;
    // base_instance.base_protected_int = 12; // Cannot access protected member
    // base_instance.base_private_int = 13; // Cannot access private member

    // Instantiate Derived
    Derived derived_instance;
    derived_instance.derived_public_int = 44;
    derived_instance.base_public_int = 400; // Accessing hidden Base member via Derived object

    // Polymorphism
    Base* base_ptr_to_base = &base_instance;
    Base* base_ptr_to_derived = &derived_instance;

    // Instantiate Contained for Container's reference member
    Contained contained_for_ref(77, "ReferencedContained");

    // Instantiate Container
    Container container_instance(contained_for_ref);
    container_instance.basic_obj.public_int = 999;
    container_instance.derived_obj.derived_public_int = 888;
    container_instance.contained_obj.data = "ContainerMainContained";
    if (container_instance.pointer_to_contained) {
        container_instance.pointer_to_contained->data = "ModifiedPointedTo";
    }
    if (container_instance.int_ptr) {
        *container_instance.int_ptr = 789;
    }
    container_instance.primitive_array[0] = 10;
    container_instance.object_array[0].data = "Elem0Modified";
    container_instance.color_member = BLUE;
    container_instance.shape_member = Shape::SQUARE;


    // Call inspection functions
    inspectBasicObject(&basic_instance);
    inspectBaseObject(&base_instance);
    inspectDerivedObject(&derived_instance);
    inspectBasePtrToDerived(base_ptr_to_derived); // Points to derived_instance
    inspectBaseObject(base_ptr_to_base);       // Points to base_instance
    inspectContainerObject(&container_instance);
    inspectGlobalVariables();


    std::cout << "Program finished." << std::endl;
    return 0;
}
