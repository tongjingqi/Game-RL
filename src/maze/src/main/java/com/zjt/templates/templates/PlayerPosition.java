package com.zjt.templates.templates;

import com.zjt.constants.MazeConstants;
import com.zjt.templates.BaseTemplate;
import com.zjt.utils.MazeUtils;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;

public class PlayerPosition extends BaseTemplate {

    public PlayerPosition(int[][] maze, int imageId) {

        super(maze, imageId);

        qa_type = "StateInfo";

        question_id = 1;

        data_id = "maze_" + String.format("%05d", imageId) + "_" + String.format("%02d", question_id);

        question_description = "Ask for the position of player.";

        qa_level = "Easy";

        question += "Which of the following are the coordinates of the player?\n\n" +
                "**Options:**";



        // answer, analysis
        int[] ans = MazeUtils.findPosition(maze, MazeConstants.PLAYER_CELL);
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


        analysis = "Take a look at the game screen, the red circle represents the player.\n" +
                "The coordinates of player are " + ansStr + ", so the right option is " + answer;

    }
}
