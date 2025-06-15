package com.zjt.generators;

import com.zjt.constants.MazeConstants;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;


public class ImageGen {

    public ImageGen() {
    }

    /**
     * Draw the maze and save it as an image.
     *
     * @param maze     The maze array.
     * @param cellSize The size of each cell (in pixels).
     * @param savePath The path to save the image.
     */
    public static void drawMaze(int[][] maze, int cellSize, String savePath) {
        // Dynamically calculate the width and height of the image
        int mazeWidth = maze[0].length * cellSize;
        int mazeHeight = maze.length * cellSize;
        int imageWidth = mazeWidth + 100;
        int imageHeight = mazeHeight + 100;

        // Calculate left margin to center the maze horizontally
        int LEFT_PADDING = (imageWidth - mazeWidth) / 2;
        int TOP_PADDING = 50; // Fixed top margin

        // Create a BufferedImage object
        BufferedImage image = new BufferedImage(imageWidth, imageHeight, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2d = image.createGraphics();
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Fill the background with white
        g2d.setColor(Color.WHITE);
        g2d.fillRect(0, 0, imageWidth, imageHeight);

        // Draw row and column labels
        g2d.setFont(new Font("Arial", Font.PLAIN, 20));
        g2d.setColor(Color.BLACK);
        for (int i = 0; i < maze.length; i++) {
            // Draw row labels (left side)
            int labelX = LEFT_PADDING - 30; // Left offset
            int labelY = TOP_PADDING + i * cellSize + cellSize / 2 + 5; // Center position of each cell
            g2d.drawString(String.valueOf(i), labelX, labelY);
        }
        for (int j = 0; j < maze[0].length; j++) {
            // Draw column labels (top side)
            int labelX = LEFT_PADDING + j * cellSize + cellSize / 2 - 5; // Center position of each cell
            int labelY = TOP_PADDING - 10; // Top offset
            g2d.drawString(String.valueOf(j), labelX, labelY);
        }

        // Draw the maze cells
        for (int row = 0; row < maze.length; row++) {
            for (int col = 0; col < maze[row].length; col++) {
                int x = LEFT_PADDING + col * cellSize;
                int y = TOP_PADDING + row * cellSize;

                switch (maze[row][col]) {
                    case MazeConstants.EMPTY_CELL:
                        g2d.setColor(Color.WHITE);
                        g2d.fillRect(x, y, cellSize, cellSize);
                        break;
                    case MazeConstants.WALL_CELL:
                        g2d.setColor(new Color(173, 216, 230));
                        g2d.fillRect(x, y, cellSize, cellSize);
                        break;
                    case MazeConstants.PLAYER_CELL:
                        g2d.setColor(Color.WHITE);
                        g2d.fillRect(x, y, cellSize, cellSize);
                        g2d.setColor(Color.RED);
                        g2d.fillOval(x + cellSize / 4, y + cellSize / 4, cellSize / 2, cellSize / 2);
                        break;
                    case MazeConstants.GOAL_CELL:
                        g2d.setColor(Color.GREEN);
                        g2d.fillRect(x, y, cellSize, cellSize);
                        break;
                }

                // Draw grid lines
                g2d.setColor(Color.LIGHT_GRAY);
                g2d.drawRect(x, y, cellSize, cellSize);
            }
        }

        g2d.dispose();

        try {
            File outputFile = new File(savePath);
            ImageIO.write(image, "png", outputFile);
        } catch (IOException e) {
            System.err.println("image save error: " + e.getMessage());
        }
    }
}


