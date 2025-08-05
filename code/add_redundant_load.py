import json
import os

def repeat_question_parts(input_file, output_file, stem_repeats, options_repeats):
    """
    Reads a JSON file, modifies the 'question' field by repeating its stem and options,
    and writes the result to a new JSON file.

    Args:
        input_file (str): Path to the input JSON file (e.g., 'database/choicequestions.json').
        output_file (str): Path to the output JSON file.
        stem_repeats (int): Number of times to repeat the question stem.
        options_repeats (int): Number of times to repeat the options part.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_file}'.")
        return

    modified_data = []
    for item in data:
        if "question" in item:
            question_parts = item["question"].split('\n', 1)
            stem = question_parts[0]
            options = question_parts[1] if len(question_parts) > 1 else ""

            repeated_stem = (stem + "\n") * stem_repeats if stem_repeats > 0 else ""
            repeated_options = options * options_repeats if options_repeats > 0 else ""

            # Remove trailing newline if stem_repeats > 0 and options_repeats == 0
            if stem_repeats > 0 and options_repeats == 0 and repeated_stem.endswith("\n"):
                repeated_stem = repeated_stem[:-1]

            new_question = repeated_stem + repeated_options

            new_item = {
                "year": item.get("year"),
                "number": item.get("number"),
                "question": new_question,
                "answer": item.get("answer")
            }
            modified_data.append(new_item)
        else:
            modified_data.append(item) # Keep items without 'question' field as is

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(modified_data, f, ensure_ascii=False, indent=4)

    print(f"Successfully processed '{input_file}' and saved to '{output_file}'.")

if __name__ == "__main__":
    input_json_file = "./database/choicequestions.json"
    output_json_file = "./database/repeat-75-choicequestions.json"

    try:
        stem_reps = int(input("Enter the number of times to repeat the question stem (e.g., 1 for no repetition): "))
        options_reps = int(input("Enter the number of times to repeat the options (e.g., 1 for no repetition): "))
    except ValueError:
        print("Invalid input. Please enter an integer for repetitions.")
    else:
        repeat_question_parts(input_json_file, output_json_file, stem_reps, options_reps)
