NAME := invaders

AGONDEV_CONFIG ?= agondev-config
AGONDEV_PREFIX ?= $(shell command -v $(AGONDEV_CONFIG) >/dev/null 2>&1 && $(AGONDEV_CONFIG) --prefix)

TOOLBIN := $(AGONDEV_PREFIX)/bin
AS := $(TOOLBIN)/ez80-none-elf-as
LD := $(TOOLBIN)/ez80-none-elf-ld
SETNAME := $(TOOLBIN)/agondev-setname
OBJCOPY := $(TOOLBIN)/ez80-none-elf-objcopy

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

ASMX ?= asmx
REFERENCE_DIR := $(BUILD_DIR)/reference
REFERENCE_ROM := $(REFERENCE_DIR)/invaders.rom
REFERENCE_LISTING := $(REFERENCE_DIR)/invaders.lst

CORE_PROOF_NAME := core-proof
CORE_PROOF_SOURCE := src/probes/original_core_proof.asm
CORE_PROOF_OBJECT := $(OBJ_DIR)/original_core_proof.o
CORE_PROOF_LISTING := $(LIST_DIR)/original_core_proof.lst
CORE_PROOF_LINKER_SCRIPT := linker/core-proof.ld
CORE_PROOF_MAP := $(BUILD_DIR)/$(CORE_PROOF_NAME).map
CORE_PROOF_BINARY := $(BIN_DIR)/$(CORE_PROOF_NAME).bin

ADAPTER_PROOF_NAME := adapter-proof
ADAPTER_PROOF_SOURCE := src/probes/adapter_proof.asm
ADAPTER_PROOF_OBJECT := $(OBJ_DIR)/adapter_proof.o
ADAPTER_PROOF_LISTING := $(LIST_DIR)/adapter_proof.lst
ADAPTER_PROOF_LINKER_SCRIPT := linker/adapter-proof.ld
ADAPTER_PROOF_MAP := $(BUILD_DIR)/$(ADAPTER_PROOF_NAME).map
ADAPTER_PROOF_BINARY := $(BIN_DIR)/$(ADAPTER_PROOF_NAME).bin

TRANSLATION_PROOF_SOURCE := src/agon/original/translation_proof.asm
TRANSLATION_PROOF_OBJECT := $(OBJ_DIR)/translation_proof.o
TRANSLATION_PROOF_LISTING := $(LIST_DIR)/translation_proof.lst
TRANSLATION_PROOF_BINARY := $(BIN_DIR)/translation-proof.bin

GPIO_PROBE_NAME := gpio-raster
GPIO_PROBE_SOURCE := src/probes/gpio_raster.asm
GPIO_PROBE_OBJECT := $(OBJ_DIR)/gpio_raster.o
GPIO_PROBE_LISTING := $(LIST_DIR)/gpio_raster.lst
GPIO_PROBE_MAP := $(BUILD_DIR)/$(GPIO_PROBE_NAME).map
GPIO_PROBE_BINARY := $(BIN_DIR)/$(GPIO_PROBE_NAME).bin
GPIO_DRIVER_LIBRARY := third_party/ez80-framebuffer-agon/gpiovideodriver_static_0xb8000.lib

ASFLAGS := -march=ez80+full --fatal-warnings -alhms=$(abspath $(LISTING))
LDFLAGS := --fatal-warnings -Map=$(MAP) -T $(LINKER_SCRIPT) --oformat binary

.PHONY: adapter-proof all clean check-toolchain core-proof gpio-probe reference-rom translation-proof verify verify-source

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

$(REFERENCE_ROM): src/invaders.asm
	mkdir -p $(REFERENCE_DIR)
	@command -v "$(ASMX)" >/dev/null 2>&1 || { \
		echo "ASMX is required only to build the original 8080 reference ROM; set ASMX=/path/to/asmx" >&2; \
		exit 1; \
	}
	$(ASMX) -e -w -b 0 -l $(REFERENCE_LISTING) -o $@ -- $<
	@printf '%s  %s\n' \
		7446e0994117596de5206519e693f8875ff3455e0be121d5cb975c3bcc224c4e \
		$@ | sha256sum -c -

reference-rom: verify-source $(REFERENCE_ROM)

$(CORE_PROOF_OBJECT): $(CORE_PROOF_SOURCE) $(REFERENCE_ROM) | check-toolchain
	mkdir -p $(OBJ_DIR) $(LIST_DIR)
	$(AS) -march=ez80+full --fatal-warnings \
		-alhms=$(abspath $(CORE_PROOF_LISTING)) $< -o $@

