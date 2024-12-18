#!/usr/bin/env python3
import os

class NTM:
    def __init__(self, machine_file, output_file):
        # Initialize the machine with files and parameters
        self.machine_file = machine_file
        self.output_file = output_file
        self.states = []
        self.alphabet = []
        self.tape_alphabet = []
        self.start_state = ""
        self.accept_state = ""
        self.reject_state = ""
        self.transitions = {}
        self.input_string = []
        self.machine_name = ""
        self.max_steps = 1000
        self.machine_file = os.path.expanduser(self.machine_file)
        self.output_file = os.path.expanduser(self.output_file)
        self.load_machine()
        self.log = open(self.output_file, "w+")
        self.transition_count = 0  

    def __del__(self): 
        # Will close the log file when done
        if hasattr(self, "log") and self.log:
            self.log.close()

    def load_machine(self): 
        # Load the machine parameters from the provided file
        with open(self.machine_file, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            self.machine_name = lines[0]
            self.states = lines[1].split(',')
            self.alphabet = lines[2].split(',')
            self.tape_alphabet = lines[3].split(',')
            self.start_state = lines[4]
            self.accept_state = lines[5]
            self.reject_state = lines[6]
            self.transitions = {}
            for line in lines[7:-1]:
                state_from, symbol, state_to, tape_symbol, direction = line.split(',')
                if (state_from, symbol) not in self.transitions:
                    self.transitions[(state_from, symbol)] = []
                self.transitions[(state_from, symbol)].append((state_to, tape_symbol, direction))
            self.input_string = list(lines[-1])  # Input string is in the last line

    def print_configuration(self, state, tape, head_pos):
        left_of_head = ''.join(tape[:head_pos]) if head_pos > 0 else ""
        right_of_head = ''.join(tape[head_pos+1:]) if head_pos < len(tape) - 1 else ""
        head_char = tape[head_pos] if 0 <= head_pos < len(tape) else "_"
        return f"{left_of_head}[{state}]{head_char}{right_of_head}\n"

    def run(self):
        # Run the NTM with exhaustive exploration
        initial_tape = self.input_string + ["_"]
        initial_state = self.start_state
        initial_head_pos = 0
        
        # find all paths
        all_paths = []
        queue = [(initial_state, initial_tape, initial_head_pos, 1, [self.print_configuration(initial_state, initial_tape, initial_head_pos)])]
        steps = 0
        max_depth = 1

        while queue and steps < self.max_steps:
            current_state, current_tape, head_pos, depth, path_history = queue.pop(0)
            steps += 1
            max_depth = max(max_depth, depth)

            if depth > self.max_steps:
                break

            current_symbol = current_tape[head_pos] if 0 <= head_pos < len(current_tape) else "_"
            possible_transitions = self.transitions.get((current_state, current_symbol), [])

            # If no transitions it is rejected
            if not possible_transitions:
                current_path_config = {
                    'state': current_state,
                    'tape': current_tape.copy(),
                    'head_position': head_pos,
                    'depth': depth,
                    'history': path_history,
                    'result': 'Rejected'
                }
                all_paths.append(current_path_config)
                continue

            # looks into all possible transitions
            for next_state, write_symbol, direction in possible_transitions:
                new_tape = current_tape.copy()
                new_tape[head_pos] = write_symbol
                new_head_pos = head_pos

                #  head movement
                if direction == "R":
                    new_head_pos += 1
                    if new_head_pos >= len(new_tape): 
                        new_tape.append("_")
                elif direction == "L":
                    new_head_pos -= 1
                    if new_head_pos < 0:  
                        new_tape.insert(0, "_")
                        new_head_pos = 0

                # Check if reached accept or reject state
                if next_state == self.accept_state:
                    path_result = 'Accepted'
                elif next_state == self.reject_state:
                    path_result = 'Rejected'
                else:
                    path_result = None

                new_path_history = path_history + [self.print_configuration(next_state, new_tape, new_head_pos)]
                
                if path_result:
                    all_paths.append({
                        'state': next_state,
                        'tape': new_tape,
                        'head_position': new_head_pos,
                        'depth': depth + 1,
                        'history': new_path_history,
                        'result': path_result
                    })
                else:
                    queue.append((
                        next_state, 
                        new_tape, 
                        new_head_pos, 
                        depth + 1, 
                        new_path_history
                    ))

        accepted_paths = [p for p in all_paths if p.get('result') == 'Accepted']
        rejected_paths = [p for p in all_paths if p.get('result') == 'Rejected']
        
        self.log.seek(0)
        if accepted_paths:
            overall_result = "Accepted"
        elif rejected_paths:
            overall_result = "Rejected"
        else:
            overall_result = "Timed Out"

        summary = (
            f"Machine Name: {self.machine_name}\n"
            f"Input String: {''.join(self.input_string)}\n"
            f"Total Explored Paths: {len(all_paths)}\n"
            f"Overall Result: {overall_result}\n\n"
        )
        self.log.write(summary)

        for i, path in enumerate(all_paths, 1):
            self.log.write(f"Path {i}:\n")
            self.log.write(f"Result: {path.get('result', 'Incomplete')}\n")
            self.log.write(f"Depth: {path['depth']}\n")
            self.log.write(f"Configurations Explored: {len(path['history'])}\n")
            self.log.write("Configuration History:\n")
            self.log.write(''.join(path['history']))
            self.log.write("\n---\n")
        return overall_result, max_depth, len(all_paths), self.transition_count

def main():
    # Update paths for the machine and output files
    machine_file = "~/theory/project2/aortiz22/aortiz22/cases/test2_aortiz22.csv"
    output_file = "~/theory/project2/aortiz22/aortiz22/output/test2_output5_aortiz22.txt"
    ntm = NTM(machine_file, output_file)
    result, depth, paths, transition_count = ntm.run()    
    print(f"Successfully ran! Results are in the output file!")

if __name__ == "__main__":
    main()
