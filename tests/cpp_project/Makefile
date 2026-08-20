CXX = g++
CXXFLAGS = -g -Wall -O0 -std=c++11

TARGET = test_program_cpp
SOURCES = main.cpp
HEADERS = types.hpp

all: $(TARGET)

$(TARGET): $(SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $@ $(SOURCES)

clean:
	rm -f $(TARGET)
