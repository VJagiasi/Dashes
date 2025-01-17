#!/usr/bin/env python3
import sys

VALID_CMDS = {'*', '+', '-', '>', '<', '[', ']'}

def parse_dashes_code(raw_code: str) -> list[str]:
    """
    Parse the raw code string and return a list of valid Dashes commands.
    Ignores anything that's not in the set of valid commands.
    Also removes inline comments introduced by '#' or '//'.
    """

    program = []

    # Split into lines so we can handle inline comment symbols (# and //)
    for line in raw_code.splitlines():
        # Remove everything after '#' on this line
        line = line.split('#', 1)[0]
        # Remove everything after '//' on this line
        line = line.split('//', 1)[0]
        # Now gather all valid Dashes commands
        for ch in line:
            if ch in VALID_CMDS:
                program.append(ch)

    return program

def run_dashes(program: list[str], debug: bool = False) -> list[int]:
    """
    Interpret and run a list of Dashes commands on a virtual Dots machine.
    Returns the final state of the 100 memory slots.
    If debug=True, prints step-by-step execution details.
    Additionally, each time slot3 is decremented, we display a 'progress' line.
    """

    # --- 1) Precompute bracket matching for loops
    stack = []
    bracket_map = {}
    for i, cmd in enumerate(program):
        if cmd == '[':
            stack.append(i)
        elif cmd == ']':
            start = stack.pop()
            bracket_map[start] = i
            bracket_map[i] = start

    # --- 2) Set up the Dots machine
    memory = [0] * 100  # 100 contiguous slots, unbounded in Python
    mc = 0              # "memory counter" (0..99) with wraparound
    pc = 0              # program counter (index into 'program')
    iteration_count = 0 # how many times we've decremented slot3

    # --- 3) Interpret the program
    while pc < len(program):
        cmd = program[pc]

        if debug:
            print(f"PC={pc:3d}, CMD={cmd!r}, MC={mc:3d}, M[MC]={memory[mc]}")

        if cmd == '*':
            # Set current slot to 1
            memory[mc] = 1

        elif cmd == '+':
            # Increment current slot
            memory[mc] += 1

        elif cmd == '-':
            # Decrement current slot
            old_val = memory[mc]
            memory[mc] -= 1

            # If we just decremented slot3, show a progress message
            # (only if the old value was higher, i.e. we truly decremented)
            if mc == 3 and old_val > memory[mc]:
                iteration_count += 1
                print(f"[Iteration {iteration_count}] Decremented slot3 from {old_val} to {memory[mc]} "
                      f"--> slot0={memory[0]}, slot1={memory[1]}, slot2={memory[2]}, slot3={memory[3]}")

        elif cmd == '>':
            # Move MC right by 1 (wrap around 100)
            mc = (mc + 1) % 100

        elif cmd == '<':
            # Move MC left by 1 (wrap around 100)
            mc = (mc - 1) % 100

        elif cmd == '[':
            # Loop begin: if current cell == 0, jump to matching ']'
            if memory[mc] == 0:
                pc = bracket_map[pc]

        elif cmd == ']':
            # Loop end: if current cell != 0, jump back to matching '['
            if memory[mc] != 0:
                pc = bracket_map[pc]

        pc += 1

    return memory

def main():
    """
    Usage:
      python dashes.py ">*++..."          # one-liner code from CLI
      python dashes.py - < program.dash   # code from a file or stdin
    """
    # If user gave code on the command line,
    # we merge all args into one string as the code.
    if len(sys.argv) > 1 and sys.argv[1].strip() != "-":
        raw_code = " ".join(sys.argv[1:])
    else:
        # Otherwise read from stdin
        raw_code = sys.stdin.read()


    # Parse code (remove comments, etc.)
    program = parse_dashes_code(raw_code)

    # Run the code
    memory = run_dashes(program, debug=False)

    # Print final memory state
    print("\nFinal memory state:", memory)

if __name__ == "__main__":
    main()