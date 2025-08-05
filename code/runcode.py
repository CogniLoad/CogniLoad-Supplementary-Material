import json
import os
import time
from openai import OpenAI
from tqdm import tqdm
import re
import threading
import queue

# ==================== Configuration (edit as needed) ====================
# MODEL_CONFIGURATIONS = [
#     {
#         "name": "Qwen3-235B-A22B",  # This will be used in the output filename
#         "model_id": "Qwen/Qwen3-235B-A22B",
#         "enable_thinking": True
#     }
# ]
MODEL_CONFIGURATIONS = [
    # {
    #     "name": "Qwen3-32B",  # This will be used in the output filename
    #     "model_id": "Qwen/Qwen3-32B",
    #     "enable_thinking": True
    # }
    {
        "name": "Qwen3-235B-A22B",  # This will be used in the output filename
        "model_id": "Qwen/Qwen3-235B-A22B",
        "enable_thinking": True
    }
    # {
    #     "name": "DeepSeek-R1-Distill-Qwen-32B",  # This will be used in the output filename
    #     "model_id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    #     "enable_thinking": True
    # }
]

# Actual keys are omitted for security.
api_keys = ["<REDACTED>"] * 30  # Replace with real keys before use.

INPUT_DIR  = "aaai-database"
OUTPUT_DIR = "amb-results"

FILES_TO_PROCESS = [
    "ambiguity-1-choicequestions.json"
    # 'contradictory-1-choicequestions.json',
    # 'contradictory-2-choicequestions.json',
    # 'contradictory-3-choicequestions.json',
    # 'contradictory-4-choicequestions.json',
]

MAX_THREADS = 4
# ======================================================================


def create_prompt(question_data):
    full_question_text = question_data.get("question", "")
    return f"""
你是一位顶级的数学解题专家，擅长解决各种高考数学题。请仔细阅读下面的单项选择题，并提供你的最终答案和详细、严谨的解题步骤。
        你的回答必须严格遵循以下JSON格式，不要在JSON代码块前后添加任何额外的解释或文本。
        {{
          "answer": "你的答案选项 (例如: A, B, C, or D)",
          "reasoning": "你得出这个答案的详细推理过程和解题步骤分析。"
        }}
        --- 问题开始 ---
        {full_question_text}
        --- 问题结束 ---
        请提供你的JSON格式的回答:
    """
# You are an expert high-school math solver. Read the following multiple-choice question carefully and return your final answer along with a detailed, rigorous solution.
# Return ONLY the following JSON format; do not include any surrounding text or markdown fences:
# {{
#   "answer": "your choice (A, B, C, or D)",
#   "reasoning": "step-by-step derivation and justification"
# }}
# --- Question starts ---
# {full_question_text}
# --- Question ends ---
# JSON response:


def clean_and_parse_json(model_output_str):
    fixed_str = model_output_str.replace('\\', '\\\\')
    if '```json' in fixed_str:
        start = fixed_str.find('```json') + len('```json')
        end   = fixed_str.rfind('```')
    else:
        start = fixed_str.find('{')
        end   = fixed_str.rfind('}')

    if start != -1 and end != -1:
        json_str = fixed_str[start:end + 1].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed after escaping backslashes: {e}")
            print(f"Attempted string: {json_str[:500]}...")
            raise
    else:
        raise json.JSONDecodeError("No valid JSON object found in model output.", model_output_str, 0)


