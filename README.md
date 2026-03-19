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