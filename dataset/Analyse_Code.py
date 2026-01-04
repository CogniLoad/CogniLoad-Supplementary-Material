import pandas as pd
import json
import os
import time
from typing import List
from openai import OpenAI
from tqdm import tqdm

# ================= 配置区域 =================
API_KEY = 'ms-e57c21aa-8d89-4ec0-b272-ed07104ce257' 

DEFAULT_KEYS = [
    API_KEY,
    'ms-7526636f-892a-442a-865f-05b45352bec2',
    'ms-52820e09-83b5-4d94-ba36-46ee0dd96672',
    'ms-6b330de2-dfc0-4c12-b34a-49a13e494573',
    'ms-c0bbb406-e6ee-4d6c-907c-9618ca548d98',
    'ms-d1cc2822-40ea-4345-b07e-0f535d509bcd',
    'ms-e026afa8-bece-47f7-9afd-97c55edd3beb',
    'ms-8a962720-9cb7-45d3-af59-310e333b97a5',
    'ms-cdf60d5a-98e7-4f2f-9874-3616b8eda165',
    'ms-4c5af8e1-b8d6-4abc-90cc-d4fb078702bb',
    'ms-af9acea8-b31d-4b3b-953e-16bc9ed8343c',
    'ms-36986390-6ea1-47f6-b874-46cd171c1c76',
    'ms-4c5af8e1-b8d6-4abc-90cc-d4fb078702bb',
    'ms-c6707241-83da-4ba8-be99-a3b13934abef',
    'ms-ad150d9d-4a18-47cc-92cf-3addcce54430',
    'ms-f39263ca-61b7-4e74-b3aa-5f5331e19cdb',
    'ms-b3fc9c8f-ea36-401f-b257-947865229557',
    'ms-3748a5b5-e450-4b9f-99cb-5d235cb67f62',
    'ms-3384c8e1-a702-40c7-ab6c-92d99ae6964f', 
    'ms-edde61f0-3e94-4a1d-9c40-fab9fe8bf9ef',
    'ms-3736c749-5550-4be6-b613-bcb564de0f48', 
    'ms-3d416a28-9bb3-47e2-8fa8-03bd83d72778',
    'ms-14484e17-2716-41c9-a7db-1b54ff59a170', 
    'ms-22af5c81-29b2-41e0-8404-cf3d2fc494e1',
    'ms-b3fc9c8f-ea36-401f-b257-947865229557', 
    'ms-46da0b4f-2f66-453f-8e36-56860a4b89f9',
    'ms-3096f086-a4d9-48cf-9e4b-ec8a12300c44', 
    'ms-498fb4fc-5a68-4896-abec-cfbd8ea042ad',
    'ms-de5c8978-d96a-4b37-a492-18db9a7505e7', 
    'ms-df7b13df-e8f5-4322-92fd-3095270d5dfb',
    'ms-260d1594-01a0-469e-b1f7-bf46df193973', 
    'ms-558e52ba-9e68-4918-a551-147db7654378',
    'ms-c5b0f6ba-34f0-44dc-a35e-3e97b5642fbb', 
    'ms-0e7d68f7-a8c1-46bc-b83d-a7dc6eba8de4',
    'ms-33e773bf-657f-4f5c-8ca0-74880e632239',
    'ms-e352ffce-aabc-4870-82d7-6e44da90ab88', 
    'ms-ce3376c8-0d90-4a22-b7ab-46c7c7b82a0e',
    'ms-3f7cebda-6ee7-41ed-8e62-1874ba73100a', 
    'ms-3549bc8b-b8ff-4a29-81e0-84a62a904049',
    'ms-8a962720-9cb7-45d3-af59-310e333b97a5', 
    'ms-cdf60d5a-98e7-4f2f-9874-3616b8eda165',
    'ms-6ae5c553-028f-4b70-86a5-95271e1defac', 
    'ms-af9acea8-b31d-4b3b-953e-16bc9ed8343c',
    'ms-f80230e0-aaea-4e11-8ae4-209115679e48', 
    'ms-569fbbea-318b-46e7-85b7-4bc9c7a71d7c', 
    'ms-b6afb51f-b90c-4638-8890-25ce72c0f106',
    'ms-3748a5b5-e450-4b9f-99cb-5d235cb67f62',
    'ms-3096f086-a4d9-48cf-9e4b-ec8a12300c44',
    'ms-3748a5b5-e450-4b9f-99cb-5d235cb67f62',
    'ms-3384c8e1-a702-40c7-ab6c-92d99ae6964f',
    'ms-edde61f0-3e94-4a1d-9c40-fab9fe8bf9ef',
    'ms-3736c749-5550-4be6-b613-bcb564de0f48',
    'ms-3d416a28-9bb3-47e2-8fa8-03bd83d72778',
    'ms-14484e17-2716-41c9-a7db-1b54ff59a170',
    'ms-22af5c81-29b2-41e0-8404-cf3d2fc494e1',
    'ms-b3fc9c8f-ea36-401f-b257-947865229557',
    'ms-46da0b4f-2f66-453f-8e36-56860a4b89f9',
    'ms-e60a8bf2-2620-425f-946a-5f82dca12386',
    'ms-80d06276-84ff-4a66-b987-61cb8f2537fa'
]



