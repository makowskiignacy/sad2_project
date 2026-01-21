# Statistical Data Analysis 2 - Final Project

## Project Description
Investigation of how the type and amount of data describing network dynamics influence the accuracy of inferring network structure within the framework of Bayesian networks using BNFinder2.

## Project report
Details on the experimental setup and results. Currently, the link below points to an Overleaf project under construction.
[Project report](https://www.overleaf.com/read/ttjxjstvmmcq#94a393)

## Task Allocation

### Data Generation - Part 1
**Assignee:** Michal-Zgieb

1. **Construct Boolean Networks:**
   - Sizes: 5 to 16 nodes (specifically 5, 16, and some intermediate sizes).
   - Constraints: Max 3 parents per node, random Boolean functions.
2. **Simulate Trajectories:**
   - Modes: Synchronous and Asynchronous.
   - Variations to cover:
     - Proportion of transient vs. attractor states.
     - Sampling frequency (steps between sampled states).
     - Overall size (number/length of trajectories).

### Data Generation - Part 2 (Biological Model)
**Assignee:** makowskiignacy

1. **Model Selection:**
   - Select a validated Boolean network model from [Biodivine repository](https://github.com/sybila/biodivine-boolean-models).
   - **Selected Model:** Mammalian Cell Cycle (Fauré et al., 2006).
   - Constraint: Size ≤ 16 nodes (Model has 10 nodes).
2. **Dataset Generation:**
   - Generate appropriate datasets for network inference based on insights from Part 1.

### BN Inference (BNFinder) & Evaluation - Part 1
**Assignee:** veranika-k

1. **Infer Dynamic Bayesian Networks:**
   - Tool: BNFinder2.
   - Scoring functions: MDL and BDe.
2. **Evaluate Accuracy:**
   - Compare reconstructed networks against ground truth.
   - Use at least two structure-based graph distance measures.
   - Analyze impact of dataset characteristics and scoring functions.

### BN Inference (BNFinder) & Evaluation - Part 2 (Biological Model):**
**Assignee:** AncientG7eek
1. **Infer a Dynamic Network:**
   - Use BNFinder2 with chosen scoring function.
2. **Evaluate:**
   - Evaluate reconstruction accuracy against the validated biological model.

## How to Run

### Prerequisites
- Python 3
- `pyboolnet` library (required for Part 1)
  ```bash
  pip install git+https://github.com/hklarner/pyboolnet
  # Note: Ensure you have git installed.
  ```

### Data Generation

#### Part 1: Random Boolean Networks
Generates random Boolean networks and simulates trajectories with varying parameters.

- **Command:**
  ```bash
  python3 zad1-2.py
  ```
- **Output:**
  - Data files in `BN_data/` directory (e.g., `nodes8_steps20_sample1_ntraj10_sync.data`).
  - `report.txt`: Contains structure of generated networks and analysis of attractors.

#### Part 2: Biological Models
Downloads validated biological models (≤ 16 nodes) and generates trajectories.

- **Command:**
  ```bash
  python3 generate_trajectories.py
  ```
- **Output:**
  - Subdirectories in `BN_data/` for each downloaded model (e.g., `BN_data/099_YEAST-HYPHAL-TRANSITION/`).
  - `.data` files inside each model folder containing the trajectories.

### Checking Results
1. **Check Commands:** Ensure scripts run without errors. `zad1-2.py` may take some time as it generates multiple datasets.
2. **Check Data:**
   - Verify `BN_data/` exists and contains output files.
   - Inspect `report.txt` to verify network structures were generated and attractors found.
   - The `.data` files should follow the BNFinder format (Time series data).