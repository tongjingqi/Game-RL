package com.zjt.templates.templates;

import com.zjt.templates.BaseTemplate;
import com.zjt.utils.MazeUtils;


import java.util.ArrayList;
import java.util.List;

public class TurnCount extends BaseTemplate {

    public TurnCount(int[][] maze, int imageId) {

        super(maze, imageId);

        question_id = 4;

        data_id = "maze_" + String.format("%05d", imageId) + "_" + String.format("%02d", question_id);

        qa_type = "TransitionPath";

        question += "Find the path to the finish and count the number of turns it takes to get there. You only need to provide one number.";

        question_description = "Count how many turns it takes to reach the finish.";

        qa_level = "Hard";





        // answer, analysis
        List<String> info = new ArrayList<>();
        List<int[]> paths = MazeUtils.dfsSolveMaze(maze, info);
        List<String> info1 = new ArrayList<>();
        Integer turns = MazeUtils.countTurns(paths, info1);
        answer = turns.toString();
        for (String str : info) {
            analysis += str;
        }
        analysis = "First," + analysis + "Therefore, the path is: " + MazeUtils.pathToString(paths);
        analysis = analysis + "\n\nThen,";
        for (String str : info1) {
            analysis += str;
        }
        analysis = analysis + ("\nIn summary, the total number of turns is " + turns);
    }
}
