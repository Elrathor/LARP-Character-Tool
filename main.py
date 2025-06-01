#!/usr/bin/env env python3
"""
LARP Character Assignment Tool using Points System
Finds optimal character assignments to maximize player satisfaction.
"""

import itertools
from typing import Dict, List, Tuple, Optional
import json


class LARPAssigner:
    def __init__(self, num_characters: int):
        """
        Initialize the LARP character assigner.

        Args:
            num_characters: Total number of characters available
        """
        self.num_characters = num_characters
        self.players: Dict[str, List[str]] = {}
        self.characters: List[str] = []

    def add_player_preferences(
            self, player_name: str, ranked_characters: List[str]
    ) -> None:
        """
        Add a player's character preferences.

        Args:
            player_name: Name of the player
            ranked_characters: List of characters in order of preference
                              (1st = most preferred)
        """
        if len(ranked_characters) != self.num_characters:
            raise ValueError(
                f"Player {player_name} must rank all {self.num_characters} "
                f"characters, got {len(ranked_characters)}"
            )

        self.players[player_name] = ranked_characters

        # Update character list (use first player's list as reference)
        if not self.characters:
            self.characters = ranked_characters.copy()

    def calculate_points(
            self, player: str, character: str, scoring_system: str = "linear"
    ) -> int:
        """
        Calculate points for a player-character assignment.

        Args:
            player: Player name
            character: Character name
            scoring_system: "linear" or "weighted" scoring

        Returns:
            Points for this assignment
        """
        if player not in self.players:
            return 0

        try:
            rank = self.players[player].index(character) + 1  # 1-indexed
        except ValueError:
            return 0  # Character not in player's list

        if scoring_system == "linear":
            # Linear: #1=n points, #2=n-1 points, etc.
            return self.num_characters - rank + 1
        elif scoring_system == "weighted":
            # Weighted: heavily favor top choices
            if rank == 1:
                return 20
            elif rank == 2:
                return 15
            elif rank == 3:
                return 10
            elif rank == 4:
                return 5
            elif rank == 5:
                return 3
            else:
                return 1
        else:
            raise ValueError("scoring_system must be 'linear' or 'weighted'")

    def generate_assignment_matrix(
            self, scoring_system: str = "linear"
    ) -> Tuple[List[str], List[str], List[List[int]]]:
        """
        Generate the points matrix for all player-character combinations.

        Args:
            scoring_system: "linear" or "weighted" scoring

        Returns:
            Tuple of (player_names, character_names, points_matrix)
        """
        player_names = list(self.players.keys())
        character_names = self.characters.copy()

        # Create points matrix
        matrix = []
        for player in player_names:
            row = []
            for character in character_names:
                points = self.calculate_points(player, character, scoring_system)
                row.append(points)
            matrix.append(row)

        return player_names, character_names, matrix

    def solve_assignment_hungarian(
            self, scoring_system: str = "linear"
    ) -> Tuple[Dict[str, str], int, List[Tuple[str, str, int]]]:
        """
        Solve the assignment problem using Hungarian Algorithm.

        Args:
            scoring_system: "linear" or "weighted" scoring

        Returns:
            Tuple of (assignments_dict, total_score, assignment_details)
        """
        try:
            from scipy.optimize import linear_sum_assignment
            import numpy as np
        except ImportError:
            raise ImportError(
                "scipy and numpy are required for optimal assignment. "
                "Install with: pip install scipy numpy"
            )

        player_names, character_names, matrix = self.generate_assignment_matrix(
            scoring_system
        )

        # Convert to numpy array and negate (Hungarian minimizes, we want max)
        cost_matrix = np.array(matrix) * -1

        # Solve assignment problem
        row_indices, col_indices = linear_sum_assignment(cost_matrix)

        # Build results
        assignments = {}
        assignment_details = []
        total_score = 0

        for i, j in zip(row_indices, col_indices):
            player = player_names[i]
            character = character_names[j]
            points = matrix[i][j]
            rank = self.players[player].index(character) + 1

            assignments[player] = character
            assignment_details.append((player, character, points, rank))
            total_score += points

        return assignments, total_score, assignment_details

    def solve_assignment_brute_force(
            self, scoring_system: str = "linear"
    ) -> Tuple[Dict[str, str], int, List[Tuple[str, str, int]]]:
        """
        Solve assignment problem by checking all permutations.
        WARNING: Only use for small groups (≤8 players) due to factorial complexity.

        Args:
            scoring_system: "linear" or "weighted" scoring

        Returns:
            Tuple of (best_assignments, best_score, assignment_details)
        """
        player_names = list(self.players.keys())
        character_names = self.characters.copy()

        if len(player_names) > 8:
            raise ValueError(
                "Brute force method not recommended for >8 players. "
                "Use solve_assignment_hungarian() instead."
            )

        best_score = -1
        best_assignment = None
        best_details = None

        # Generate all possible assignments (permutations)
        for char_permutation in itertools.permutations(character_names):
            current_assignment = dict(zip(player_names, char_permutation))
            current_score = 0
            current_details = []

            for player, character in current_assignment.items():
                points = self.calculate_points(player, character, scoring_system)
                rank = self.players[player].index(character) + 1
                current_score += points
                current_details.append((player, character, points, rank))

            if current_score > best_score:
                best_score = current_score
                best_assignment = current_assignment
                best_details = current_details

        return best_assignment, best_score, best_details

    def check_satisfaction_constraints(
            self, assignments: Dict[str, str], max_rank_allowed: int = None
    ) -> Tuple[bool, List[str]]:
        """
        Check if assignment meets satisfaction constraints.

        Args:
            assignments: Player -> Character assignments
            max_rank_allowed: Maximum rank a player can receive (None = no limit)

        Returns:
            Tuple of (all_satisfied, list_of_unsatisfied_players)
        """
        unsatisfied = []

        for player, character in assignments.items():
            rank = self.players[player].index(character) + 1

            if max_rank_allowed and rank > max_rank_allowed:
                unsatisfied.append(
                    f"{player} got rank {rank} choice ({character})"
                )

        return len(unsatisfied) == 0, unsatisfied

    def print_results(
            self,
            assignments: Dict[str, str],
            total_score: int,
            details: List[Tuple[str, str, int, int]],
            scoring_system: str = "linear",
    ) -> None:
        """Print formatted results."""
        print(f"\n{'=' * 60}")
        print(f"OPTIMAL LARP CHARACTER ASSIGNMENT")
        print(f"{'=' * 60}")
        print(f"Scoring System: {scoring_system.title()}")
        print(f"Total Satisfaction Score: {total_score}")
        print(f"Average Score per Player: {total_score / len(assignments):.1f}")

        print(f"\n{'Player':<15} {'Character':<15} {'Rank':<6} {'Points':<8}")
        print("-" * 50)

        # Sort by rank for better readability
        sorted_details = sorted(details, key=lambda x: x[3])

        for player, character, points, rank in sorted_details:
            print(f"{player:<15} {character:<15} #{rank:<5} {points:<8}")

        # Statistics
        ranks = [detail[3] for detail in details]
        rank_counts = {}
        for i in range(1, self.num_characters + 1):
            rank_counts[i] = ranks.count(i)

        print(f"\n{'Rank Distribution:'}")
        for rank, count in rank_counts.items():
            if count > 0:
                print(f"  Rank #{rank}: {count} players")

        print(f"\nFirst choice assignments: {rank_counts[1]}")
        print(f"Top 3 choice assignments: {sum(rank_counts[i] for i in [1, 2, 3])}")


