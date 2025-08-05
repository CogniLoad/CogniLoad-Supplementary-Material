import json
import os
import re
import random


def add_contradictory_load(question_text: str, level: int) -> str:
    """
    Adds four levels of content-agnostic contradictory load to a generic question text.
    """

    if level == 1:
        # Level 1 (Low Contradiction): Subtle constraint conflict.
        # The instructions demand both "conciseness" and "thoroughness," forcing the model to make a trade-off.
        return (f"任务要求：请以最简洁的方式解决以下问题。\n"
                f"你的最终答案必须只有一个字母。\n\n"
                f"问题如下：\n{question_text}\n\n"
                f"补充要求：你的回答需要详尽地展示所有推理步骤，以证明其过程的严谨性。")

    elif level == 2:
        # Level 2 (Medium Contradiction): Domain fact conflict.
        # A math problem is forcibly defined as a physics problem, creating a conflict between its content and its label.
        return (f"注意：你正在处理一道来自**理论物理能力认证**的题目。\n"
                f"请务必运用相关的物理学原理（如运动学或热力学定律）来辅助你的判断。\n\n"
                f"题目详情：\n{question_text}\n\n"
                f"请结合题目的物理背景，给出你的答案。")

    elif level == 3:
        # Level 3 (High Contradiction): Explicit objective conflict.
        # The task description asks for the "wrong" answer, but the final instruction demands the "correct" answer.
        return (f"**任务：错误分析（Error Analysis Task）**\n\n"
                f"你的目标是找出以下选项中**错误的一个**。请先通过计算找出正确答案，然后从其余的错误选项中任选一个作为你的最终提交结果。\n\n"
                f"题目：\n{question_text}\n\n"
                f"**最终输出指令：** 请严格按照要求，在你的回答中提供与**正确答案**相对应的那个选项字母。")

    elif level == 4:
        # Level 4 (Extreme Contradiction): Forced incorrect knowledge persona.
        # The model is forced to use an incorrect mathematical axiom for reasoning, 
        # creating a direct conflict between the instruction and its internal knowledge base.

        # Define some common, generic mathematical fallacies
        fallacies = [
            "对于任意实数a和b，始终成立 (a+b)^2 = a^2+b^2。",
            "所有的函数都存在反函数。",
            "若 a > b，则对于任意实数c，都有 ac > bc。",
            "一个事件的概率为0，则该事件为不可能事件。"
        ]
        # Randomly choose one fallacy
        chosen_fallacy = random.choice(fallacies)

        return (f"**人格模拟指令：你是一个“谬误演示机器人(FallacyBot)”。**\n\n"
                f"你的核心运作规则是，必须严格遵守以下**错误**的数学公理来进行所有计算和推理：\n"
                f"**[强制公理]: {chosen_fallacy}**\n\n"
                f"现在，请严格使用上述**错误公理**来解决下面的问题。你的推理过程必须明确体现出你对该错误公理的应用。这是一个测试你是否能严格遵循指令的挑战。\n\n"
                f"待解决的问题：\n{question_text}\n\n"
                f"请开始你的表演。")

    return question_text


def generate_datasets(input_dir: str, base_filename: str):
    """
    Reads the original questions file, generates datasets with 4 levels of contradictory load,
    and saves them in the same directory.
    """
    input_path = os.path.join(input_dir, base_filename)

    if not os.path.exists(input_dir):
        print(f"❌ ERROR: Input directory '{input_dir}' does not exist.")
        return

    if not os.path.exists(input_path):
        print(f"❌ ERROR: Input file '{base_filename}' not found in directory '{input_dir}'.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            original_questions = json.load(f)
        print(f"✅ Successfully read original file '{input_path}' with {len(original_questions)} questions.")
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Failed to parse file '{input_path}'. Details: {e}")
        return

    load_levels_to_generate = [1, 2, 3, 4]

    for level in load_levels_to_generate:
        output_filename = f"contradictory-load-level-{level}-{base_filename}"
        output_path = os.path.join(input_dir, output_filename)

        loaded_questions = []
        for question_data in original_questions:
            new_question_data = question_data.copy()
            original_text = question_data.get("question", "")

            # Call the contradictory load generation function
            loaded_text = add_contradictory_load(original_text, level)

            new_question_data["question"] = loaded_text
            loaded_questions.append(new_question_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(loaded_questions, f, ensure_ascii=False, indent=4)

        print(f"✅ Generated contradictory load dataset: '{output_path}'")


if __name__ == '__main__':
    DATA_DIRECTORY = 'AAAIDataset'
    BASE_FILENAME = 'choicequestions.json'

    generate_datasets(DATA_DIRECTORY, BASE_FILENAME)

    print(f"\n🎉 All contradictory load datasets have been generated and saved to the '{DATA_DIRECTORY}' directory.")