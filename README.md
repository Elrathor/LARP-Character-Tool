# LARP Character Assignment Generator

A Python tool that optimally assigns LARP characters to players based on their preferences using mathematical optimization algorithms.

## Overview

This tool solves the classic assignment problem for Live Action Role Playing (LARP) games by finding the optimal character-to-player assignments that maximize overall player satisfaction. It uses both brute force and Hungarian Algorithm approaches to ensure players get characters they want while maintaining fairness.

## Features

- **Optimal Assignment**: Uses the Hungarian Algorithm for mathematically optimal solutions
- **Multiple Scoring Systems**: Supports both linear and weighted scoring for different preference models
- **Flexible Input**: Accepts player preferences in rank order
- **Satisfaction Analysis**: Checks constraint satisfaction and provides detailed statistics
- **JSON Support**: Can load preferences from JSON files for larger groups
- **Detailed Output**: Provides comprehensive assignment results with rankings and scores

## Requirements

- Python 3.6+
- scipy (for Hungarian Algorithm)
- numpy (for matrix operations)

Install dependencies:
```bash
pip install scipy numpy
```

## Usage

### Basic Example

```python
from main import LARPAssigner

# Define available characters
characters = [
    "Franky Mangata",
    "Sigrid Mangata", 
    "Halimede Mangata",
    "Callisto Mangata",
    "Dr. Celestin Mangata"
]

# Create assigner
assigner = LARPAssigner(len(characters))

# Add player preferences (ranked from most to least preferred)
assigner.add_player_preferences(
    "Player #1",
    ["Halimede Mangata", "Dr. Celestin Mangata", "Franky Mangata",
     "Sigrid Mangata", "Callisto Mangata"]
)

# Add more players...

# Solve assignment
assignments, score, details = assigner.solve_assignment_hungarian("linear")
assigner.print_results(assignments, score, details, "linear")
```

### JSON Input Format

```json
{
    "characters": ["Character1", "Character2", "Character3"],
    "players": {
        "Player1": ["Character2", "Character1", "Character3"],
        "Player2": ["Character1", "Character3", "Character2"]
    }
}
```

Load from JSON:
```python
from main import load_from_json

assigner = load_from_json("preferences.json")
assignments, score, details = assigner.solve_assignment_hungarian()
```

## Scoring Systems

### Linear Scoring
- 1st choice: n points
- 2nd choice: n-1 points  
- 3rd choice: n-2 points
- etc.

### Weighted Scoring
- 1st choice: 20 points
- 2nd choice: 15 points
- 3rd choice: 10 points
- 4th choice: 5 points
- 5th choice: 3 points
- 6+ choice: 1 point

## Methods

### [`LARPAssigner`](c:\Users\tobia\PycharmProjects\LarpAssignmentGenerator\main.py)

#### Core Methods
- [`add_player_preferences()`](c:\Users\tobia\PycharmProjects\LarpAssignmentGenerator\main.py): Add a player's ranked character preferences
- [`solve_assignment_hungarian()`](c:\Users\tobia\PycharmProjects\LarpAssignmentGenerator\main.py): Optimal solution using Hungarian Algorithm
- [`solve_assignment_brute_force()`](c:\Users\tobia\PycharmProjects\LarpAssignmentGenerator\main.py): Exhaustive search (≤8 players only)

#### Analysis Methods  
- [`calculate_points()`](c:\Users\tobia\PycharmProjects\LarpAssignmentGenerator\main.py): Calculate points for player-character assignment
- [`check_satisfaction_constraints()`](c:\Users\tobia\PycharmProjects\LarpAssignmentGenerator\main.py): Verify assignment meets constraints
- [`print_results()`](c:\Users\tobia\PycharmProjects\LarpAssignmentGenerator\main.py): Display formatted assignment results

## Example Output

```
============================================================
OPTIMAL LARP CHARACTER ASSIGNMENT
============================================================
Scoring System: Linear
Total Satisfaction Score: 19
Average Score per Player: 3.8

Player          Character       Rank   Points  
--------------------------------------------------
Player #1       Halimede Mangata #1     5      
Player #2       Callisto Mangata #1     5      
Player #3       Sigrid Mangata   #1     5      
Player #4       Dr. Celestin Mangata #1 5      
Player #5       Franky Mangata   #1     5      

Rank Distribution:
  Rank #1: 5 players

First choice assignments: 5
Top 3 choice assignments: 5

✅ All players got their top 3 choices!
```

## Algorithm Complexity

- **Hungarian Algorithm**: O(n³) - Efficient for any group size
- **Brute Force**: O(n!) - Only recommended for ≤8 players

## License

This project is licensed under the MIT License - see the [LICENSE](c:\Users\tobia\PycharmProjects\LarpAssignmentGenerator\LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Author

Tobias Boyer

## Acknowledgments

- Uses the Hungarian Algorithm implementation from scipy
- Inspired by the assignment problem in operations research