def load_from_json(filename: str) -> LARPAssigner:
    """
    Load player preferences from JSON file.

    Expected format:
    {
        "characters": ["Character1", "Character2", ...],
        "players": {
            "Player1": ["Character2", "Character1", ...],
            "Player2": ["Character1", "Character3", ...]
        }
    }
    """
    with open(filename, 'r') as f:
        data = json.load(f)

    characters = data['characters']
    assigner = LARPAssigner(len(characters))

    for player, preferences in data['players'].items():
        assigner.add_player_preferences(player, preferences)

    return assigner


def main():
    """Example usage of the LARP Character Assigner."""

    # Example data - replace with your actual data
    characters = [
        "Franky Mangata",
        "Sigrid Mangata",
        "Halimede Mangata",
        "Callisto Mangata",
        "Dr. Celestin Mangata"
    ]

    # Create assigner
    assigner = LARPAssigner(len(characters))

    # Add player preferences (each player ranks ALL characters)
    assigner.add_player_preferences(
        "Player #1",
        ["Halimede Mangata", "Dr. Celestin Mangata", "Franky Mangata",
         "Sigrid Mangata", "Callisto Mangata"]
    )
    assigner.add_player_preferences(
        "Player #2",
        ["Callisto Mangata", "Franky Mangata", "Sigrid Mangata",
         "Halimede Mangata", "Dr. Celestin Mangata"]
    )
    assigner.add_player_preferences(
        "Player #3",
        ["Sigrid Mangata", "Halimede Mangata", "Callisto Mangata",
         "Dr. Celestin Mangata", "Franky Mangata"]
    )
    assigner.add_player_preferences(
        "Player #4",
        ["Dr. Celestin Mangata", "Franky Mangata", "Halimede Mangata",
         "Sigrid Mangata", "Callisto Mangata"]
    )
    assigner.add_player_preferences(
        "Player #5",
        ["Franky Mangata", "Callisto Mangata", "Dr. Celestin Mangata",
         "Halimede Mangata", "Sigrid Mangata"]
    )

    # Solve using Hungarian Algorithm (optimal)
    print("Solving with Hungarian Algorithm (Optimal Solution):")
    assignments, score, details = assigner.solve_assignment_hungarian("linear")
    assigner.print_results(assignments, score, details, "linear")

    # Check satisfaction
    satisfied, unsatisfied = assigner.check_satisfaction_constraints(
        assignments, max_rank_allowed=3
    )
    if satisfied:
        print("\n✅ All players got their top 3 choices!")
    else:
        print(f"\n⚠️  Some players got lower choices:")
        for issue in unsatisfied:
            print(f"   - {issue}")

    # Try weighted scoring
    print(f"\n{'-' * 60}")
    print("Solving with Weighted Scoring System:")
    assignments_w, score_w, details_w = assigner.solve_assignment_hungarian(
        "weighted"
    )
    assigner.print_results(assignments_w, score_w, details_w, "weighted")


if __name__ == "__main__":
    main()