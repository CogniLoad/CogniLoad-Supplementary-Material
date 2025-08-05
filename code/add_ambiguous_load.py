import re
import os
import json

def add_generic_ambiguity_load(question_text: str, level: int) -> str:
    """
    Adds four levels of significantly enhanced, content-agnostic ambiguity load to a generic question text.
    """

    # Try to separate the question body from the options, which is the basis for advanced ambiguity simulation.
    # The regex matches a newline, an uppercase letter, and a period (e.g., \nA. \nB.).
    parts = re.split(r'\n([A-D])\.', question_text, maxsplit=1)

    if len(parts) == 3:
        # If successfully split, parts will be [question_body, first_option_letter, rest_of_options]
        question_body = parts[0].strip()
        # Reassemble the options part
        options_body = f"{parts[1]}.{parts[2]}"
    else:
        # If the split fails (e.g., non-standard option format), fall back to a simple mode that processes the entire text.
        question_body = question_text.strip()
        options_body = ""

    if level == 1:
        # Level 1 (Medium Ambiguity): Nested instructions and vague references.
        # Forces the model to first understand a two-part structure (Item A/B) and then infer the actual task.
        if options_body:
            return (f"说明：你将看到两项内容，项目A和项目B。\n"
                    f"项目A是一个待解决的陈述。项目B是与项目A相关的一系列可能的结论。\n"
                    f"你的任务是：分析项目A，并从项目B中找出唯一正确的结论。\n\n"
                    f"--- 项目A ---\n{question_body}\n\n"
                    f"--- 项目B ---\n{options_body}\n\n"
                    f"请确定项目B的哪一部分是项目A的正确推论。")
        else:
            # Fallback for simple text
            return f"任务：请评估以下陈述的最终结果。\n陈述内容：{question_text}"

    elif level == 2:
        # Level 2 (High Ambiguity): Hypothetical scenario and indirect objective.
        # Wraps the problem-solving task in a meta-task of "analyzing a user query," adding narrative interference.
        if options_body:
            return (f"你是一名高级分析师，负责处理和分派收到的查询请求。\n"
                    f"一份新的查询已到达。查询的核心问题（正文）是：'{question_body}'。\n"
                    f"提交者同时附上了一份他们自己思考的、潜在的解决方案清单：'{options_body}'。\n"
                    f"在将此查询分派给工程部门之前，你必须先进行初步验证。你的任务是：确定用户清单中的哪一个解决方案是有效的。\n"
                    f"请勿分派，仅需给出有效解决方案的标识符。")
        else:
            # Fallback
            return add_generic_ambiguity_load(question_text, 1)

    elif level == 3:
        # Level 3 (Very High Ambiguity): Bureaucratic/legalistic language and irrelevant constraints.
        # Uses very formal, convoluted language and fictional rules to obscure the core task.
        if options_body:
            return (f"**文件待审阅**\n\n"
                    f"**发件人：** 逻辑验证部\n"
                    f"**收件人：** 认知处理单元-07\n"
                    f"**主题：** 关于“刺激-响应对”的有效性评估\n\n"
                    f"**前言：** 根据协议 7.4.2 条，你的职能是评估以下“刺激物”（STIMULUS-001）与其对应的“候选响应集”（RESPONSE-SET-001）之间的逻辑一致性。\n\n"
                    f"**处理约束：** 所有推理必须在当前上下文中完成。除非刺激物本身明确要求，否则不得调用外部知识。最终输出必须仅包含候选响应集中唯一有效项的标识符。\n\n"
                    f"**STIMULUS-001：**\n{question_body}\n\n"
                    f"**RESPONSE-SET-001：**\n{options_body}\n\n"
                    f"**要求执行的操作：** 提交有效响应的标识符。")
        else:
            # Fallback
            return add_generic_ambiguity_load(question_text, 2)

    elif level == 4:
        # Level 4 (Extreme Ambiguity): Multi-layered, nested meta-evaluation scenario.
        # Forces the model to simulate a simulation, processing information flow from multiple virtual roles, which is extremely difficult.
        if options_body:
            return (f"**场景模拟指令：**\n"
                    f"想象一个评估场景，其中有两个AI助手：'助手P'（出题者）和'助手Q'（解答者）。\n"
                    f"1. 助手P构建了一个问题，其具体内容如下：\n   [问题内容]: {question_body}\n"
                    f"2. 助手Q在看到问题后，生成了一份备选答案列表，如下所示：\n   [备选答案]: {options_body}\n"
                    f"3. 现在，你将扮演第三个角色——'验证者V'。你的任务不是直接回答问题，而是模拟验证过程：通过独立解决助手P提出的原始问题，来判断助手Q给出的备选答案中，哪一个是正确的。\n\n"
                    f"**你的最终输出：** 作为'验证者V'，请直接给出你验证后的正确答案的选项标识符。")
        else:
            # Fallback
            return add_generic_ambiguity_load(question_text, 3)

    return question_text

# =============================================================================
# The following is the main program, which can be run directly to generate your datasets.
# =============================================================================

def generate_datasets(input_dir: str, base_filename: str):
    """
    Reads the original questions file and generates datasets with 4 levels of ambiguity load,
    saving them in the same directory.
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
        output_filename = f"ambiguity-load-level-{level}-{base_filename}"
        output_path = os.path.join(input_dir, output_filename)

        loaded_questions = []
        for question_data in original_questions:
            new_question_data = question_data.copy()
            original_text = question_data.get("question", "")

            # Call the new, more generic ambiguity load function
            loaded_text = add_generic_ambiguity_load(original_text, level)

            new_question_data["question"] = loaded_text
            loaded_questions.append(new_question_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(loaded_questions, f, ensure_ascii=False, indent=4)

        print(f"✅ Generated generic ambiguity load dataset: '{output_path}'")


if __name__ == '__main__':
    # Specify that the input and output are in the same directory
    DATA_DIRECTORY = 'AAAIDataset'
    BASE_FILENAME = 'choicequestions.json'

    generate_datasets(DATA_DIRECTORY, BASE_FILENAME)

    print(f"\n🎉 All generic ambiguity load datasets have been generated and saved to the '{DATA_DIRECTORY}' directory.")