API_KEYS = [k.strip() for k in os.getenv("OPENAI_API_KEYS", ",".join(DEFAULT_KEYS)).split(",") if k.strip()]

FILE_PATH = '/Users/bruce7/Documents/AIED2026/Code/Data/GroupA-G 2025年12月25日.xlsx'
OUTPUT_PATH = FILE_PATH.replace('.xlsx', '编码结果.xlsx')

PROCESSED_FLAG = '_processed_flag'
SAVE_EVERY = 10 

TEXT_COLUMN_CANDIDATES = ['讨论文本', '讨论内容', '文本', '对话文本', 'Unnamed: 2']
GROUP_COLUMN_CANDIDATES = ['组别', '小组', '组', 'Unnamed: 0']
NAME_COLUMN_CANDIDATES = ['姓名', '发送者', '学生姓名', 'Unnamed: 1']

clients: List[OpenAI] = [
    OpenAI(base_url='https://api-inference.modelscope.cn/v1', api_key=k)
    for k in API_KEYS if k != 'YOUR_NEW_API_KEY_HERE'
]
current_key_idx = 0

def generate_prompt(text_content, current_speaker, context_list, std_list):
    """
    修改为针对 E-R 列的单向选择 Prompt
    """
    context_str = "\n".join(context_list) if context_list else "（这是对话的开始，无前文）"
    
    prompt = f"""
## 角色设定
你是一位教育技术专家，专注于 CSCL（计算机支持的协作学习）中的知识建构分析。

## 任务背景
请根据上下文，分析学生【{current_speaker}】这句话的知识建构水平。
为了准确判断，我提供了该组之前的对话记录作为背景。

## 特殊标记说明
对话内容中若出现"[图片]"这一文字，代表对应的发言者在该轮对话中上传了相关的材料图片（如资料、截图等），请在分析话语意图时考虑这一信息。

## 对话背景（上下文）
{context_str}

## 待分析文本（目标）
**【{current_speaker}】说**: "{text_content}"

## 编码任务
请结合上下文，判断【{current_speaker}】这句话的意图，请从以下 14 个标准中，选出**唯一一个**最符合该话语意图的选择：
{json.dumps(std_list, ensure_ascii=False, indent=2)}

## 输出要求
仅输出一个标准 JSON：
{{
    "reasoning": "简短的理由（说明为什么属于该类别）",
    "choice": "从标准列表中选择的原话（必须完全一致）"
}}
"""
    return prompt

