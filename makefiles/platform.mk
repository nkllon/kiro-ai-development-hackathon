# Beast Mode Framework - Platform Detection
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

ifeq ($(UNAME_S),Darwin)
    PLATFORM := macos
endif
ifeq ($(UNAME_S),Linux)
    PLATFORM := linux
endif
