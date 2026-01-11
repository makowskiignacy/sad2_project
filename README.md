# Statistical Data Analysis 2 - Final Project

## Project Description
Investigation of how the type and amount of data describing network dynamics influence the accuracy of inferring network structure within the framework of Bayesian networks using BNFinder2.

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
