import json
import os
import time
from openai import OpenAI
from tqdm import tqdm
import re
from typing import List, Dict, Any

# ==================== CONFIGURATION ====================
# ⭐ Optimization Switch! Set to True to enable the COF framework, False to run the original baseline code.
USE_COF_FRAMEWORK = True

MODEL_CONFIGURATIONS = [
    {
        "name": "Qwen3-235B-A22B",
        "model_id": "Qwen/Qwen3-235B-A22B",
        "enable_thinking": True # This config is now used in the filename
    }
]

api_keys = [
    '3748a5b5-e430-429f-99cb-5d235447f62', '3748a5b5-e430-429f-99cb-5d235447f62',
] # api_keys = ["<REDACTED>"] * 30  # Replace with real keys before use.

INPUT_DIR = "aaai-database"
# ⭐ Output directory now changes dynamically based on the switch
OUTPUT_DIR = "AAAIresults_COF" if USE_COF_FRAMEWORK else "AAAIresults_Baseline"

FILES_TO_PROCESS = [
    'choicequestions.json',
    'contradictory-load-level-1-choicequestions.json',
    'contradictory-load-level-2-choicequestions.json',
    'contradictory-load-level-3-choicequestions.json',
    'contradictory-load-level-4-choicequestions.json'
]

# ==================== COF FRAMEWORK DEFINITION ====================

class CollectiveMemoryStore:
    """Dynamic Collective Memory Store (S_t)"""
    def __init__(self):
        self.state = {}

    def update(self, new_insights: List[str], time_step: int):
        self.state[f"step_{time_step}"] = new_insights
        return self.state

class GenericAgent:
    """Generic Agent A_i"""
    def __init__(self, agent_id: Any, client: OpenAI, model_id: str, enable_thinking: bool):
        self.id = agent_id
        self.client = client
        self.model_id = model_id
        self.enable_thinking = enable_thinking

    def generate(self, prompt: str) -> str:
        try:
            # Differentiate whether to enable streaming output and thinking process
            if self.enable_thinking:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    extra_body={"enable_thinking": True}
                )
                model_output = ""
                for chunk in response:
                    answer_chunk = chunk.choices[0].delta.content or ""
                    model_output += answer_chunk
                return model_output
            else:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[{"role": "user", "content": prompt}],
                    extra_body={"enable_thinking": False}
                )
                return response.choices[0].message.content
        except Exception as e:
            # Add a short delay to prevent API rejection from too many rapid requests
            time.sleep(1)
            print(f"   - Agent {self.id} API call failed: {e}")
            return f"Error in Agent {self.id}: {e}"

class CognitiveOrchestrator:
    """Central Cognitive Orchestrator (O)"""
    def __init__(self, client: OpenAI, model_id: str, enable_thinking: bool):
        self.agent = GenericAgent(agent_id="Orchestrator", client=client, model_id=model_id, enable_thinking=enable_thinking)

    def decompose_task(self, query: str, num_agents: int) -> List[str]:
        prompt = (f"You are a task decomposition expert. Analyze the following complex query and break it down into "
                  f"{num_agents} distinct, complementary, and specialized thinking styles or sub-tasks that a team of agents can work on in parallel. "
                  f"Provide your answer ONLY as a JSON list of strings. For example: [\"Style 1\", \"Style 2\"].\n\n"
                  f"QUERY:\n{query}")
        response_str = self.agent.generate(prompt)
        try:
            # Try to extract the JSON part from the model's returned text
            match = re.search(r'\[.*\]', response_str, re.DOTALL)
            if match:
                styles = json.loads(match.group(0))
                if isinstance(styles, list) and len(styles) == num_agents:
                    return styles
        except (json.JSONDecodeError, TypeError):
            pass
        # If JSON parsing fails, return a list of generic styles
        print("   - Orchestrator failed to parse JSON for styles, using default.")
        return [f"Analytical Style {i+1}" for i in range(num_agents)]

    def synthesize_answer(self, query: str, final_outputs: List[str], final_memory_state: Dict) -> str:
        prompt = (f"You are an expert synthesizer. Your task is to generate a final, high-quality answer for the original query based on the collective work of a team of agents. "
                  f"Adhere strictly to the required JSON output format.\n\n"
                  f"ORIGINAL QUERY:\n{query}\n\n"
                  f"FINAL AGENT OUTPUTS:\n{json.dumps(final_outputs, indent=2)}\n\n"
                  f"FINAL COLLECTIVE MEMORY:\n{json.dumps(final_memory_state, indent=2)}\n\n"
                  f"Based on all the above information, provide the final answer in the following JSON format:\n"
                  f"{{\n"
                  f'  "answer": "Your final answer option (e.g., A, B, C, or D)",\n'
                  f'  "reasoning": "Your synthesized, final reasoning process that integrates the best points from the agents."\n'
                  f"}}")
        return self.agent.generate(prompt)

