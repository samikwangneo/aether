CONCEPTS = [
    # ── CMSC330 ────────────────────────────────────────────────────
    {"id": "c330-ocaml", "course_id": "cmsc330", "label": "OCaml", "mastery": 75},
    {"id": "c330-pattern-match", "course_id": "cmsc330", "label": "Pattern Matching", "mastery": 70},
    {"id": "c330-recursion", "course_id": "cmsc330", "label": "Recursion", "mastery": 80},
    {"id": "c330-regex", "course_id": "cmsc330", "label": "Regular Expressions", "mastery": 60},
    {"id": "c330-nfa-dfa", "course_id": "cmsc330", "label": "NFA / DFA", "mastery": 55},
    {"id": "c330-cfg", "course_id": "cmsc330", "label": "Context-Free Grammars", "mastery": 50},
    {"id": "c330-lambda", "course_id": "cmsc330", "label": "Lambda Calculus", "mastery": 40},
    {"id": "c330-rust", "course_id": "cmsc330", "label": "Rust", "mastery": 45},
    {"id": "c330-ownership", "course_id": "cmsc330", "label": "Ownership & Borrowing", "mastery": 40},
    {"id": "c330-type-inference", "course_id": "cmsc330", "label": "Type Inference", "mastery": 65},
    
    # ── MATH240 ────────────────────────────────────────────────────
    {"id": "m240-vectors", "course_id": "math240", "label": "Vectors", "mastery": 85},
    {"id": "m240-matrices", "course_id": "math240", "label": "Matrices", "mastery": 80},
    {"id": "m240-lin-transform", "course_id": "math240", "label": "Linear Transformations", "mastery": 60},
    {"id": "m240-eigenvalues", "course_id": "math240", "label": "Eigenvalues", "mastery": 45},
    {"id": "m240-eigenvectors", "course_id": "math240", "label": "Eigenvectors", "mastery": 45},
    {"id": "m240-diagonalization", "course_id": "math240", "label": "Diagonalization", "mastery": 35},
    {"id": "m240-vector-spaces", "course_id": "math240", "label": "Vector Spaces", "mastery": 70},
    {"id": "m240-basis-dim", "course_id": "math240", "label": "Basis & Dimension", "mastery": 65},
    {"id": "m240-null-col-space", "course_id": "math240", "label": "Null & Column Space", "mastery": 60},
    {"id": "m240-determinant", "course_id": "math240", "label": "Determinant", "mastery": 75},

    # ── CMSC216 ────────────────────────────────────────────────────
    {"id": "c216-c", "course_id": "cmsc216", "label": "C Programming Basics", "mastery": 80},
    {"id": "c216-bits", "course_id": "cmsc216", "label": "Bits & Data Rep", "mastery": 85},
    {"id": "c216-mem", "course_id": "cmsc216", "label": "Memory Management", "mastery": 70},
    {"id": "c216-asm", "course_id": "cmsc216", "label": "x86 Assembly", "mastery": 50},
    {"id": "c216-proc", "course_id": "cmsc216", "label": "Processes & Fork", "mastery": 65},
    {"id": "c216-syscall", "course_id": "cmsc216", "label": "System Calls", "mastery": 60},
    {"id": "c216-link", "course_id": "cmsc216", "label": "Linking & Loading", "mastery": 55},
    {"id": "c216-vm", "course_id": "cmsc216", "label": "Virtual Memory", "mastery": 40},
    {"id": "c216-cache", "course_id": "cmsc216", "label": "Cache Hierarchy", "mastery": 45},

    # ── CMSC250 ────────────────────────────────────────────────────
    {"id": "c250-proplogic", "course_id": "cmsc250", "label": "Propositional Logic", "mastery": 80},
    {"id": "c250-predlogic", "course_id": "cmsc250", "label": "Predicate Logic", "mastery": 75},
    {"id": "c250-proofs", "course_id": "cmsc250", "label": "Proof Techniques", "mastery": 70},
    {"id": "c250-sets", "course_id": "cmsc250", "label": "Set Theory", "mastery": 85},
    {"id": "c250-relations", "course_id": "cmsc250", "label": "Relations & Functions", "mastery": 70},
    {"id": "c250-induction", "course_id": "cmsc250", "label": "Mathematical Induction", "mastery": 65},
    {"id": "c250-recurrences", "course_id": "cmsc250", "label": "Recurrences", "mastery": 60},
    {"id": "c250-combinatorics", "course_id": "cmsc250", "label": "Combinatorics", "mastery": 55},
    {"id": "c250-numtheory", "course_id": "cmsc250", "label": "Number Theory", "mastery": 50},
    {"id": "c250-graphs", "course_id": "cmsc250", "label": "Graph Theory", "mastery": 50},

    # ── CMSC351 ────────────────────────────────────────────────────
    {"id": "c351-bigo", "course_id": "cmsc351", "label": "Asymptotic Analysis", "mastery": 75},
    {"id": "c351-dc", "course_id": "cmsc351", "label": "Divide & Conquer", "mastery": 70},
    {"id": "c351-sort", "course_id": "cmsc351", "label": "Sorting Algorithms", "mastery": 65},
    {"id": "c351-greedy", "course_id": "cmsc351", "label": "Greedy Algorithms", "mastery": 60},
    {"id": "c351-dp", "course_id": "cmsc351", "label": "Dynamic Programming", "mastery": 55},
    {"id": "c351-graphs", "course_id": "cmsc351", "label": "Graph Algorithms", "mastery": 50},
    {"id": "c351-shortpath", "course_id": "cmsc351", "label": "Shortest Paths", "mastery": 45},
    {"id": "c351-mst", "course_id": "cmsc351", "label": "Minimum Spanning Trees", "mastery": 45},
    {"id": "c351-np", "course_id": "cmsc351", "label": "NP-Completeness", "mastery": 30},

    # ── CMSC320 / DATA320 ──────────────────────────────────────────
    {"id": "c320-pandas", "course_id": "cmsc320", "label": "Pandas & Data Cleaning", "mastery": 60},
    {"id": "c320-stats", "course_id": "cmsc320", "label": "Probability & Hypothesis Testing", "mastery": 50},
    {"id": "c320-ml-intro", "course_id": "cmsc320", "label": "Applied Machine Learning", "mastery": 45},

    # ── BMGT230 ────────────────────────────────────────────────────
    {"id": "b230-prob", "course_id": "bmgt230", "label": "Business Probability", "mastery": 65},
    {"id": "b230-hyp-test", "course_id": "bmgt230", "label": "Hypothesis Testing", "mastery": 55},
    {"id": "b230-regression", "course_id": "bmgt230", "label": "Linear Regression", "mastery": 50},

    # ── ECON306 ────────────────────────────────────────────────────
    {"id": "e306-cost", "course_id": "econ306", "label": "Cost Functions", "mastery": 70},
    {"id": "e306-game", "course_id": "econ306", "label": "Advanced Game Theory", "mastery": 65},
    {"id": "e306-externality", "course_id": "econ306", "label": "Advanced Externalities", "mastery": 60},

    # ── CMSC471 ────────────────────────────────────────────────────
    {"id": "c471-vis", "course_id": "cmsc471", "label": "Visual Encodings", "mastery": 50},
    {"id": "c471-interact", "course_id": "cmsc471", "label": "Interactive D3/Web", "mastery": 40},
    {"id": "c471-network", "course_id": "cmsc471", "label": "Network & Trees Vis", "mastery": 45},

    # ── CMSC422 ────────────────────────────────────────────────────
    {"id": "c422-sup", "course_id": "cmsc422", "label": "Supervised Learning", "mastery": 55},
    {"id": "c422-unsup", "course_id": "cmsc422", "label": "Unsupervised Learning", "mastery": 50},
    {"id": "c422-nn", "course_id": "cmsc422", "label": "Deep Neural Networks", "mastery": 40},
    {"id": "c422-pca", "course_id": "cmsc422", "label": "PCA & Dimensionality", "mastery": 45},

    # ── CMSC421 ────────────────────────────────────────────────────
    {"id": "c421-search", "course_id": "cmsc421", "label": "State Space Search", "mastery": 60},
    {"id": "c421-kr", "course_id": "cmsc421", "label": "Knowledge Rep & Logic", "mastery": 55},
    {"id": "c421-bayes", "course_id": "cmsc421", "label": "Bayesian Inference", "mastery": 45},

    # ── MATH401 ────────────────────────────────────────────────────
    {"id": "m401-svd", "course_id": "math401", "label": "Singular Value Decomposition", "mastery": 30},
    {"id": "m401-markov", "course_id": "math401", "label": "Markov Chains", "mastery": 35},
    {"id": "m401-quantum", "course_id": "math401", "label": "Quantum Bits", "mastery": 20},

    # ── CMSC470 ────────────────────────────────────────────────────
    {"id": "c470-ngram", "course_id": "cmsc470", "label": "N-Grams & Semantics", "mastery": 50},
    {"id": "c470-cfg", "course_id": "cmsc470", "label": "NLP Parsing & CFG", "mastery": 45},
    {"id": "c470-transformer", "course_id": "cmsc470", "label": "Transformers & Attention", "mastery": 35},
]