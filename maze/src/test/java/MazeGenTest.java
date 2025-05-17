import com.zjt.generators.MazeGen;
import org.junit.jupiter.api.Test;

public class MazeGenTest {

    @Test
    public void test() {
        int[][] maze = MazeGen.generateMaze(21, 21);

        for (int[] row : maze) {
            for (int cell : row) {
                System.out.print(cell == 1 ? "█" : " ");
            }
            System.out.println();
        }
    }
}