def call_deepseek_model(prompt):
    global current_key_idx
    if not clients: return None
    total_keys = len(clients)
    for k_offset in range(total_keys):
        key_idx = (current_key_idx + k_offset) % total_keys
        cli = clients[key_idx]
        try:
            response = cli.chat.completions.create(
                model='deepseek-ai/DeepSeek-R1-0528',
                messages=[{'role': 'user', 'content': prompt}],
                stream=True
            )
            full_content = ""
            done_thinking = False
            print(f"\n--- [Key {key_idx}] 正在思考 ---") 
            
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                        print(f"\033[90m{delta.reasoning_content}\033[0m", end='', flush=True)
                    if delta.content:
                        full_content += delta.content
            
            cleaned_content = full_content.replace('```json', '').replace('```', '').strip()
            current_key_idx = key_idx 
            return json.loads(cleaned_content)
        except Exception as e:
            print(f"\nKey {key_idx} 报错: {e}")
            continue
            
    return None

def pick_column(df, candidates, default_idx=None):
    for c in candidates:
        if c in df.columns: return c
    return df.columns[default_idx] if default_idx is not None and len(df.columns) > default_idx else None

def main():
    print("🚀 开始运行...")
    if os.path.exists(OUTPUT_PATH):
        df = pd.read_excel(OUTPUT_PATH)
    else:
        # header=2 确保读取的是 Excel 的第 3 行作为列名
        df = pd.read_excel(FILE_PATH, header=2)

    text_col = pick_column(df, TEXT_COLUMN_CANDIDATES, default_idx=2)
    group_col = pick_column(df, GROUP_COLUMN_CANDIDATES, default_idx=0)
    name_col = pick_column(df, NAME_COLUMN_CANDIDATES, default_idx=1)
    
    # 修改：提取 E列(4) 到 R列(17) 对应的标准列名
    try:
        std_cols = df.columns[4:18].tolist()
        print(f"识别到评判标准 (E-R): {std_cols}")
    except IndexError:
        print("❌ 错误：Excel 列数不足，无法识别 E-H 范围。")
        return

    df[group_col] = df[group_col].ffill()
    df[name_col] = df[name_col].ffill()

    if PROCESSED_FLAG not in df.columns:
        df[PROCESSED_FLAG] = 0

    pbar = tqdm(total=len(df), desc="DeepSeek 编码进度")
    
    for index, row in df.iterrows():
        if row.get(PROCESSED_FLAG, 0) == 1:
            pbar.update(1)
            continue
            
        text = row[text_col]
        if pd.isna(text) or str(text).strip() == "":
            pbar.update(1)
            continue

        # 构建同组上下文
        context_slice = df[(df[group_col] == row[group_col]) & (df.index < index)].tail(5)
        context_list = [f"[{r[name_col]}]: {r[text_col]}" for _, r in context_slice.iterrows() if pd.notna(r[text_col])]

        prompt = generate_prompt(text, row[name_col], context_list, std_cols)
        result = call_deepseek_model(prompt)

        # 清理该行所有标准列，先设为 0
        for col in std_cols:
            df.at[index, col] = 0

        if result:
            choice = result.get('choice')
            # 模糊匹配寻找最接近的列名
            matched_col = None
            if choice in std_cols:
                matched_col = choice
            else:
                for c in std_cols:
                    if choice and (choice in c or c in choice):
                        matched_col = c
                        break
            
            if matched_col:
                df.at[index, matched_col] = 1 # 选中的标 1
                status = "✅"
            else:
                status = "❓(匹配失败)"
        else:
            status = "❌"

        df.at[index, PROCESSED_FLAG] = 1
        pbar.set_postfix({"组": str(row[group_col]), "状态": status})
        pbar.update(1)

        if (index + 1) % SAVE_EVERY == 0:
            df.to_excel(OUTPUT_PATH, index=False)

    pbar.close()
    df.to_excel(OUTPUT_PATH, index=False)
    print(f"🎉 处理完成！文件保存在: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()