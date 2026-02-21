# Stockfish Chess Python
**⚠️ Requirements:** You must have [Stockfish.exe](https://stockfishchess.org/download/) in the folder to play!

https://github.com/rizwanahmed109-beep/stockfish-chess-python/blob/main/screenshots/Screenshot%202026-02-21%20044917.png

## Description
A fully functional, graphical 2D chess game built using Python, Pygame, and the world-class Stockfish engine. Stockfish is a free and open-source chess engine, which has won all main events of the Top Chess Engine Championship (TCEC) since 2020. 

The game tracks your performance with an ELO rating system, provides quality-of-life features like undoing moves, highlighting legal destinations, and offers dynamic pawn promotion overlays.

## Features
* **Unbeatable AI (Stockfish):** Play against 4 difficulty levels (Easy, Medium, Hard, Unbeatable) powered by the Stockfish engine.
* **Dynamic ELO Tracking:** The game calculates and saves both the Player and AI ELO ratings in a local `elo.json` file after every match.
* **Takebacks / Undo Move:** Made a blunder? Press `Backspace` to seamlessly rewind the game state (undoing both the AI's last move and your last move).
* **Audio Feedback:** Authentic `.wav` sound effects trigger dynamically for standard moves, piece captures, and when a king is placed in check.
* **Graphical Pawn Promotion:** A sleek, centered UI overlay pauses the game and lets you click to choose your promotion piece (Queen, Rook, Bishop, Knight).
* **Responsive Window:** The board calculates its size dynamically based on the window height, ensuring it always fits your screen perfectly.

## Prerequisites
Before running the game, ensure you have Python 3.x installed along with the required Python libraries. The project relies on the `python-chess` library for move generation and validation.

You can install all dependencies via pip:
`pip install pygame chess stockfish`

## Installation & Setup

1. **Clone or Download the Repository**
   Download the project files to your local machine.
   
2. **Download Stockfish**
   You must download the official Stockfish executable for your operating system (available at [stockfishchess.org](https://stockfishchess.org/)). 
   * Extract the `.exe` file (or binary for Mac/Linux).
   * Rename the executable to `stockfish.exe` (or update the path in `chess_ai.py`).
   * Place it directly in the root folder of this project alongside `chess_ai.py`.

3. **Asset Folders**
   Ensure your project folder contains the following structure for visual and audio assets:
   ```text
   📁 Project Root
   ├── 📄 chess_ai.py
   ├── 📄 stockfish.exe
   └── 📁 assets
       ├── 📁 pieces (e.g., white_pawn.png, black_knight.png)
       └── 📁 sounds (move.wav, capture.wav, check.wav)

How to Play
Run the main Python script to start the game:
python chess_ai.py

Controls:

Mouse Left-Click: Select a piece and click a legal highlighted square to move.

Number Keys (1–4): Change AI Difficulty (1 = Easy, 2 = Medium, 3 = Hard, 4 = Unbeatable).

Backspace / Left Arrow: Undo your last move (and the AI's response).

R: Reset the board and start a new game.

Q: Quit the application safely.

Acknowledgements
The chess engine is powered by Stockfish.

Board logic and state validation handled by python-chess.

Graphical interface rendered with Pygame.

## 🛠️ Troubleshooting

### "FileNotFoundError: [WinError 2] The system cannot find the file specified"
If you see this error, it means Python cannot find `stockfish.exe`.
1. **Check the filename:** Ensure your file is named exactly `stockfish.exe` and not something like `stockfish-windows-x86-64-avx2.exe`.
2. **Check the folder:** The file must be in the same folder as `chess_ai.py`.
3. **Check the path in code:** In `chess_ai.py`, ensure the initialization line looks like this:
   `self.engine = stockfish.Stockfish(path="./stockfish.exe")`

### "AttributeError: 'Stockfish' object has no attribute 'quit'"
This happens if you are using an older version of the Stockfish wrapper. The current script uses `del self.engine` to safely close the process. Ensure you have the latest version by running:
`pip install --upgrade stockfish`

### Pieces are not appearing
Make sure you have an `assets` folder with a `pieces` subfolder containing the `.png` files. The game expects names like `white_pawn.png` and `black_king.png`.
