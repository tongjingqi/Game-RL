import asyncio
import re
from typing import List

import json

from swift.plugin import ORM, orms
from swift.utils import get_logger

logger = get_logger()


# Code borrowed from plugin/orm.py
class MathAccuracy(ORM):

    def __init__(self):
        import importlib.util
        assert importlib.util.find_spec('math_verify') is not None, (
            "The math_verify package is required but not installed. Please install it using 'pip install math_verify'.")

    def __call__(self, completions, solution, **kwargs) -> List[float]:
        from latex2sympy2_extended import NormalizationConfig
        from math_verify import LatexExtractionConfig, parse, verify
        rewards = []
        for content, sol in zip(completions, solution):
            gold_parsed = parse(sol, extraction_mode='first_match', extraction_config=[LatexExtractionConfig()])
            if len(gold_parsed) != 0:
                # We require the answer to be provided in correct latex (no malformed operators)
                answer_parsed = parse(
                    content,
                    extraction_config=[
                        LatexExtractionConfig(
                            normalization_config=NormalizationConfig(
                                nits=False,
                                malformed_operators=False,
                                basic_latex=True,
                                equations=True,
                                boxed=True,
                                units=True,
                            ),
                            # Ensures that boxed is tried first
                            boxed_match_priority=0,
                            try_extract_without_anchor=False,
                        )
                    ],
                    extraction_mode='first_match',
                )
                # Reward 1 if the content is the same as the ground truth, 0 otherwise
                reward = float(verify(answer_parsed, gold_parsed))
            else:
                # If the gold solution is not parseable, we reward 1 to skip this example
                reward = 1.0
            rewards.append(reward)
        return rewards


class MathFormat(ORM):

    def __call__(self, completions, **kwargs) -> List[float]:
        """Reward function that checks if the completion has a specific format."""
        pattern = r'^<think>.*?</think>\s*<answer>.*?</answer>(?![\s\S])'
        matches = [re.match(pattern, content, re.DOTALL | re.MULTILINE) for content in completions]
        return [1.0 if match else 0.0 for match in matches]


class CountdownORM(ORM):

    def __call__(self, completions, target, nums, **kwargs) -> List[float]:
        """
        Evaluates completions based on Mathematical correctness of the answer

        Args:
            completions (list[str]): Generated outputs
            target (list[str]): Expected answers
            nums (list[str]): Available numbers

        Returns:
            list[float]: Reward scores
        """
        rewards = []
        for completion, gt, numbers in zip(completions, target, nums):
            try:
                # Check if the format is correct
                match = re.search(r'<answer>(.*?)<\/answer>', completion)
                if match is None:
                    rewards.append(0.0)
                    continue
                # Extract the "answer" part from the completion
                equation = match.group(1).strip()
                if '=' in equation:
                    equation = equation.split('=')[0]
                # Extract all numbers from the equation
                used_numbers = [int(n) for n in re.findall(r'\d+', equation)]

                # Check if all numbers are used exactly once
                if sorted(used_numbers) != sorted(numbers):
                    rewards.append(0.0)
                    continue
                # Define a regex pattern that only allows numbers, operators, parentheses, and whitespace
                allowed_pattern = r'^[\d+\-*/().\s]+$'
                if not re.match(allowed_pattern, equation):
                    rewards.append(0.0)
                    continue

                # Evaluate the equation with restricted globals and locals
                result = eval(equation, {"__builti'ns__": None}, {})
                # Check if the equation is correct and matches the ground truth
                if abs(float(result) - float(gt)) < 1e-5:
                    rewards.append(1.0)
                else:
                    rewards.append(0.0)
            except Exception:
                # If evaluation fails, reward is 0
                rewards.append(0.0)
        return rewards


from openai import OpenAI
from typing import Dict, List, Any, Union
import re

