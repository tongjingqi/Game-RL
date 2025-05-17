package com.zjt.templates.templates;

import com.zjt.constants.MazeConstants;
import com.zjt.templates.BaseTemplate;
import com.zjt.utils.MazeUtils;


import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public class PositionAfterMoving extends BaseTemplate {

    public PositionAfterMoving(int[][] maze, int imageId) {

        super(maze, imageId);

        qa_type = "ActionOutcome";

        question_id = 6;

        data_id = "maze_" + String.format("%05d", imageId) + "_" + String.format("%02d", question_id);

        question_description = "The position after moving.";

        qa_level = "Medium";

        question += "What are the coordinates of player after moving ";


        // answer, analysis
        int[] player = MazeUtils.findPosition(maze, MazeConstants.PLAYER_CELL);

        List<String> ans = MazeUtils.getAvailableDirections(maze);
        int randomIndex = ThreadLocalRandom.current().nextInt(ans.size());
        String direction = ans.get(randomIndex);

        question += (direction + "?\n\n**Options:**");;

        String ansStr = "";
        if (direction.equals("up")) {
            ansStr = "(" + (player[0]-1) + ", " + player[1] + ")";
        } else if (direction.equals("down")) {
            ansStr = "(" + (player[0]+1) + ", " + player[1] + ")";
        } else if (direction.equals("left")) {
            ansStr = "(" + (player[0]) + ", " + (player[1]-1) + ")";
        } else if (direction.equals("right")) {
            ansStr = "(" + (player[0]) + ", " + (player[1]+1) + ")";
        }

        HashSet<String> op = new HashSet<>();
        op.add(ansStr);
        op.add("(" + (player[0]+1) + ", " + player[1] + ")");
        op.add("(" + (player[0]-1) + ", " + player[1] + ")");
        op.add("(" + player[0] + ", " + (player[1]+1) + ")");
        op.add("(" + player[0] + ", " + (player[1]-1) + ")");
        op.add("(" + player[0] + ", " + player[1] + ")");

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

        analysis = "Observe the screen, the position of player is (" + player[0] + "," + player[1] + ")"+
                    ". After moving " + direction + ", the player is in " + ansStr +
                    ". Therefore, the right option is " + answer;

    }
}
