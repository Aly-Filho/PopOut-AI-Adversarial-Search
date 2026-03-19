# PopOut-AI-Adversarial-Search
An Artificial Intelligence project focused on implementing adversarial search strategies and decision trees for the game PopOut (a Connect-4 variant). This repository includes a Monte Carlo Tree Search (MCTS) with UCT for game-playing and a custom ID3-based Decision Tree classifier developed from scratch.


## 📂 Project Structure

The organization below follows best practices for AI and Data Science projects:

```text
PopOut-AI-Project/
├── data/                   # Datasets for training and testing the Decision Tree
├── docs/                   # Assignment prompt and additional documentation
├── notebooks/              # Jupyter Notebooks for performance analysis and experiments
├── src/                    # Main source code
│   ├── game/               # PopOut game logic (rules, board, interface)
│   ├── mcts/               # Monte Carlo Tree Search and UCT implementation
│   ├── decision_tree/      # ID3 Algorithm developed from scratch
│   └── utils/              # Data preprocessing and helper functions
├── tests/                  # Unit tests for game rules and AI moves
├── .gitignore              # Files to be ignored by Git
├── README.md               # Project overview and instructions
└── requirements.txt        # Project dependencies
```

## ⏳ Project Roadmap (9-Week Schedule)

This schedule outlines the development phases to ensure the project is completed by the **May 17, 2026** deadline.

| Week | Phase | Key Tasks & Milestones |
| :--- | :--- | :--- |
| **Week 1** | **Foundation** | Repository setup with `.gitkeep`; Implement PopOut core rules (drop/pop logic). |
| **Week 2** | **Game Engine** | Complete win condition detection; Create CLI/GUI for Human vs Human play. |
| **Week 3** | **MCTS - Core** | Implement the basic Monte Carlo Tree Search structure and the UCT formula. |
| **Week 4** | **MCTS - Tuning** | Refine the simulation/playout phase and optimize tree traversal performance. |
| **Week 5** | **ID3 - Logic** | Develop the ID3 Decision Tree algorithm from scratch (Information Gain/Entropy). |
| **Week 6** | **ID3 - Training** | Data preprocessing; Train the classifier using the provided game state datasets. |
| **Week 7** | **Integration** | Merge all agents: Human vs AI and AI vs AI (MCTS vs Decision Tree). |
| **Week 8** | **Analysis** | Execute performance benchmarks; Document technical rigor in Jupyter Notebooks. |
| **Week 9** | **Final Review** | Code cleanup; Finalize README; Prepare for the group presentation. |