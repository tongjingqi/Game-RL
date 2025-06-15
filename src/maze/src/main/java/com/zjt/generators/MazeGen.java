package com.zjt.generators;

import com.zjt.constants.MazeConstants;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;

public class MazeGen {

    private static final Random RANDOM = new Random();

    /**
     * Generate a maze using the random depth-first search algorithm.
     * @param rows The number of rows in the maze (must be an odd number).
     * @param cols The number of columns in the maze (must be an odd number).
     * @return The generated maze array, including the player and goal.
     */
    public static int[][] generateMaze(int rows, int cols) {
        // Ensure the number of rows and columns is odd
        if (rows % 2 == 0 || cols % 2 == 0) {
            throw new IllegalArgumentException("The number of rows and columns in the maze must be odd!");
        }

        // Initialize the maze array, filling it entirely with walls (1)
        int[][] maze = new int[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                maze[i][j] = MazeConstants.WALL_CELL;
            }
        }

        // Randomized depth-first search algorithm
        maze[1][1] = MazeConstants.EMPTY_CELL;
        generateMazeDFS(maze, 1, 1);
        // Randomly place the player and goal
        placePlayerAndGoal(maze);

        return maze;
    }

    /**
     * Generate the maze using depth-first search.
     * @param maze The maze array.
     * @param row The current row position.
     * @param col The current column position.
     */
    private static void generateMazeDFS(int[][] maze, int row, int col) {
        // Define four directions (up, right, down, left)
        int[][] directions = {
                {-2, 0}, // Up
                {0, 2},  // Right
                {2, 0},  // Down
                {0, -2}  // Left
        };

        // Randomly shuffle the directions
        List<int[]> shuffledDirections = new ArrayList<>();
        Collections.addAll(shuffledDirections, directions);
        Collections.shuffle(shuffledDirections, RANDOM);

        // Traverse each direction
        for (int[] direction : shuffledDirections) {
            int nextRow = row + direction[0];
            int nextCol = col + direction[1];

            // Check if the position is out of bounds and if it has been visited
            if (isInBounds(maze, nextRow, nextCol) && maze[nextRow][nextCol] == 1) {
                // Remove the wall and set the position between the current and target as a path
                maze[row + direction[0] / 2][col + direction[1] / 2] = MazeConstants.EMPTY_CELL;
                maze[nextRow][nextCol] = MazeConstants.EMPTY_CELL;

                // Recursively continue generating
                generateMazeDFS(maze, nextRow, nextCol);
            }
        }
    }

    /**
     * Randomly place the player and goal in the maze.
     * @param maze The maze array.
     */
    public static void placePlayerAndGoal(int[][] maze) {
        Random random = new Random();
        int rows = maze.length;
        int cols = maze[0].length;

        int playerRow, playerCol, goalRow, goalCol;

        // Collect all the positions of empty cells
        List<int[]> emptyCells = new ArrayList<>();
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (maze[r][c] == MazeConstants.EMPTY_CELL) {
                    emptyCells.add(new int[]{r, c});
                }
            }
        }

        // Randomly select the player's position
        if (emptyCells.isEmpty()) {
            throw new IllegalArgumentException("There are no empty cells in the maze to place the player and goal.");
        }
        int[] playerPos = emptyCells.get(random.nextInt(emptyCells.size()));
        playerRow = playerPos[0];
        playerCol = playerPos[1];

        // Calculate the distance of all empty cells from the player's position
        List<CellDistance> cellDistances = new ArrayList<>();
        for (int[] cell : emptyCells) {
            if (cell[0] == playerRow && cell[1] == playerCol) {
                continue; // Skip the player's position
            }
            int distance = Math.abs(cell[0] - playerRow) + Math.abs(cell[1] - playerCol); // Manhattan distance
            cellDistances.add(new CellDistance(cell, distance));
        }

        if (cellDistances.isEmpty()) {
            throw new IllegalArgumentException("There are not enough empty cells to place the goal.");
        }

        // Get all unique distances and sort them (in descending order)
        List<Integer> uniqueDistances = cellDistances.stream()
                .map(cd -> cd.distance)
                .distinct()
                .sorted(Collections.reverseOrder())
                .collect(Collectors.toList());

        // Determine the target distance (the third farthest distance)
        int targetDistance;
        if (uniqueDistances.size() >= 3) {
            targetDistance = uniqueDistances.get(2); // Index starts from 0, the 3rd element
        } else if (uniqueDistances.size() >= 2) {
            targetDistance = uniqueDistances.get(1); // If less than 3, select the second farthest
        } else {
            targetDistance = uniqueDistances.get(0); // If only one, select the farthest
        }

        // Collect all cells with the target distance
        List<int[]> targetCells = cellDistances.stream()
                .filter(cd -> cd.distance == targetDistance)
                .map(cd -> cd.cell)
                .collect(Collectors.toList());

        if (targetCells.isEmpty()) {
            throw new IllegalArgumentException("No cells found with the target distance to place the goal.");
        }

        // Randomly select one of the target cells as the goal
        int[] goalPos = targetCells.get(random.nextInt(targetCells.size()));
        goalRow = goalPos[0];
        goalCol = goalPos[1];

        // Set the player and goal positions in the maze
        maze[playerRow][playerCol] = MazeConstants.PLAYER_CELL; // Player value (assume 2 represents the player)
        maze[goalRow][goalCol] = MazeConstants.GOAL_CELL;       // Goal value (assume 3 represents the goal)
    }

    /**
     * Helper class to store cells and their distances from the player's position.
     */
    private static class CellDistance {
        int[] cell;
        int distance;

        CellDistance(int[] cell, int distance) {
            this.cell = cell;
            this.distance = distance;
        }
    }

    /**
     * Check whether a position is within the bounds of the maze.
     * @param maze The maze array.
     * @param row The row position to check.
     * @param col The column position to check.
     * @return True if within bounds, otherwise false.
     */
    private static boolean isInBounds(int[][] maze, int row, int col) {
        return row > 0 && row < maze.length && col > 0 && col < maze[0].length;
    }
}


