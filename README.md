# Settlers of Catan - AI

A Python framework of the classic board game "Settlers of Catan". The project aims to develop an AI player for the popular board game “Settlers of
Catan” using machine learning. Unlike traditional board games like Chess or Go,
where every player has complete access to all the information needed to make
decisions, Settlers of Catan is an imperfect information and non-deterministic game
involving a complex trading system where players can trade resources between
themselves. This means players must make strategic decisions based on limited
information and probabilistic outcomes.

![Catan Board](/images/game_gui.png)

## Overview

```renderer.py``` - Renders the state of the game to the screen using pygame.

```game.py``` - The class containing the main game loop and game logic.

```board.py``` - The class which contains the board state and is responsible for any changes to that state.

```components.py``` - Contains the Hextile, Vertex and Edge class definitions which define the board.

```hexlib.py``` - Library implementing hex coordinate system functionality.

```player.py``` - The player classes containing the player scores and state along with implementing the player decision making mechanisms.

## Usage

Run using:
```python
python main.py
```
