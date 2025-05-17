package com.zjt.templates.templates;

import com.zjt.templates.BaseTemplate;
import com.zjt.utils.MazeUtils;

import java.util.*;

public class FindPathToGoal extends BaseTemplate {


    public FindPathToGoal(int[][] maze, int imageId) {

        super(maze, imageId);

        question_id = 3;

        this.data_id = "maze_" + String.format("%05d", imageId) + "_" + String.format("%02d", question_id);

        qa_type = "TransitionPath";

        question_description = "Find the path to the goal";

        qa_level = "Medium";

        question += "Which sequence of movements will allow the player to reach the destination?\n\n" +
                "**Options:**";


        // answer, analysis
        List<String> info = new ArrayList<>();

        List<int[]> paths = MazeUtils.dfsSolveMaze(maze, info);
//        answer = MazeUtils.pathToString(paths);
        List<String> actions = getActions(paths);


        String ansStr = actions.get(0);
        for (int i = 1; i < actions.size(); i ++) {ansStr += (", " + actions.get(i));}

        HashSet<String> set = new HashSet<>();
        set.add(ansStr);
        for (int i = 0; i < 4; i++) {
            set.add(genRandomPath(actions.size()));
        }

        List optionsList = Arrays.asList(set.toArray());

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


        for (String str : info) {
            analysis += str;
        }
        analysis = analysis + "\n\nTherefore, the right sequence of movements are: " + ansStr +
                "\nThe right option is " + answer;
    }

    public String genRandomPath(int n) {
        String directions[] = new String[]{"up","down","left","right"};
        String res = "";
        Random r = new Random();
        res += (directions[r.nextInt(directions.length)]);
        for (int i = 0; i < n; i++) {
            res += (", " + directions[r.nextInt(directions.length)]);
        }

        return res;
    }

    public static List<String> getActions(List<int[]> paths) {
        List<String> actions = new ArrayList<>();

        // 遍历坐标序列
        for (int i = 1; i < paths.size(); i++) {
            int[] current = paths.get(i);
            int[] previous = paths.get(i - 1);

            // 判断当前坐标与前一个坐标的变化，生成动作
            if (current[0] == previous[0]) {
                // 横向移动
                if (current[1] > previous[1]) {
                    actions.add("right");
                } else {
                    actions.add("left");
                }
            } else if (current[1] == previous[1]) {
                // 纵向移动
                if (current[0] > previous[0]) {
                    actions.add("down");
                } else {
                    actions.add("up");
                }
            }
        }

        return actions;
    }
}
