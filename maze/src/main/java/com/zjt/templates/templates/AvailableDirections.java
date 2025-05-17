package com.zjt.templates.templates;

import com.zjt.constants.MazeConstants;
import com.zjt.templates.BaseTemplate;
import com.zjt.utils.MazeUtils;


import java.util.*;

public class AvailableDirections extends BaseTemplate {

    public AvailableDirections(int[][] maze, int imageId) {

        super(maze, imageId);

        question_id = 5;

        data_id = "maze_" + String.format("%05d", imageId) + "_" + String.format("%02d", question_id);

        qa_type = "StateInfo";

        question_description = "Ask for the available directions to move are currently.";

        qa_level = "Easy";

        question += "Which directions are available to move now?\n\n" +
                "**Options:**";


        // answer, analysis
        List<String> ans = MazeUtils.getAvailableDirections(maze);
        String ans_str = ans.get(0);
        for (int i = 1; i < ans.size(); i++) ans_str = ans_str + ", " + ans.get(i);

        String[] options1 = new String[]{"up", "down", "left", "right"};
        String[] options2 = new String[]{"up, down", "up, left", "up, right", "down, left", "down, right", "left, right"};
        String[] options3 = new String[]{"up, down, left", "up, down, right", "up, left, right","down, left, right"};
        String[] options4 = new String[]{"up, down, left, right"};

        HashSet<String> options_ = new HashSet<>();

        addRandomOptions(options_, options1, 2);
        addRandomOptions(options_, options2, 2);
        addRandomOptions(options_, options3, 2);
        addRandomOptions(options_, options4, 1);
        options_.add(ans_str);

        List<String> optionsList = new ArrayList<>(options_);

        Collections.sort(optionsList, new Comparator<String>() {
            @Override
            public int compare(String o1, String o2) {
                return Integer.compare(o1.length(), o2.length());
            }
        });

        options = new String[optionsList.size()];

        char label = 'A';
        for (int i = 0; i < optionsList.size(); i++) {
            options[i] = (char)(label + i) + ". " + optionsList.get(i);
            if (optionsList.get(i).equals(ans_str)) {
                answer = String.valueOf((char)(label + i));
            }
        }

        for (String option : options) {
            question += ("\n" + option);
        }

        int[] player = MazeUtils.findPosition(maze,MazeConstants.PLAYER_CELL);

        analysis = "The player is on (" + player[0] + ", " + player[1] + ")";
        analysis += ", and";
        if (ans_str.contains("up")) {
            analysis += " (" + (player[0]-1) + ", " + player[1] + ")";
        }
        if (ans_str.contains("down")) {
            analysis += " (" + (player[0]+1) + ", " + player[1] + ")";
        }
        if (ans_str.contains("left")) {
            analysis += " (" + player[0] + ", " + (player[1]-1) + ")";
        }
        if (ans_str.contains("right")) {
            analysis += " (" + player[0] + ", " + (player[1]+1) + ")";
        }
        analysis += " is empty. The player can move " + ans_str + ". Therefore, The option is " + answer;

    }

    public static void addRandomOptions(HashSet<String> set, String[] options, int count) {
        Random random = new Random();
        count = set.size() + count;
        while (set.size() < count) {
            String randomOption = options[random.nextInt(options.length)];
            set.add(randomOption);
        }
    }

}
