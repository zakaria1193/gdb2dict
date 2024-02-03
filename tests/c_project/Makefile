CC = gcc
CFLAGS = -g -Wall -O1

TARGET = test_program
SOURCES = main.c
HEADERS = types.h

all: $(TARGET)

$(TARGET): $(SOURCES) $(HEADERS)
	$(CC) $(CFLAGS) -o $@ $(SOURCES)

clean:
	rm -f $(TARGET)
