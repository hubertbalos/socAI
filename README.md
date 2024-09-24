# socAI - Python based simulator for Settlers of Catan

This project is an AI-driven simulation engine for Settlers of Catan, a popular strategy board game that mixes randomness, deep strategy, and player interaction. The goal was to explore how Monte Carlo Tree Search (MCTS) can be enhanced with domain-specific techniques like move pruning and virtual wins to create a smarter and more competitive AI. Built in Python, the engine uses parallel processing for faster simulations and includes a user-friendly interface created using Pygame for visualising player decision making.

![Catan Board](/images/game_gui.png)

## Installation

Clone this repository.

```bash
git clone https://github.com/hubertbalos/socAI
```

Create a virtual environment with Python 3.12 or higher and install the dependencies.

```bash
pip install -r requirements.txt
```

## Usage

You can edit simulation settings at the top of the ```simulator.py``` file.

```python
WINDOW_SIZE = (x, y)        # Pygame window size
USE_MULTIPROCESSING = True  # Multiprocessing (uses all CPU cores by default)
TOTAL_GAMES = 1000          # Total games to simulate
GAMELOG = False             # Print game events to terminal
DEBUG = False               # Print additional debugging information to terminal
SAVEGAME = False            # Turn on to view games using Pygame UI
```

Pro tip: turn off bottom 3 settings for best simulation performance.

Additionally, you can alter the player composition as you wish. The 3 available players to choose from can be seen below.

```python
"Player that takes random actions"
RandomPlayer(Colour="RED"), 

"Player that skews distribution of actions"
WeightedRandomPlayer(Colour="RED"),

"Player that uses Monte Carlo Tree Search to select actions"
MCTSPlayer(Colour="RED", Iterations=(int), Pruning=(bool), Reward=(bool)),
# Iterations: number of times 4-step MCTS cycle is repeated before selecting action
# Pruning: whether to use pruning heuristic or not
# Reward: whether to use reward heuristic or not
```

After you set and save simulation settings, you can run the simulation from the root of the repository.

```bash
python src/simulator.py
```