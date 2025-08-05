import json
import os
import base64


def add_chaotic_irrelevant_load(question_text: str, level: int) -> str:
    """
    Adds four highly differentiated, chaotic HTML structural loads to the question text.
    The complexity of each level roughly doubles from the previous one.
    """

    # HTML-encode special characters in the original text to increase parsing difficulty
    encoded_question_text = question_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # --- Level 1 (High Load Baseline) ---
    # Simulates a complex page with various typical web elements, serving as a base for subsequent levels.
    level_1_html = (
        f'<!DOCTYPE html>\n'
        f'<html lang="zh-CN">\n'
        f'<head>\n'
        f'  <meta charset="UTF-8">\n'
        f'  <title>在线测验平台</title>\n'
        f'  <style>\n'
        f'    body {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; background-color: #f4f4f9; }}\n'
        f'    .container {{ max-width: 960px; margin: 20px auto; padding: 15px; background: #fff; border: 1px solid #ddd; }}\n'
        f'    .question-box {{ border: 2px dashed #ccc; padding: 20px; margin-top: 15px; }}\n'
        f'    .hidden-ad {{ display: none !important; }}\n'
        f'  </style>\n'
        f'</head>\n'
        f'<body>\n'
        f'  <div id="page-wrapper">\n'
        f'    <header role="banner">\n'
        f'      <div class="hidden-ad">ADVERTISEMENT</div>\n'
        f'      <h1>欢迎来到在线测验</h1>\n'
        f'    </header>\n'
        f'    <main id="main-content" role="main">\n'
        f'      \n'
        f'      <div class="question-box" data-question-type="multiple-choice">\n'
        f'        <p>{encoded_question_text}</p>\n'
        f'      </div>\n'
        f'    </main>\n'
        f'    <script>\n'
        f'      // A simple script to track page load. Should be ignored.\n'
        f'      const startTime = new Date().getTime();\n'
        f'      window.onload = function() {{ console.log("Page loaded in: " + (new Date().getTime() - startTime) + "ms"); }};\n'
        f'    </script>\n'
        f'  </div>\n'
        f'</body>\n'
        f'</html>'
    )
    if level == 1:
        return level_1_html

    # --- Level 2 (Complexity Doubled) ---
    # Embeds the Level 1 content into a more chaotic structure with table layouts and numerous attributes.
    noise_data_1 = base64.b64encode(os.urandom(256)).decode('utf-8')
    level_2_html = (
        f'<div class="app-root" data-version="2.1.0">\n'
        f'  <nav class="top-nav">\n'
        f'    <span>首页</span> | <span>关于我们</span> | <span>联系方式</span>\n'
        f'  </nav>\n'
        f'  <table id="layout-table" border="1" style="width:100%; border-collapse: collapse;">\n'
        f'    <tbody>\n'
        f'      <tr>\n'
        f'        <td style="padding: 20px; vertical-align: top;" class="content-cell">\n'
        f'          <h3>请仔细阅读以下内容并作答</h3>\n'
        f'          {level_1_html}\n'
        f'        </td>\n'
        f'        <td style="width: 200px;" class="sidebar-cell">\n'
        f'          <h4>相关资料</h4>\n'
        f'          <p>这是一个侧边栏，包含无关信息。</p>\n'
        f'          <img alt="placeholder" src="data:image/gif;base64,{noise_data_1}">\n'
        f'        </td>\n'
        f'      </tr>\n'
        f'    </tbody>\n'
        f'  </table>\n'
        f'</div>'
    )
    if level == 2:
        return level_2_html

    # --- Level 3 (Complexity Doubled Again) ---
    # Treats the Level 2 content as a "main post" and adds a "comment section" and more script noise.
    lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor."
    level_3_html = (
        f'<div id="forum-thread-page">\n'
        f'  <div class="main-post" data-post-id="54321">\n'
        f'    {level_2_html}\n'
        f'  </div>\n'
        f'  <div class="comment-section">\n'
        f'    <h3>评论区</h3>\n'
        f'    <div class="comment" data-user-id="101"><p>这个题目有点难度！</p></div>\n'
        f'    <div class="comment" data-user-id="102"><p>{lorem_ipsum}</p></div>\n'
        f'  </div>\n'
        f'  <script>\n'
        f'    (function() {{\n'
        f'      var config = {{ "user_id": 123, "tracking_enabled": true }};\n'
        f'      function complex_function(a, b) {{ return a * b; }}\n'
        f'      console.log("Complex UI script loaded.");\n'
        f'    }})();\n'
        f'  </script>\n'
        f'</div>'
    )
    if level == 3:
        return level_3_html

    # --- Level 4 (Final Complexity Doubling) ---
    # Places the Level 3 content into a simulated "print preview" frame, surrounded by numerous comments and repetitive structural noise.
    final_noise_block = "\n".join([f'' for i in range(20)])
    level_4_html = (
        f'<div class="print-preview-wrapper">\n'
        f'  {final_noise_block}\n'
        f'  <div class="page-a4">\n'
        f'    <div class="header-print">文档打印预览 - 请勿修改</div>\n'
        f'    {level_3_html}\n'
        f'  </div>\n'
        f'  {final_noise_block}\n'
        f'  <div class="page-a4-duplicate-for-layout-testing" style="display:none;">\n'
        f'    \n'
        f'    {level_3_html.replace(encoded_question_text, "这是一个用于增加复杂度的重复结构中的占位符文本。")}\n'
        f'  </div>\n'
        f'  {final_noise_block}\n'
        f'</div>'
    )
    if level == 4:
        return level_4_html

    return question_text

