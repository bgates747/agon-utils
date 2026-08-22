NAME := invaders

AGONDEV_CONFIG ?= agondev-config
AGONDEV_PREFIX ?= $(shell command -v $(AGONDEV_CONFIG) >/dev/null 2>&1 && $(AGONDEV_CONFIG) --prefix)

TOOLBIN := $(AGONDEV_PREFIX)/bin
AS := $(TOOLBIN)/ez80-none-elf-as
LD := $(TOOLBIN)/ez80-none-elf-ld
SETNAME := $(TOOLBIN)/agondev-setname

BUILD_DIR := build
OBJ_DIR := $(BUILD_DIR)/obj
BIN_DIR := $(BUILD_DIR)/bin
LIST_DIR := $(BUILD_DIR)/listings

SOURCE := src/agon/main.asm
OBJECT := $(OBJ_DIR)/main.o
LISTING := $(LIST_DIR)/main.lst
LINKER_SCRIPT := linker/adl0.ld
MAP := $(BUILD_DIR)/$(NAME).map
BINARY := $(BIN_DIR)/$(NAME).bin

ASFLAGS := -march=ez80+full --fatal-warnings -alhms=$(abspath $(LISTING))
LDFLAGS := --fatal-warnings -Map=$(MAP) -T $(LINKER_SCRIPT) --oformat binary

.PHONY: all clean check-toolchain verify verify-source

all: verify

check-toolchain:
	@test -n "$(AGONDEV_PREFIX)" || { \
		echo "agondev not found: put agondev-config on PATH or set AGONDEV_PREFIX" >&2; \
		exit 1; \
	}
	@test -x "$(AS)" -a -x "$(LD)" -a -x "$(SETNAME)" || { \
		echo "AGONDEV_PREFIX does not name a complete agondev installation: $(AGONDEV_PREFIX)" >&2; \
		exit 1; \
	}

verify-source:
	sha256sum -c SOURCE.sha256

$(OBJECT): $(SOURCE) | check-toolchain
	mkdir -p $(OBJ_DIR) $(LIST_DIR)
	$(AS) $(ASFLAGS) $< -o $@

$(BINARY): $(OBJECT) $(LINKER_SCRIPT) | check-toolchain
	mkdir -p $(BIN_DIR)
	$(LD) $(LDFLAGS) -o $@ $(OBJECT)
	$(SETNAME) $@ $(NAME).bin >/dev/null

verify: verify-source $(BINARY)
	tools/validate_build.sh "$(BINARY)" "$(MAP)" "$(OBJECT)"

clean:
	$(RM) -r $(BUILD_DIR)
