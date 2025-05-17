package com.zjt.utils;

import com.zjt.constants.MazeConstants;

import java.util.*;

public class MazeUtils {
    /**
     * Find the position of a specific value in the maze.
     *
     * @param maze        The maze array.
     * @param targetValue The value to search for (e.g., player value 2 or goal value 3).
     * @return An array containing the row and column {row, col}, or throws an exception if not found.
     */
    public static int[] findPosition(int[][] maze, int targetValue) {
        for (int row = 0; row < maze.length; row++) {
            for (int col = 0; col < maze[row].length; col++) {
                if (maze[row][col] == targetValue) {
                    return new int[]{row, col};
                }
            }
        }
        throw new IllegalArgumentException("Target value not found in the maze: " + targetValue);
    }

    /**
     * Depth-First Search (DFS) algorithm to find a path in the maze and output backtracking information.
     *
     * @param maze The maze array.
     * @param info A list to store step-by-step information about the process.
     * @return The path found (contains all coordinates visited).
     */
    public static List<int[]> dfsSolveMaze(int[][] maze, List<String> info) {
        int[][] mazeState = new int[maze.length][maze[0].length];
        for (int row = 0; row < maze.length; row++) {
            System.arraycopy(maze[row], 0, mazeState[row], 0, maze[row].length);
        }

        List<int[]> path = new ArrayList<>();
        Stack<int[]> backtrack = new Stack<>();
        int[] player = findPosition(maze, MazeConstants.PLAYER_CELL);
        int[] goal = findPosition(maze, MazeConstants.GOAL_CELL);

        int startRow = player[0];
        int startCol = player[1];
        int goalRow = goal[0];
        int goalCol = goal[1];

        Stack<int[]> stack = new Stack<>();
        int[][] directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

        mazeState[startRow][startCol] = -1;
        shuffleDirections(directions);

        int branchCount = 0;
        for (int[] direction : directions) {
            int newRow = startRow + direction[0];
            int newCol = startCol + direction[1];

            if (isValid(mazeState, newRow, newCol)) {
                stack.push(new int[]{newRow, newCol});
                branchCount++;
            }
        }
        if (branchCount > 1) {
            backtrack.push(new int[]{startRow, startCol, branchCount - 1});
        }
        path.add(new int[]{startRow, startCol});

        int curRow = startRow;
        int curCol = startCol;
        int step = 1;
        info.add("Let’s figure out the path to the goal step by step.\n");

        while (!stack.isEmpty()) {
            info.add("Step " + step + ". ");
            step++;
            int[] next = stack.pop();
            int row = next[0];
            int col = next[1];
            mazeState[row][col] = -1;
            path.add(new int[]{row, col});

            String direction = getDirection(new int[]{curRow, curCol}, next);
            info.add("Go " + direction + ", from (" + curRow + ", " + curCol + ") to (" + row + ", " + col + "). ");

            curRow = row;
            curCol = col;

            if (row == goalRow && col == goalCol) {
                info.add("Achieved the goal!");
                return path;
            }

            branchCount = 0;
            shuffleDirections(directions);
            for (int[] dir : directions) {
                int newRow = row + dir[0];
                int newCol = col + dir[1];

                if (isValid(mazeState, newRow, newCol)) {
                    stack.push(new int[]{newRow, newCol});
                    branchCount++;
                }
            }
            if (branchCount > 1) {
                backtrack.push(new int[]{row, col, branchCount - 1});
            }
            if (branchCount == 0) {
                int[] back = backtrack.pop();
                curRow = back[0];
                curCol = back[1];
                int remainingBranches = back[2];

                info.add("Oops! We hit a dead end. Going back to the last unexplored branch at (" + curRow + ", " + curCol + ").");
                if (remainingBranches > 1) {
                    backtrack.push(new int[]{curRow, curCol, remainingBranches - 1});
                }

                while (!path.isEmpty() && (path.get(path.size() - 1)[0] != curRow || path.get(path.size() - 1)[1] != curCol)) {
                    path.remove(path.size() - 1);
                }
            }

            info.add("\n");
        }
        return path;
    }