class CognitiveOrchestrationFramework:
    """The complete COF Framework"""
    def __init__(self, client: OpenAI, model_id: str, enable_thinking: bool, num_agents: int = 3, num_iterations: int = 1):
        self.num_agents = num_agents
        self.num_iterations = num_iterations
        self.orchestrator = CognitiveOrchestrator(client, model_id, enable_thinking)
        self.agents = [GenericAgent(i, client, model_id, enable_thinking) for i in range(num_agents)]
        self.memory = CollectiveMemoryStore()

    def run(self, original_question_text: str) -> str:
        # Step 1: Task Decomposition
        specialized_prompts = self.orchestrator.decompose_task(original_question_text, self.num_agents)
        
        initial_thoughts = []
        for i, agent in enumerate(self.agents):
            prompt = (f"As an expert with the thinking style '{specialized_prompts[i]}', "
                      f"provide your initial analysis and solution for the following problem:\n\n{original_question_text}")
            thought = agent.generate(prompt)
            initial_thoughts.append(thought)
        
        # Step 2: Iterative Refinement
        self.memory.update(initial_thoughts, time_step=0)
        
        last_step_outputs = initial_thoughts
        for t in range(1, self.num_iterations + 1):
            current_step_outputs = []
            for i, agent in enumerate(self.agents):
                peer_outputs = [o for j, o in enumerate(last_step_outputs) if i != j]
                prompt = (f"You are an expert with the thinking style '{specialized_prompts[i]}'. "
                          f"You have already provided an initial thought. Now, review the collective memory and the outputs from your peers, then provide a refined and improved analysis.\n\n"
                          f"ORIGINAL PROBLEM:\n{original_question_text}\n\n"
                          f"COLLECTIVE MEMORY:\n{json.dumps(self.memory.state, indent=2)}\n\n"
                          f"PEER OUTPUTS:\n{json.dumps(peer_outputs, indent=2)}\n\n"
                          f"YOUR PREVIOUS OUTPUT:\n{last_step_outputs[i]}\n\n"
                          f"Provide your refined output:")
                refined_thought = agent.generate(prompt)
                current_step_outputs.append(refined_thought)
            
            self.memory.update(current_step_outputs, time_step=t)
            last_step_outputs = current_step_outputs

        # Step 3: Final Synthesis
        final_answer = self.orchestrator.synthesize_answer(original_question_text, last_step_outputs, self.memory.state)
        
        return final_answer

# ==================== ORIGINAL CODE MODIFICATION SECTION ====================

def create_baseline_prompt(question_data):
    # ... (Your create_baseline_prompt function remains unchanged)
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

def clean_and_parse_json(model_output_str):
    # ... (Your clean_and_parse_json function remains unchanged)
    fixed_str = model_output_str.replace('\\', '\\\\')
    if '```json' in fixed_str:
        start_index = fixed_str.find('```json') + len('```json')
        end_index = fixed_str.rfind('```')
    else:
        start_index = fixed_str.find('{')
        end_index = fixed_str.rfind('}')

    if start_index != -1 and end_index != -1:
        json_str = fixed_str[start_index:end_index + 1].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"\nJSON parsing failed: {e}")
            print(f"Attempted to parse string: {json_str[:500]}...")
            raise
    else:
        raise json.JSONDecodeError("Could not find a valid JSON object in the model output.", model_output_str, 0)