def process_single_file_with_model(input_file, output_file, model_config):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"Loaded: {os.path.basename(input_file)} ({len(questions)} questions)")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: Cannot read or parse {input_file}. {e}")
        return

    model_name      = model_config["name"]
    model_id        = model_config["model_id"]
    enable_thinking = model_config.get("enable_thinking", False)
    print(f"Results will be written to: {output_file}")

    results, completed_ids = [], set()
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            completed_ids = {r.get('original_id') for r in results if r.get('original_id')}
            print(f"Resumed progress: loaded {len(completed_ids)} already processed questions")
        except (json.JSONDecodeError, FileNotFoundError):
            results, completed_ids = [], set()

    current_key_index = 0
    questions_to_process = [
        q for q in questions
        if f"{q.get('year')}-{q.get('number')}" not in completed_ids
    ]
    progress = tqdm(questions_to_process, desc=f"Model: {model_name}")

    for q in progress:
        year, number = q.get("year"), q.get("number")
        if year is None or number is None:
            continue
        question_id = f"{year}-{number}"

        full_prompt = create_prompt(q)
        success = False

        while True:
            if current_key_index >= len(api_keys):
                print("\nAll API keys exhausted, aborting.")
                break

            api_key = api_keys[current_key_index]
            try:
                progress.set_postfix_str(f"ID {question_id}, key idx {current_key_index}")
                client = OpenAI(
                    base_url="https://api-inference.modelscope.cn/v1/",
                    api_key=api_key
                )

                model_output = ""
                inner_reasoning = ""

                if enable_thinking:
                    stream = client.chat.completions.create(
                        model=model_id,
                        messages=[{"role": "user", "content": full_prompt}],
                        stream=True,
                        extra_body={"enable_thinking": True}
                    )
                    print(f"\n--- Reasoning trace for {question_id} ---")
                    for chunk in stream:
                        reasoning_chunk = chunk.choices[0].delta.reasoning_content or ""
                        answer_chunk    = chunk.choices[0].delta.content or ""
                        if reasoning_chunk:
                            inner_reasoning += reasoning_chunk
                            print(reasoning_chunk, end='', flush=True)
                        if answer_chunk:
                            model_output += answer_chunk
                    print(f"\n--- Final answer for {question_id} ---\n{model_output}")
                else:
                    resp = client.chat.completions.create(
                        model=model_id,
                        messages=[{"role": "user", "content": full_prompt}],
                        extra_body={"enable_thinking": False}
                    )
                    model_output = resp.choices[0].message.content

                model_reasoning_from_json = model_output
                model_answer = "ERROR"
                try:
                    parsed = clean_and_parse_json(model_output)
                    model_answer = parsed.get("answer", "PARSE_ERROR")
                except json.JSONDecodeError as e:
                    print(f"\nJSON parsing failed for {question_id}: {e}")
                    match = re.search(r'"answer"\s*:\s*"([A-D])"', model_output, re.IGNORECASE)
                    if match:
                        model_answer = match.group(1).upper()
                        print(f"Fallback extraction succeeded: {model_answer}")
                    else:
                        print("Fallback extraction failed.")

                correct_answer = q.get("answer")
                is_correct = (
                    model_answer and correct_answer and
                    model_answer.strip().upper() == correct_answer.strip().upper()
                )

                results.append({
                    "original_id": question_id,
                    "original_question": q.get("question"),
                    "model_answer": model_answer,
                    "model_reasoning": model_reasoning_from_json,
                    "correct_answer": correct_answer,
                    "inner_reasoning": inner_reasoning,
                    "is_correct": is_correct
                })
                success = True
                break

            except Exception as e:
                err = str(e).lower()
                if '401' in err or '429' in err or 'insufficient_quota' in err:
                    print(f"\nKey index {current_key_index} failed; rotating...")
                    current_key_index += 1
                    time.sleep(1)
                else:
                    print(f"\nUnhandled error for {question_id}: {e}")
                    break

        if not success:
            print(f"\nProcessing failed for {question_id}")
            results.append({
                "original_id": question_id,
                "original_question": q.get("question"),
                "model_answer": "ERROR",
                "model_reasoning": "Processing failed",
                "correct_answer": q.get("answer"),
                "inner_reasoning": "",
                "is_correct": False
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\nModel {model_name} finished processing {os.path.basename(input_file)}")


def worker(task_queue):
    while True:
        task = task_queue.get()
        if task is None:
            break
        input_path, output_path, model_cfg = task
        print(f"\nThread {threading.current_thread().name} processing {os.path.basename(input_path)}")
        process_single_file_with_model(input_path, output_path, model_cfg)
        task_queue.task_done()


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Starting batch processing.")
    print(f"Input directory:  {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    task_queue = queue.Queue()
    threads = []

    for i in range(MAX_THREADS):
        t = threading.Thread(target=worker, args=(task_queue,), name=f"Worker-{i+1}")
        t.start()
        threads.append(t)

    for cfg in MODEL_CONFIGURATIONS:
        model_name = cfg["name"]
        enable_thinking = cfg.get("enable_thinking", False)
        print("\n" + "=" * 80)
        print(f"Model: {model_name} (thinking: {enable_thinking})")
        print("=" * 80)

        for filename in FILES_TO_PROCESS:
            in_path = os.path.join(INPUT_DIR, filename)
            if not os.path.exists(in_path):
                print(f"Warning: {in_path} not found, skipping.")
                continue

            m = re.search(r'ambiguity-(\d+)', filename)
            repetition = m.group(1) if m else '0'
            thinking_str = "true" if enable_thinking else "false"
            out_filename = f"ambiguity-{repetition}-{model_name}-{thinking_str}-choiceanswer.json"
            out_path = os.path.join(OUTPUT_DIR, out_filename)

            task_queue.put((in_path, out_path, cfg))

    task_queue.join()

    for _ in range(MAX_THREADS):
        task_queue.put(None)
    for t in threads:
        t.join()

    print("\nAll tasks finished.")