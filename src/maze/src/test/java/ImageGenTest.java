import com.zjt.generators.ImageGen;
import com.zjt.generators.MazeGen;
import org.junit.jupiter.api.Test;

public class ImageGenTest {

    @Test
    public void test() {

        int[][] maze = MazeGen.generateMaze(21, 21);

        int cellSize = 50;
        String savePath = "output/images/image_gen_test.png";

        ImageGen.drawMaze(maze, cellSize, savePath);
    }
}
