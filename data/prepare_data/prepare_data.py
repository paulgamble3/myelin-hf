import pandas as pd
import json 

fn = './data/prepare_data/eval_calls_mar_2024_5_to_7_with_responses_6k.csv'
#'data/prepare_data/NK_HF_responses_3_18.csv'
df = pd.read_csv(fn)

def clean_instructions(raw_text):
    remove_tags = ["[INST]", "[/INST]", "<<SYS>>", "</SYS>>", "[TASK_1]"]

    for tag in remove_tags:
        raw_text = raw_text.replace(tag, "")
    return raw_text

def split_conversation_into_turns(conversation_raw):
    p_split = conversation_raw.split("Patient:")
    p_split = ["Patient:" + t for t in p_split]
    p_split = [t.strip() for t in p_split]
    np_split = [t.split("Nurse:") for t in p_split]

    all_turns = []

    for z in np_split:
        for t in z:
            turn = t.strip()
            if len(turn) == 0:
                continue
            if "Patient:" in turn:
                p_turn = turn.replace("Patient:", "").strip()
                if len(p_turn) > 0:
                    all_turns.append({"speaker": "Patient", "text": p_turn})
            else:
                n_turn = turn.replace("Nurse:", "").strip()
                if len(n_turn) > 0:
                    all_turns.append({"speaker": "Nurse", "text": n_turn})

    return all_turns

COLLECT_ROWS = []

for i, row in df.iterrows():
    # if i > 5:
    #     break
    
    prompt_id = row['prompt_id']
    checklist = row['checklist']
    kickout_checklist = row['kickout_checklist']
    if type(kickout_checklist) == float:
        kickout_checklist = ""

    responses = {
        "gpt4_0": row['gpt4_0'],
        "G55_0.3": row['G55_0.3'],
        "G54_0.6": row['G54_0.6'],
        "G54_1.0": row['G54_1.0']
    }

    instruction = row['instruction']
    if type(instruction) == float:
        continue
    sys_tag_split = instruction.split("<</SYS>>")

    if len(sys_tag_split) != 2:
        print("ERROR: ", len(sys_tag_split))
        continue

    system_prompt = sys_tag_split[0]
    conversation_raw = sys_tag_split[1]
    system_prompt = clean_instructions(system_prompt)
    conversation_raw = clean_instructions(conversation_raw)

    c_turns = split_conversation_into_turns(conversation_raw)

    row = {
        "prompt_id": prompt_id,
        "checklist": checklist,
        "kickout_checklist": kickout_checklist,
        "system_prompt": system_prompt,
        "conversation_raw": c_turns,
        "responses": responses,
    }
    COLLECT_ROWS.append(row)

with open("./data/prepare_data/eval_calls_mar_2024_5_to_7_with_responses_6k.json", "w") as f:
    json.dump(COLLECT_ROWS, f, indent=4)

    