def generate_irrelevant_load_datasets(input_dir: str, base_filename: str):
    """
    Reads the original questions file, generates datasets with 4 levels of irrelevant load,
    and saves them in the same directory.
    """
    input_path = os.path.join(input_dir, base_filename)

    # Ensure the input directory exists
    if not os.path.exists(input_dir):
        print(f"❌ ERROR: Input directory '{input_dir}' does not exist. Please create it and place the required files inside.")
        return

    # Ensure the input file exists
    if not os.path.exists(input_path):
        print(f"❌ ERROR: Input file '{base_filename}' not found in directory '{input_dir}'.")
        return

    # Read the original JSON file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            original_questions = json.load(f)
        print(f"✅ Successfully read original file '{input_path}' with {len(original_questions)} questions.")
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Failed to parse file '{input_path}'. Details: {e}")
        return

    # Define the 4 levels of load configurations to generate
    # Filenames will be generated automatically based on this configuration
    load_levels_to_generate = [1, 2, 3, 4]

    # Loop to generate and save each dataset
    for level in load_levels_to_generate:
        # Generate the new filename according to your naming convention
        output_filename = f"irrelevant-load-level-{level}-{base_filename}"
        output_path = os.path.join(input_dir, output_filename)

        loaded_questions = []
        for question_data in original_questions:
            new_question_data = question_data.copy()
            original_text = question_data.get("question", "")

            # Apply the corresponding level of irrelevant load
            loaded_text = add_chaotic_irrelevant_load(original_text, level)

            new_question_data["question"] = loaded_text
            loaded_questions.append(new_question_data)

        # Write to the JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(loaded_questions, f, ensure_ascii=False, indent=4)

        print(f"✅ Generated dataset: '{output_path}'")


if __name__ == '__main__':
    # Specify that the input and output are in the same directory
    DATA_DIRECTORY = 'AAAIDataset'
    BASE_FILENAME = 'choicequestions.json'

    generate_irrelevant_load_datasets(DATA_DIRECTORY, BASE_FILENAME)

    print(f"\n🎉 All irrelevant load datasets have been generated and saved to the '{DATA_DIRECTORY}' directory.")