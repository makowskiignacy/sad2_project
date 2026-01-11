import random
import re

def load_bnet(filepath):
    targets = []
    expressions_dict = {}
    
    # Read the file and parse defined target nodes and their rules
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ',' not in line:
                continue
            
            target, expr = line.split(',', 1)
            target = target.strip()
            if target.lower() == "targets":
                 continue
            
            targets.append(target)
            expressions_dict[target] = expr.strip()
            
    # Identify input nodes (nodes mentioned in rules but not defined as targets)
    all_referenced_names = set()
    # Simple regex to find words (potential node names) in expressions
    word_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
    for expr in expressions_dict.values():
        all_referenced_names.update(word_pattern.findall(expr))
    
    # Filter out keywords and defined targets
    keywords = {"not", "and", "or", "True", "False"}
    input_nodes = [name for name in all_referenced_names if name not in targets and name not in keywords]
    
    # Add input nodes to the network. They will stay at their initial value (next = self).
    node_names = targets + input_nodes
    for name in input_nodes:
        expressions_dict[name] = name
        
    # Map node names to their index (0, 1, 2...) for easier processing
    name_to_idx = {name: i for i, name in enumerate(node_names)}
    
    parents_map = {}
    function_map = {}
    
    # Convert each rule into a Python lambda function
    for i, name in enumerate(node_names):
        expr_str = expressions_dict[name]
        
        # Identify which nodes (parents) are mentioned in the rule
        found_parents = []
        for other_name in node_names:
             if re.search(r'\b' + re.escape(other_name) + r'\b', expr_str):
                 found_parents.append(other_name)
        
        # Sort parents to match the order in the 'bits' input of the generated function
        found_parents.sort(key=lambda x: name_to_idx[x])
        parent_indices = [name_to_idx[p] for p in found_parents]
        parents_map[i] = parent_indices
        
        # Prepare the expression for Python evaluation:
        # Replace BNet symbols (!, &, |) with Python keywords (not, and, or)
        py_expr = expr_str.replace('!', ' not ').replace('&', ' and ').replace('|', ' or ')
        
        # Replace node names in the rule with access to an input list (bits[0], bits[1]...)
        for k, p_name in enumerate(found_parents):
            # Using regex to ensure we only replace whole names
            py_expr = re.sub(r'\b' + re.escape(p_name) + r'\b', f"bits[{k}]", py_expr)

        # Create a small function that evaluates this rule
        # 'bits' is a list of the parent nodes' current values (0 or 1)
        function_map[i] = lambda bits, code=py_expr: int(eval(code, {"__builtins__":{}}, {"bits": bits}))
            
    return (parents_map, function_map, expressions_dict), node_names


def update_sync(state, parents, functions):
    new_state = state[:]
    for i in range(len(state)):
        if i in functions:
            parent_values = [state[p] for p in parents[i]]
            new_state[i] = int(bool(functions[i](parent_values)))
    return new_state

def update_async(state, parents, functions):
    new_state = state[:]
    i = random.randrange(len(state))
    if i in functions:
        parent_values = [state[p] for p in parents[i]]
        new_state[i] = int(bool(functions[i](parent_values)))
    return new_state

def simulate_sync(network, steps):
    parents, functions, _ = network
    state = [random.randint(0, 1) for _ in range(len(parents))]
    trajectory = [state[:]]
    for _ in range(steps):
        state = update_sync(state, parents, functions)
        trajectory.append(state[:])
    return trajectory

def simulate_async(network, steps):
    parents, functions, _ = network
    state = [random.randint(0, 1) for _ in range(len(parents))]
    trajectory = [state[:]]
    for _ in range(steps):
        state = update_async(state, parents, functions)
        trajectory.append(state[:])
    return trajectory

def save_bnf(filename, trajectories, node_names):
    if not trajectories: 
        return
    
    # Flatten if we have a list of trajectories
    if isinstance(trajectories[0][0], list):
        data_to_save = [state for traj in trajectories for state in traj]
    else:
        data_to_save = trajectories
        
    num_nodes = len(node_names)
    num_steps = len(data_to_save)
    
    with open(filename, "w") as f:
        # Write header (S0, S1, S2...)
        header = ["Gene"] + [f"S{t}" for t in range(num_steps)]
        f.write("\t".join(header) + "\n")
        
        # Write state for each node row by row
        for i, name in enumerate(node_names):
            row = [name] + [str(state[i]) for state in data_to_save]
            f.write("\t".join(row) + "\n")