def process_single_file_with_model(input_file, output_file, model_config, current_key_index=0):
    # ... (Your file reading and progress recovery logic remains unchanged)
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"✅ Successfully read: {os.path.basename(input_file)} ({len(questions)} questions)")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ ERROR: Could not read or parse file {input_file}. Error: {e}")
        return

    model_name = model_config["name"]
    model_id = model_config["model_id"]
    enable_thinking = model_config.get("enable_thinking", False)
    
    print(f"   Results will be saved to: {output_file}")
    results = []
    completed_ids = set()
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            completed_ids = {result.get('original_id') for result in results if result.get('original_id')}
            print(f"🔄 Resuming progress: Successfully loaded {len(completed_ids)} records.")
        except (json.JSONDecodeError, FileNotFoundError):
            results, completed_ids = [], set()

    questions_to_process = [q for q in questions if f"{q.get('year')}-{q.get('number')}" not in completed_ids]
    progress_bar = tqdm(questions_to_process, desc=f"Model: {model_name}")

    for question_data in progress_bar:
        year, number = question_data.get("year"), question_data.get("number")
        if year is None or number is None: continue
        question_id = f"{year}-{number}"

        success = False
        while True: # API Key loop
            if current_key_index >= len(api_keys):
                print("\n🚨 All API keys have been tried and failed.")
                break
            
            api_key = api_keys[current_key_index]
            try:
                progress_bar.set_postfix_str(f"ID {question_id}, Key Idx: {current_key_index}")
                client = OpenAI(base_url='https://api-inference.modelscope.cn/v1/', api_key=api_key)

                # ================= Core Logic Switch =================
                model_output = ""
                inner_reasoning = "" # COF framework does not support streaming thought, this item is empty

                if USE_COF_FRAMEWORK:
                    # --- Use COF framework for optimized processing ---
                    cof_system = CognitiveOrchestrationFramework(
                        client=client, 
                        model_id=model_id, 
                        enable_thinking=enable_thinking,
                        num_agents=3, 
                        num_iterations=1
                    )
                    model_output = cof_system.run(question_data.get("question", ""))
                else:
                    # --- Use the original baseline method ---
                    full_prompt = create_baseline_prompt(question_data)
                    if enable_thinking:
                        response = client.chat.completions.create(
                            model=model_id,
                            messages=[{"role": "user", "content": full_prompt}],
                            stream=True,
                            extra_body={"enable_thinking": True}
                        )
                        for chunk in response:
                            reasoning_chunk = chunk.choices[0].delta.reasoning_content or ""
                            answer_chunk = chunk.choices[0].delta.content or ""
                            if reasoning_chunk: inner_reasoning += reasoning_chunk
                            if answer_chunk: model_output += answer_chunk
                    else:
                        response = client.chat.completions.create(
                            model=model_id,
                            messages=[{"role": "user", "content": full_prompt}],
                        )
                        model_output = response.choices[0].message.content
                # ================================================

                # --- Result processing and saving (logic remains unchanged) ---
                model_answer = "ERROR"
                model_reasoning_from_json = model_output
                try:
                    parsed_response = clean_and_parse_json(model_output)
                    model_answer = parsed_response.get("answer", "PARSE_ERROR")
                    model_reasoning_from_json = parsed_response.get("reasoning", "PARSE_ERROR")
                except json.JSONDecodeError:
                    match = re.search(r'"answer"\s*:\s*"([A-D])"', model_output, re.IGNORECASE)
                    if match:
                        model_answer = match.group(1).upper()

                correct_answer = question_data.get("answer")
                is_correct = False
                if model_answer not in ["ERROR", "PARSE_ERROR"]:
                    is_correct = model_answer.strip().upper() == correct_answer.strip().upper()

                final_result = {
                    "original_id": question_id,
                    "original_question": question_data.get("question"),
                    "model_answer": model_answer,
                    "model_reasoning": model_reasoning_from_json,
                    "correct_answer": correct_answer,
                    "inner_reasoning": inner_reasoning,
                    "is_correct": is_correct
                }
                results.append(final_result)
                success = True
                break
            
            except Exception as e:
                error_str = str(e).lower()
                if any(err_key in error_str for err_key in ['401', '429', 'insufficient_quota']):
                    print(f"\n🟡 Key index {current_key_index} failed. Switching...")
                    current_key_index += 1
                    time.sleep(1)
                else:
                    print(f"\n⚠️ Unknown error on ID {question_id}: {e}")
                    break
        
        if not success:
             results.append({
                "original_id": question_id, "original_question": question_data.get("question"),
                "model_answer": "ERROR", "model_reasoning": "All API keys failed or an unrecoverable error occurred.",
                "correct_answer": question_data.get("answer"), "is_correct": False
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Model {model_name} finished processing file {os.path.basename(input_file)}.")
    return current_key_index


# ==================== MAIN EXECUTION LOGIC ====================
if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"🎉🎉🎉 Starting batch processing task 🎉🎉🎉")
    print(f"⭐ Current mode: {'COF Framework Optimization' if USE_COF_FRAMEWORK else 'Baseline Direct Call'}")
    print(f"Input directory: '{INPUT_DIR}'")
    print(f"Output directory: '{OUTPUT_DIR}'")

    # ⭐ Global API key index, persistent across all files and questions
    global_current_key_index = 0

    for model_config in MODEL_CONFIGURATIONS:
        model_name = model_config["name"]
        enable_thinking = model_config.get("enable_thinking", False)
        print("\n" + "=" * 80)
        print(f"🚀 Using model: {model_name} (Thinking: {enable_thinking})")
        print("=" * 80)

        for filename in FILES_TO_PROCESS:
            input_file_path = os.path.join(INPUT_DIR, filename)
            if not os.path.exists(input_file_path):
                print(f"🟡 WARNING: File not found {input_file_path}, skipping.")
                continue
            
            # ⭐ Corrected and enhanced the filename generation logic
            file_prefix = os.path.splitext(filename)[0].replace('-choicequestions', '') # e.g., "contradictory-load-level-1"
            cof_str = "COF" if USE_COF_FRAMEWORK else "Baseline"
            enable_thinking_str = "true" if enable_thinking else "false"
            output_filename = f"{file_prefix}-{model_name}-{cof_str}-{enable_thinking_str}-choiceanswer.json"
            output_file_path = os.path.join(OUTPUT_DIR, output_filename)

            print(f"\n▶️  Processing file: {filename}")
            # ⭐ Pass and update the global API key index
            global_current_key_index = process_single_file_with_model(input_file_path, output_file_path, model_config, global_current_key_index)

    print("\n\n🎉🎉🎉 All tasks completed! 🎉🎉🎉")