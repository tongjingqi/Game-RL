package com.zjt.utils;

import java.io.File;

public class FileUtils {
    /**
     * Initialize output directories, ensure directories exist, and clear the contents of the image directory.
     *
     * @param outputDir The main output directory.
     * @param imagesDir The directory for images.
     * @param statesDir The directory for state files.
     */
    public static void setupOutputDirectories(String outputDir, String imagesDir, String statesDir) {
        createDirectory(outputDir);
        createDirectory(imagesDir);
        cleanDirectory(imagesDir);
        createDirectory(statesDir);
        cleanDirectory(statesDir);
    }

    /**
     * Create a directory (if it does not exist).
     *
     * @param dirPath The path of the directory.
     */
    public static void createDirectory(String dirPath) {
        File dir = new File(dirPath);
        if (!dir.exists() && !dir.mkdirs()) {
            System.err.println("Failed to create directory: " + dirPath);
        }
    }

    /**
     * Clear the contents of a directory.
     *
     * @param dirPath The path of the directory.
     */
    public static void cleanDirectory(String dirPath) {
        File dir = new File(dirPath);
        if (dir.exists() && dir.isDirectory()) {
            for (File file : dir.listFiles()) {
                deleteRecursively(file);
            }
        }
    }

    /**
     * Recursively delete a file or directory.
     *
     * @param file The file or directory to delete.
     */
    public static void deleteRecursively(File file) {
        if (file.isDirectory()) {
            for (File subFile : file.listFiles()) {
                deleteRecursively(subFile);
            }
        }
        if (!file.delete()) {
            System.err.println("Failed to delete file: " + file.getAbsolutePath());
        }
    }
}

