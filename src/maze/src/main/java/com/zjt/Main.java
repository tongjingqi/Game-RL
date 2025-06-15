package com.zjt;

import com.zjt.constants.MazeConstants;
import com.zjt.constants.RulesConstants;
import com.zjt.generators.DataGen;
import com.zjt.templates.BaseTemplate;
import com.zjt.utils.FileUtils;

import java.util.ArrayList;
import java.util.List;


public class Main {

    public static void main(String[] args) {
        if (args.length != 4) {
            System.err.println("Missing parameter");
            System.exit(1);
        }


        String outputDir = args[0];
        String imagesDir = outputDir + "/" + MazeConstants.IMAGES_DIR;
        String statesDir = outputDir + "/" + MazeConstants.STATES_DIR;
        String dataFilePath = outputDir + "/" + MazeConstants.DATA_PATH;


        FileUtils.setupOutputDirectories(outputDir, imagesDir, statesDir);

        // Parse the counts for each maze size
        int[] counts = new int[RulesConstants.ALLOWED_SIZES.length];
        for (int i = 0; i < RulesConstants.ALLOWED_SIZES.length; i++) {
            String countStr = args[i + 1];
            try {
                int count = Integer.parseInt(countStr);
                if (count < 0) {
                    System.err.println("Error: Count must be a non-negative integer. Provided count: " + count);
                    System.exit(1);
                }
                counts[i] = count;
            } catch (NumberFormatException e) {
                System.err.println("Error: Count must be an integer. Provided input: " + countStr);
                System.exit(1);
            }
        }

        // Generate data and save to JSON
        List<BaseTemplate> data = new ArrayList<>();
        int startId = 0;

        for (int i = 0; i < RulesConstants.ALLOWED_SIZES.length; i++) {
            int size = RulesConstants.ALLOWED_SIZES[i];
            int count = counts[i];
            String label = RulesConstants.SIZE_LABELS[i];
            if (count > 0) {
                System.out.println("Generating " + count + " " + label + " mazes...");
                data.addAll(DataGen.generateData(startId, count, size, imagesDir, statesDir));
                startId += count;
            }
        }

        DataGen.saveDataToJson(data, dataFilePath);

        System.out.println("Data generation completed. Output directory: " + outputDir);
    }
}
