import com.zjt.generators.DataGen;
import com.zjt.templates.BaseTemplate;
import org.junit.jupiter.api.Test;

import java.util.List;

public class DataGenTest {

    @Test
    public void test() {
        int[][] maze = {
                {1, 1, 1, 1, 1},
                {1, 2, 0, 0, 1},
                {1, 0, 1, 0, 1},
                {1, 0, 0, 3, 1},
                {1, 1, 1, 1, 1}
        };

        List<BaseTemplate> questionsAndAnswers = DataGen.generateJsonData(maze,1);

        // 保存到 JSON 文件
        String filePath = "maze_questions_and_answers.json";
        DataGen.saveDataToJson(questionsAndAnswers, filePath);
    }
}