class MultiModalAccuracyORM(ORM):
    
    @staticmethod
    def simplify_prediction(prediction):
        if "###" in prediction:
            return prediction[prediction.rindex("###"):]
        
        last_double_newline_index = prediction.rfind("\n\n")
        while last_double_newline_index != -1 and prediction[last_double_newline_index - 1] == ":":
            last_double_newline_index = prediction.rfind("\n\n", 0, last_double_newline_index)
        
        if last_double_newline_index != -1:
            return prediction[last_double_newline_index:]
        
        therefore_index = prediction.lower().rfind("therefore")
        conclusion_index = prediction.lower().rfind("conclusion")
        
        if therefore_index != -1 and conclusion_index != -1:
            return prediction[max(therefore_index, conclusion_index):]
        elif therefore_index != -1:
            return prediction[therefore_index:]
        elif conclusion_index != -1:
            return prediction[conclusion_index:]
        
        return prediction
    
    def _create_openai_client(self):
        return OpenAI(
            api_key="your-api-key-here",
            base_url="http://0.0.0.0:8075/v1",
        )
    
    def _normalize_inputs(self, completions, solution, options):
        if not isinstance(solution, list):
            solution = [solution] * len(completions)
        elif len(solution) < len(completions):
            last_sol = solution[-1] if solution else ""
            solution.extend([last_sol] * (len(completions) - len(solution)))

        if options and isinstance(options, list) and len(options) < len(completions):
            last_option = options[-1] if options else []
            options.extend([last_option] * (len(completions) - len(options)))
        
        return solution, options
    
    def _get_option_content(self, sol, current_options):
        if not (current_options and isinstance(current_options, list) and len(current_options) > 0):
            return None
            
        if not (sol.isdigit() and 1 <= int(sol) <= len(current_options)):
            return None
            
        try:
            option_index = int(sol) - 1
            option_item = current_options[option_index]
            return option_item[0] if isinstance(option_item, list) and len(option_item) > 0 else option_item
        except IndexError:
            return None
    
    def _create_evaluation_prompt(self, student_answer, sol, current_options):
        system_prompt = (
            "Compare the ground truth with the prediction from AI model and determine if the prediction is correct. "
            "The question is about an image, which we have not given here. You need to determine whether the model's prediction "
            "is consistent with the ground truth. No points will be awarded for wrong answers, over answers or under answers. "
            "There are times when the answer may have a different form of expression and some variation is acceptable."
        )
        
        option_content = self._get_option_content(sol, current_options)
        
        if option_content:
            user_content = f"## Ground Truth: The correct option is {sol}: {option_content}\n## Prediction: {student_answer}\n\nYou need to determine whether the model's prediction is consistent with the ground truth. Output only:\nCorrectness: (Yes or No)"
        elif current_options:
            user_content = f"## Ground Truth: The correct option is {sol}\n## Prediction: {student_answer}\n\nYou need to determine whether the model's prediction is consistent with the ground truth. Output only:\nCorrectness: (Yes or No)"
        else:
            user_content = f"## Ground Truth: The correct answer is {sol}\n## Prediction: {student_answer}\n\nYou need to determine whether the model's prediction is consistent with the ground truth. Output only:\nCorrectness: (Yes or No)"
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
    
    def _evaluate_with_api(self, client, messages, sol, student_answer):
        try:
            response = client.chat.completions.create(
                model="Qwen2.5-72B-Instruct-AWQ",
                messages=messages,
                max_tokens=128,
                temperature=0.0,
            )
            
            api_response = response.choices[0].message.content.strip()
            
            if re.search(r'Correctness:\s*Yes', api_response, re.IGNORECASE):
                return 1.0
            
        except Exception:
            if sol.strip().lower() in student_answer.lower():
                return 1.0
        
        return 0.0
    
    def __call__(self, completions, solution, **kwargs) -> List[float]:
        rewards = []
        options = kwargs.get("options", None)
        
        client = self._create_openai_client()
        solution, options = self._normalize_inputs(completions, solution, options)
        
        for idx, (content, sol) in enumerate(zip(completions, solution)):
            sol = str(sol) if sol is not None else ""
            
            try:
                student_answer = MultiModalAccuracyORM.simplify_prediction(content.strip())
                current_options = options[idx] if options and isinstance(options, list) and idx < len(options) else None
                
                messages = self._create_evaluation_prompt(student_answer, sol, current_options)
                reward = self._evaluate_with_api(client, messages, sol, student_answer)
                
            except Exception:
                reward = 0.0
            
            rewards.append(reward)
        
        return rewards


