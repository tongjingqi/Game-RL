package com.zjt.templates;

import com.zjt.constants.MazeConstants;
import com.zjt.constants.RulesConstants;

import java.util.List;

public class BaseTemplate{
    public String data_id;

    public String qa_type;

    public Integer question_id;

    public String question_description;

    public String image;

    public String state;

    public String plot_level;

    public String qa_level;

    public String question = "**Rules:**\n" +
            "1. This is a maze mini-game.The player needs to navigate around obstacles to reach the destination and achieve victory.\n" +
            "2. The red circle represents the player, the green block is the goal and the blue blocks are obstacles.\n" +
            "3. The player can only move within the white blocks.\n" +
            "4. The coordinates are given in the format (row, col), where row represents the vertical position and col represents the horizontal position.\n\n" +
            "**Question:** ";

    public String answer;

    public String[] options;

    public String analysis = "";




    public BaseTemplate(int[][] maze, int imageId) {

        image = MazeConstants.IMAGES_DIR + "/image_" + String.format("%05d", imageId) + ".png";
        state = MazeConstants.STATES_DIR + "/state_" + String.format("%05d", imageId) + ".json";

        switch (maze.length) {
            case RulesConstants.EASY_MAZE_COLS:
                plot_level = "Easy";
                break;
            case RulesConstants.MEDIUM_MAZE_COLS:
                plot_level = "Medium";
                break;
            case RulesConstants.HARD_MAZE_COLS:
                plot_level = "Hard";
                break;
        }
    }

}
