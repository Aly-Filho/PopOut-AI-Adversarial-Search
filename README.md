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

## :hourglass: Cronogram.

Week 1 - Foundation - Set up GitHub repo with .gitkeep files; Implement PopOut core rules (drop/pop).
Week 2 - Game Engine -  Complete win condition logic and create a basic CLI/GUI for Human vs Human play.
Week 3 - MCTS: Core - Implement the base Monte Carlo Tree Search algorithm and the UCT selection formula.
Week 4 - MCTS: Engine - Refine the simulation/playout phase and optimize tree traversal performance.
Week 5 - ID3: Logic - Develop the ID3 Decision Tree algorithm from scratch (handling Information Gain/Entropy).
Week 6 - ID3: Training - Process the provided datasets and train the classifier to recognize game states.
Week 7 - Integration -  Merge agents: Enable Human vs Computer and Computer vs Computer (MCTS vs DT) modes.
Week 8 - Analysis -  Conduct rigorous performance evaluations and document results in Jupyter Notebooks.
Week 9 - Final Review - Code cleanup, final documentation, and preparation for the group presentation.