    /**
     * Check if a cell in the maze is valid for visiting.
     *
     * @param maze The maze array.
     * @param row  The row index.
     * @param col  The column index.
     * @return Whether the cell is valid to visit.
     */
    private static boolean isValid(int[][] maze, int row, int col) {
        return row >= 0 && row < maze.length && col >= 0 && col < maze[0].length &&
                (maze[row][col] == MazeConstants.EMPTY_CELL || maze[row][col] == MazeConstants.GOAL_CELL);
    }

    /**
     * Convert a path list into a string representation.
     *
     * @param path The path list.
     * @return The string representation of the path.
     */
    public static String pathToString(List<int[]> path) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < path.size(); i++) {
            int[] point = path.get(i);
            sb.append("(").append(point[0]).append(", ").append(point[1]).append(")");
            if (i != path.size() - 1) {
                sb.append(", ");
            }
        }
        return sb.toString();
    }

    /**
     * Count the number of turns in a path.
     *
     * @param path The path list.
     * @param info A list to store step-by-step turn counting information.
     * @return The number of turns.
     */
    public static int countTurns(List<int[]> path, List<String> info) {
        if (path == null || path.size() < 2) {
            return 0;
        }
        info.add("Let's count the number of turns step by step.\n");

        int turns = 0;
        int[] first = path.get(0);
        int[] second = path.get(1);
        String prevDirection = getDirection(first, second);

        for (int i = 2; i < path.size(); i++) {
            int[] previous = path.get(i - 1);
            int[] current = path.get(i);
            String currentDirection = getDirection(previous, current);

            info.add("Step " + i + ". ");
            if (!currentDirection.equals(prevDirection)) {
                info.add("Turn detected: from " + prevDirection + " to " + currentDirection + ".\n");
                turns++;
                prevDirection = currentDirection;
            } else {
                info.add("No turn detected.\n");
            }
        }
        return turns;
    }

    /**
     * Get the direction of movement between two points.
     *
     * @param from The starting point.
     * @param to   The destination point.
     * @return The direction as a string.
     */
    public static String getDirection(int[] from, int[] to) {
        if (from == null || to == null || from.length != 2 || to.length != 2) {
            throw new IllegalArgumentException("Invalid arguments.");
        }

        int dx = to[0] - from[0];
        int dy = to[1] - from[1];

        if (dx == -1 && dy == 0) {
            return "up";
        } else if (dx == 1 && dy == 0) {
            return "down";
        } else if (dx == 0 && dy == -1) {
            return "left";
        } else if (dx == 0 && dy == 1) {
            return "right";
        } else {
            return "invalid";
        }
    }

    /**
     * Shuffle the direction order randomly.
     *
     * @param directions The directions array.
     */
    public static void shuffleDirections(int[][] directions) {
        Random random = new Random();
        for (int i = directions.length - 1; i > 0; i--) {
            int j = random.nextInt(i + 1);
            int[] temp = directions[i];
            directions[i] = directions[j];
            directions[j] = temp;
        }
    }

    /**
     * Get all available directions the player can move in.
     *
     * @param maze The maze array.
     * @return A list of available directions as strings.
     */
    public static List<String> getAvailableDirections(int[][] maze) {
        List<String> availableDirections = new ArrayList<>();
        int rows = maze.length;
        int cols = maze[0].length;
        int playerRow = -1;
        int playerCol = -1;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (maze[r][c] == MazeConstants.PLAYER_CELL) {
                    playerRow = r;
                    playerCol = c;
                    break;
                }
            }
        }

        if (playerRow == -1 || playerCol == -1) {
            throw new IllegalArgumentException("Player position not found in the maze.");
        }

        String[] directions = {"up", "down", "left", "right"};
        int[][] directionOffsets = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

        for (int i = 0; i < directions.length; i++) {
            int newRow = playerRow + directionOffsets[i][0];
            int newCol = playerCol + directionOffsets[i][1];

            if (newRow >= 0 && newRow < rows && newCol >= 0 && newCol < cols &&
                    (maze[newRow][newCol] == MazeConstants.EMPTY_CELL || maze[newRow][newCol] == MazeConstants.GOAL_CELL)) {
                availableDirections.add(directions[i]);
            }
        }

        return availableDirections;
    }

}