$(CORE_PROOF_BINARY): $(CORE_PROOF_OBJECT) $(CORE_PROOF_LINKER_SCRIPT) | check-toolchain
	mkdir -p $(BIN_DIR)
	$(LD) --fatal-warnings -Map=$(CORE_PROOF_MAP) -T $(CORE_PROOF_LINKER_SCRIPT) \
		--oformat binary -o $@ $(CORE_PROOF_OBJECT)
	$(SETNAME) $@ $(CORE_PROOF_NAME).bin >/dev/null

core-proof: verify-source $(CORE_PROOF_BINARY)
	tools/validate_core_proof.sh "$(CORE_PROOF_BINARY)" \
		"$(CORE_PROOF_MAP)" "$(CORE_PROOF_OBJECT)" "$(REFERENCE_ROM)" \
		"$(CORE_PROOF_LISTING)"

$(ADAPTER_PROOF_OBJECT): $(ADAPTER_PROOF_SOURCE) $(REFERENCE_ROM) | check-toolchain
	mkdir -p $(OBJ_DIR) $(LIST_DIR)
	$(AS) -march=ez80+full --fatal-warnings \
		-alhms=$(abspath $(ADAPTER_PROOF_LISTING)) $< -o $@

$(ADAPTER_PROOF_BINARY): $(ADAPTER_PROOF_OBJECT) $(ADAPTER_PROOF_LINKER_SCRIPT) | check-toolchain
	mkdir -p $(BIN_DIR)
	$(LD) --fatal-warnings -Map=$(ADAPTER_PROOF_MAP) -T $(ADAPTER_PROOF_LINKER_SCRIPT) \
		--oformat binary -o $@ $(ADAPTER_PROOF_OBJECT)
	$(SETNAME) $@ $(ADAPTER_PROOF_NAME).bin >/dev/null

adapter-proof: verify-source $(ADAPTER_PROOF_BINARY)
	tools/validate_adapter_proof.sh "$(ADAPTER_PROOF_BINARY)" \
		"$(ADAPTER_PROOF_MAP)" "$(ADAPTER_PROOF_OBJECT)" "$(REFERENCE_ROM)" \
		"$(ADAPTER_PROOF_LISTING)"

$(TRANSLATION_PROOF_OBJECT): $(TRANSLATION_PROOF_SOURCE) | check-toolchain
	mkdir -p $(OBJ_DIR) $(LIST_DIR)
	$(AS) -march=ez80+full --fatal-warnings \
		-alhms=$(abspath $(TRANSLATION_PROOF_LISTING)) $< -o $@

$(TRANSLATION_PROOF_BINARY): $(TRANSLATION_PROOF_OBJECT) | check-toolchain
	mkdir -p $(BIN_DIR)
	$(OBJCOPY) -O binary -j .text $< $@

translation-proof: verify-source $(REFERENCE_ROM) $(TRANSLATION_PROOF_BINARY)
	tools/validate_translation_proof.sh "$(TRANSLATION_PROOF_BINARY)" \
		"$(REFERENCE_ROM)" "$(TRANSLATION_PROOF_LISTING)"

$(GPIO_PROBE_OBJECT): $(GPIO_PROBE_SOURCE) $(GPIO_DRIVER_LIBRARY) | check-toolchain
	mkdir -p $(OBJ_DIR) $(LIST_DIR)
	$(AS) -march=ez80+full --fatal-warnings \
		-alhms=$(abspath $(GPIO_PROBE_LISTING)) $< -o $@

$(GPIO_PROBE_BINARY): $(GPIO_PROBE_OBJECT) $(LINKER_SCRIPT) | check-toolchain
	mkdir -p $(BIN_DIR)
	$(LD) --fatal-warnings -Map=$(GPIO_PROBE_MAP) -T $(LINKER_SCRIPT) \
		--oformat binary -o $@ $(GPIO_PROBE_OBJECT)
	$(SETNAME) $@ $(GPIO_PROBE_NAME).bin >/dev/null

gpio-probe: verify-source $(GPIO_PROBE_BINARY)
	tools/validate_gpio_probe.sh "$(GPIO_PROBE_BINARY)" \
		"$(GPIO_PROBE_MAP)" "$(GPIO_PROBE_OBJECT)" \
		"$(GPIO_DRIVER_LIBRARY)"

verify: verify-source $(BINARY)
	tools/validate_build.sh "$(BINARY)" "$(MAP)" "$(OBJECT)"

clean:
	$(RM) -r $(BUILD_DIR)