# ref implementation: https://github.com/huggingface/open-r1/blob/main/src/open_r1/rewards.py
class CodeReward(ORM):

    def __init__(self):
        import importlib.util
        assert importlib.util.find_spec('e2b') is not None, (
            "The e2b package is required but not installed. Please install it using 'pip install e2b-code-interpreter'."
        )
        from dotenv import load_dotenv
        load_dotenv()

    @staticmethod
    def extract_code(completion: str, language: str) -> str:
        pattern = re.compile(rf'```{language}\n(.*?)```', re.DOTALL)
        matches = pattern.findall(completion)
        extracted_answer = matches[-1] if len(matches) >= 1 else ''
        return extracted_answer

    def run_async_from_sync(self, scripts: List[str], languages: List[str]) -> List[float]:
        """Function wrapping the `run_async` function."""
        # Create a new event loop and set it
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the async function and get the result
            rewards = loop.run_until_complete(self.run_async(scripts, languages))
        finally:
            loop.close()

        return rewards

    async def run_async(self, scripts: List[str], languages: List[str]) -> List[float]:
        from e2b_code_interpreter import AsyncSandbox

        # Create the sandbox by hand, currently there's no context manager for this version
        try:
            sbx = await AsyncSandbox.create(timeout=30, request_timeout=3)
        except Exception as e:
            logger.warning(f'Error from E2B executor: {e}')
            return [0.0] * len(scripts)
        # Create a list of tasks for running scripts concurrently
        tasks = [self.run_script(sbx, script, language) for script, language in zip(scripts, languages)]

        # Wait for all tasks to complete and gather their results as they finish
        results = await asyncio.gather(*tasks)
        rewards = list(results)  # collect results

        # Kill the sandbox after all the tasks are complete
        await sbx.kill()

        return rewards

    async def run_script(self, sbx, script: str, language: str) -> float:
        try:
            execution = await sbx.run_code(script, language=language, timeout=30)
        except Exception as e:
            logger.warning(f'Error from E2B executor: {e}')
            return 0.0
        try:
            return float(execution.text)
        except (TypeError, ValueError):
            return 0.0

    def __call__(self, completions, **kwargs) -> List[float]:
        """Reward function that evaluates code snippets using the E2B code interpreter.

        Assumes the dataset contains a `verification_info` column with test cases.
        """
        evaluation_script_template = """
        import subprocess
        import json

        def evaluate_code(code, test_cases):
            passed = 0
            total = len(test_cases)
            exec_timeout = 5

            for case in test_cases:
                process = subprocess.run(
                    ["python3", "-c", code],
                    input=case["input"],
                    text=True,
                    capture_output=True,
                    timeout=exec_timeout
                )

                if process.returncode != 0:  # Error in execution
                    continue

                output = process.stdout.strip()
                if output.strip() == case["output"].strip():
                    passed += 1

            success_rate = (passed / total)
            return success_rate

        code_snippet = {code}
        test_cases = json.loads({test_cases})

        evaluate_code(code_snippet, test_cases)
        """
        verification_info = kwargs['verification_info']
        languages = [info['language'] for info in verification_info]
        code_snippets = [
            self.extract_code(completion, language) for completion, language in zip(completions, languages)
        ]
        scripts = [
            evaluation_script_template.format(
                code=json.dumps(code), test_cases=json.dumps(json.dumps(info['test_cases'])))
            for code, info in zip(code_snippets, verification_info)
        ]
        try:
            rewards = self.run_async_from_sync(scripts, languages)

        except Exception as e:
            logger.warning(f'Error from E2B executor: {e}')
            rewards = [0.0] * len(completions)

        return rewards


class CodeFormat(ORM):

    def __call__(self, completions, **kwargs) -> List[float]:
        verification_info = kwargs['verification_info']
        rewards = []
        for content, info in zip(completions, verification_info):
            pattern = r'^<think>.*?</think>\s*<answer>.*?```{}.*?```.*?</answer>(?![\s\S])'.format(info['language'])
            match = re.match(pattern, content, re.DOTALL | re.MULTILINE)
            reward = 1.0 if match else 0.0
            rewards.append(reward)
        return rewards


orms['external_math_acc'] = MathAccuracy
orms['external_math_format'] = MathFormat
orms['external_countdown'] = CountdownORM
orms['external_r1v_acc'] = MultiModalAccuracyORM
orms['external_code_reward'] = CodeReward
orms['external_code_format'] = CodeFormat
