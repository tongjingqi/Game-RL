package com.zjt.generators;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.zjt.constants.MazeConstants;
import com.zjt.templates.BaseTemplate;
import com.zjt.templates.templates.*;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class DataGen {

    /**
     * Generate JSON data.
     * @param maze The maze array.
     * @return A list of JSON items, where each item contains fields such as data_id, qa_type, etc.
     */
    public static List<BaseTemplate> generateJsonData(int[][] maze, int dataId) {
        List<BaseTemplate> jsonItems = new ArrayList<>();

        // Register templates
        jsonItems.add(new PlayerPosition(maze, dataId));
        jsonItems.add(new GoalPosition(maze, dataId));
        jsonItems.add(new PositionAfterMoving(maze, dataId));
        jsonItems.add(new AvailableDirections(maze, dataId));
        jsonItems.add(new FindPathToGoal(maze, dataId));
        jsonItems.add(new TurnCount(maze, dataId));

        return jsonItems;
    }

    /**
     * Generate data.
     *
     * @param idBegin   Starting ID.
     * @param dataSize  The number of data items to generate.
     * @param mazeSize  The size of the maze.
     * @param imagesDir The directory for saving images.
     * @param stateDir  The directory for saving state files.
     * @return A list of generated template data.
     */
    public static List<BaseTemplate> generateData(int idBegin, int dataSize, int mazeSize, String imagesDir, String stateDir) {
        List<BaseTemplate> data = new ArrayList<>();

        for (int id = idBegin; id < idBegin + dataSize; id++) {
            String saveImagePath = String.format("%s/image_%05d.png", imagesDir, id);
            int[][] maze = MazeGen.generateMaze(mazeSize, mazeSize);
            ImageGen.drawMaze(maze, MazeConstants.CELL_SIZE, saveImagePath);
            String saveStatePath = String.format("%s/state_%05d.json", stateDir, id);
            StateGen.saveState(maze, saveStatePath);
            data.addAll(DataGen.generateJsonData(maze, id));
        }

        return data;
    }

    /**
     * Save the list of question templates as a JSON file.
     * @param questions The list of question templates.
     * @param filePath The path of the JSON file.
     */
    public static void saveDataToJson(List<BaseTemplate> questions, String filePath) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create(); // Format output
        try (FileWriter writer = new FileWriter(filePath)) {
            gson.toJson(questions, writer); // Serialize the object into JSON
        } catch (IOException e) {
            System.err.println("save JSON File error: " + e.getMessage());
        }
    }
}

