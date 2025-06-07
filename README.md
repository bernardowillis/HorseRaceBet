# Horse Race Betting Game

**Project Members:** Robbe de Guytenaer, Bernardo José Willis Lozano

## Description

The Horse Race Betting Game is a simple betting simulation built with Python and Kivy. Players start with a balance and can add more, place bets on one of six horses, and watch the race unfold in real time. The goal is to win as much virtual money as possible by correctly predicting the winning horse. Even if the game is not used in real-life virtual casino games, it can be used for other options like party games. This project serves both as an educational tool for learning Python, MVC patterns and Kivy, and as an entertaining mini game.

## Platform and Motivation

**Chosen Platform:** Kivy (Python)

We chose Kivy because:

* It has the option to build cross-platform graphical applications entirely in Python.
* We wanted to improve our Python skills.
* Kivy is really good for the creation of a simple game.

## Requirements and Setup

### Prerequisites

* **Python 3.8 or higher**
  Download from [python.org](https://www.python.org/downloads/).

* **pip** (Python package installer)
  Included with Python 3. Ensure it’s up to date by running:

  ```bash
  python -m pip install --upgrade pip
  ```

* **Kivy**
  Install via pip:

  ```bash
  pip install kivy
  ```

* **Additional Python Libraries**
  All required libraries are part of the Python standard library or Kivy. Everything else comes with the standard library, so once you have Python 3.8+ and install Kivy, you’ll have all the pieces you need to run the game.

### Running the Application

1. **Clone the repository**

   ```bash
   git clone https://github.com/bernardowillis/HorseRaceBet.git
   cd horse-race-betting-game
   ```
   or download via Canvas.

2. **Install dependencies**

   ```bash
   pip install kivy
   ```

3. **Run the game**

   ```bash
   python main.py
   ```

No additional IDE is required—any text editor or Python IDE (e.g., VS Code, PyCharm) will work.

## Known Issues and Platform Limitations

* **Kivy Development Workflow:**

During our work, we found Kivy really interesting. The fact that we coded everything in python was good because we learned a lot, but picturing more of creating a bigger videogame we can say that:

  * Kivy does not offer a visual editor for layouts, so UI changes require code edits and manual reloads.
  * Debugging complex UI behaviors can be more time-consuming compared to engines with built-in inspectors like Unity.

* **Game Development Alternatives:**
  While Kivy is great for Python-based GUIs, dedicated game engines like Unity can be better in a way that has:

  * Visual scene editors and asset pipelines.
  * Built-in physics, particle systems, and animation tools.
  * More robust tooling for rapid iteration on game mechanics.

  For a production-quality game, those platforms may offer a faster and more feature-rich workflow.
