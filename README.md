# S1mple CPU Dev Tools

This project's goal is to develop an integrated dev tool package for S1mple CPU with:
1) Assembler
2) Emulator
3) Serial Monitor
4) Microcode Merger
---

# Microcode Merger
A tool to merge ISA data, ROM, Control Word Settings into a single format.
The format is based on JSON.

# Assembler
Desired specifications:
- Default base 16 (use '0d' prefix for decimal)
- Pointer Prefix '@'
- Line-by-line processing (TODO: find a workaround for multiline Define)

Roadmap:
1) Basic Assembly
2) Define
3) Pointers
4) Labels