import streamlit as st
from firebase.firebase_utils import write_task_item
import json
import random

FIREBASE_DB = '3-19-human-feedback'

data_file = './data/prepare_data/NK_HF_responses_3_18.json'
with open(data_file, "r") as f:
    ALL_DATA = json.load(f)

st.title('Myelin Human Feedback')




# checklist = "Sample Checklist"
# sample_background = "Sample background + kickout checklist"
# sample_conversation = "Sample conversation"

# responses = [
#     "Response 1",
#     "Response 2",
#     "Response 3",
#     "Response 4"
# ]


with st.form("myelin-hf-form", clear_on_submit=True):

    user_name = st.text_input("Enter your name", key="user_name")



    def sample_item():
        return random.choice(ALL_DATA)

    sample = sample_item()
    prompt_id = sample['prompt_id']

    checklist = sample['checklist']
    kickout_checklist = sample['kickout_checklist']

    system_prompt = sample['system_prompt']
    conversation = sample['conversation_raw']
    responses = sample['responses']
    # shuffle the responses
    responses = dict(random.sample(responses.items(), len(responses)))
    for model_key, response in responses.items():
        responses[model_key] = response.replace("[INST]", "")

    if len(kickout_checklist) > 0:
        checklist = kickout_checklist

    def capture_score():
        response_rankings = []
        text_responses = []
        model_keys = []

        for model_key, response in responses.items():
            model_keys.append(model_key)
            text_responses.append(response)
            response_rankings.append(st.session_state[model_key])

        rewrte = str(st.session_state["rewrite"])


        feedback_object = {
            "user_name": user_name,
            "prompt_id": prompt_id,
            "response_rankings": response_rankings,
            "responses": text_responses,
            "model_keys": model_keys,
        }

        print(feedback_object)

        write_task_item(feedback_object, FIREBASE_DB)

    with st.expander("Review Checklist"):
        st.write(checklist)

    with st.expander("Review Call Background"):
        st.write(system_prompt)


    st.write("**Conversation Transcript:**")
    with st.container(border=True):
        for turn in conversation:
            with st.container(border=True):
                st.write("**" + turn['speaker'] + ":** " + turn['text'])

    st.write("**Read the following responses and rank them 1-4 (1 is the best, 4 is the worst). Please ensure that you give each response a different ranking:**")

    for model_key, response in responses.items():
        with st.container(border=True):
            st.write(response)
            #st.radio("Rank this response", options=[1, 2, 3, 4], key=response)
            st.selectbox("Rank this response:", options=[1, 2, 3, 4], key=model_key)

    # no real way to validate this input...
            
    rewrite = st.text_area("If you feel that none of responses are good, and/or you have a better response in mind, please write it here:", key="rewrite")

    submit_button = st.form_submit_button(label='Submit', on_click=capture_score)