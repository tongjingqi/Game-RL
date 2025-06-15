package com.zjt.templates.templates;

import com.zjt.constants.MazeConstants;
import com.zjt.templates.BaseTemplate;
import com.zjt.utils.MazeUtils;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;


public class GoalPosition extends BaseTemplate {

    public GoalPosition(int[][] maze, int imageId) {

        super(maze, imageId);

        qa_type = "StateInfo";

        question_id = 2;

        data_id = "maze_" + String.format("%05d", imageId) + "_" + String.format("%02d", question_id);

        question_description = "Ask for the position of goal within the maze.";

        qa_level = "Easy";

        question += "Which of the following are the coordinates of the goal?\"\n\n" +
                "**Optoins:**";


        // answer, analysis
        int[] ans = MazeUtils.findPosition(maze, MazeConstants.GOAL_CELL);
        String ansStr = "(" + ans[0] + ", " + ans[1] + ")";

        HashSet<String> op = new HashSet<>();
        op.add(ansStr);
        op.add("(" + (ans[0]+1) + ", " + ans[1] + ")");
        op.add("(" + (ans[0]-1) + ", " + ans[1] + ")");
        op.add("(" + ans[0] + ", " + (ans[1]+1) + ")");
        op.add("(" + ans[0] + ", " + (ans[1]-1) + ")");

        List optionsList = Arrays.asList(op.toArray());

        options = new String[optionsList.size()];
        char label = 'A';
        for (int i = 0; i < optionsList.size(); i++) {
            options[i] = (char)(label + i) + ". " + optionsList.get(i);
            if (optionsList.get(i).equals(ansStr)) {
                answer = String.valueOf((char)(label + i));
            }
        }

        for (String option : options) {
            question += ("\n" + option);
        }

        analysis = "Take a look at the game screen, the green block represents the goal.\n" +
                "The coordinates of goal are " + ansStr + ", so the right option is " + answer;

    }
}
