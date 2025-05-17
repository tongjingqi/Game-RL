package com.zjt.generators;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.zjt.constants.MazeConstants;
import com.zjt.utils.MazeUtils;

import java.io.FileWriter;
import java.io.IOException;

public class StateGen {
    public static void saveState(int[][] maze, String saveStatePath) {
        int[] mazeSize = {maze.length, maze[0].length};

        int[] playerPosition = MazeUtils.findPosition(maze, MazeConstants.PLAYER_CELL);
        int[] endPosition = MazeUtils.findPosition(maze, MazeConstants.GOAL_CELL);

        MazeState mazeState = new MazeState(maze, mazeSize, playerPosition, endPosition);

        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        String json = gson.toJson(mazeState);

        try (FileWriter writer = new FileWriter(saveStatePath)) {
            writer.write(json);
        } catch (IOException e) {
            System.err.println("Failed to save maze state: " + e.getMessage());
        }
    }

    // Inner class: represents the maze state
    static class MazeState {
        private int[][] maze;
        private int[] size;
        private int[] playerPosition;
        private int[] endPosition;

        public MazeState(int[][] maze, int[] size, int[] playerPosition, int[] endPosition) {
            this.maze = maze;
            this.size = size;
            this.playerPosition = playerPosition;
            this.endPosition = endPosition;
        }
    }
}

