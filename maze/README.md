# Maze Q&A Generator



## Introduction

This is a Maze Q&A Generator. It generates mazes and corresponding Q&A datasets for different question types.

**Rules:**

1. This is a mini maze game. The player must navigate through the maze, avoid obstacles, and reach the goal to win.  
2. The **red circle** represents the player, the **green block** is the goal, and the **blue blocks** are obstacles.  
3. The player can only move on the **white blocks**.

**Maze Sizes:**

- **Small:** 9 x 9  
- **Medium:** 11 x 11  
- **Large:** 13 x 13  

**Registered Question Templates:**  

- **AvailableDirections:** Ask for the directions the player can currently move in.  
- **FindPathToGoal:** Find the path from the player’s position to the goal.  
- **GoalPosition:** Locate the position of the goal.  
- **PlayerPosition:** Locate the player’s current position.  
- **PositionAfterMoving:** Determine the player’s position after making a move.  
- **TurnCount:** Count how many moves are needed to reach the goal.  



## Structure

```
maze/
├── src/                  # Source code and test directory.
│   ├── main/../zjt       # Main application source code directory.
│   │   ├── constants/    # Directory for constant values used throughout the project.
│   │   ├── generators/   # Directory for data generators.
│   │   ├── templates/    # Directory for QA template files.
│   │   ├── utils/        # Utility classes and helper functions.
│   │   └── Main.java     # Main application entry point.
│   ├── test/             # Directory for test files.
├── maze_dataset_example/ 
├── build.gradle          # Gradle build script.
├── settings.gradle       # Gradle settings file.
├── gradlew               # Gradle wrapper script for UNIX-based systems.
├── gradlew.bat           # Gradle wrapper script for Windows-based systems.
├── gradle/               # Gradle wrapper files directory.
├── README.md             
├── ...
```



## Dependencies

jdk (version 8 or higher)

## Build and Run

### Step 1:  
Check if your system has a jdk installed by running:  

```bash
javac -version
```

If not, install the required jdk (version 8 or higher) .

For example:

```bash
sudo apt install openjdk-8-jdk-headless
```

### Step 2:  

Enter the root directory

```
cd maze
```

**Build command:**

```bash
./gradlew build
```

The first build may take some time because Gradle will download all project dependencies from remote repositories and the Gradle Wrapper's specified version, which can result in a longer build process.

**Run command:**

```
./gradlew run 
```

This command needs four parameters :
1. Output directory  
2. Number of small mazes to generate  
3. Number of medium mazes to generate  
4. Number of large mazes to generate  

For example:

```bash
./gradlew run --args="maze_dataset_example 1 1 1"
```

This will generate one small maze, one medium maze, and one large maze in the folder `maze_dataset_example`.

Each maze will generate all types of questions.

```bash
./gradlew run --args="maze_dataset 60 30 10"
```

This will generate 60 small mazes, 30 medium mazes, and 10 large mazes in the folder `maze_dataset`.

