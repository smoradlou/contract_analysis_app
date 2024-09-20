from pathlib import Path
from src.config import load_config
from src.utils import getText
from src.prompts import read_prompt, format_prompt

import streamlit as st

from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMMathChain
from langchain.agents import AgentExecutor, create_tool_calling_agent, Tool
from langchain_core.prompts import ChatPromptTemplate

import pandas as pd

# Helper functions to handle extraction, relevant terms, and compliance checks
def extract_terms(model, document):
    example = read_prompt("resources/example_extraction.md")
    formatted_prompt_text = format_prompt(
        read_prompt("resources/prompts/extraction_prompt.md"),
        contract_text=document,
        example=example,
    )
    return model.invoke(formatted_prompt_text)


def get_relevant_terms(model, task_description, terms_json):
    formatted_prompt_text = format_prompt(
        read_prompt("resources/prompts/relevant_terms_prompt.md"),
        task_description=task_description,
        terms_json=terms_json,
    )
    return model.invoke(formatted_prompt_text)


def check_compliance(model, tools, task_sentence, relevant_terms_json):
    # This is the compliance prompt filled with the task and its relevant terms
    formatted_prompt_text = format_prompt(
        read_prompt("resources/prompts/compliance_prompt.md"),
        task_sentence=task_sentence,
        relevant_terms_json=relevant_terms_json,
    )

    # This is the chat prompt for the agent
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful contract manager.",
            ),
            ("human", "{input}"),
            # Placeholders fill up a **list** of messages
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executer = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        agent_executor_kwargs={
            "handle_parsing_errors": True,
            "return_intermediate_steps": True,
        },
    )

    response = agent_executer.invoke({"input": formatted_prompt_text})
    return response["output"]


st.set_page_config(layout="wide")
st.title("🦜🔗 Contract Analysis App")

# Load configuration
config = load_config()

# Secret keys (make sure to set these in your Cloud Run environment and local environment)
OPENAI_API_KEY = config["OPENAI_API_KEY"]
LLM_MODEL_NAME = config["LLM_MODEL_NAME"]

# Initialize the two data structures
terms_json = None
tasks_df = None

# Initialize LLM for extraction and relevance with JSON binding
json_output_llm = ChatOpenAI(
    model=LLM_MODEL_NAME, temperature=0.0, api_key=OPENAI_API_KEY
)
json_output_llm = json_output_llm.bind(response_format={"type": "json_object"})


# Initialize LLM for compliance without JSON binding
llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=0.0, api_key=OPENAI_API_KEY)


llm_math_chain = LLMMathChain.from_llm(llm=llm)
tools = [
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="Useful for when you need to answer questions that involve math. \
        For instance if you need to calculate a new adjusted budget cap using multipliers.\
            Or if you need to see if a cost of a task or an event is under the budget cap.",
    )
]

# Define layout with two columns
col1, col2 = st.columns(2)

with col1:
    # Upload the contract document
    uploaded_doc = st.file_uploader(
        "Upload your contract here!", type=["docx"], accept_multiple_files=False
    )

    if uploaded_doc is not None:
        contract_text = getText(uploaded_doc)

        # Extract contract terms
        response = extract_terms(json_output_llm, contract_text)
        terms_json = response.content
        st.json(terms_json)

with col2:
    # Upload the tasks CSV, Excel, or text file
    uploaded_table = st.file_uploader(
        'Upload Tasks! The first column must be "Task Description", and the second "Amount"',
        type=["csv", "xlsx"],
        accept_multiple_files=False,
    )

    if uploaded_table is not None:
        # Load the tasks into a DataFrame based on file type
        if Path(uploaded_table.name).suffix == ".xlsx":
            tasks_df = pd.read_excel(uploaded_table, index_col=False)
        else:
            tasks_df = pd.read_csv(uploaded_table, index_col=False)

    results_df = pd.DataFrame(
        columns=[
            "Task Description",
            "Amount",
            "Compliance",
            "Rationale",
            "Relevant Terms",
        ]
    )

    if tasks_df is not None and terms_json is not None:
        st.write("The tool will only analyse the first 100 rows max!")
        for index, row in tasks_df.iterrows():
            if index < 100:  # To limit api costs for now
                task_desc = row["Task Description"]
                task_amount = row["Amount"]
                task_text = f"{task_desc} for {task_amount}"
                relevant_terms_json = get_relevant_terms(
                    json_output_llm, task_desc, terms_json
                ).content
                if relevant_terms_json != "None":
                    response = check_compliance(
                        llm, tools, task_text, relevant_terms_json
                    )
                # Use all terms if the relevance prompt doesn't return any terms
                else:
                    response = check_compliance(llm, tools, task_text, terms_json)
                response = "\n".join(response.split("\n")[1:])

                # Display task description, compliance results, and relevant terms
                with st.expander(f"#### Task: {task_text}"):
                    st.write("#### Compliance Check:")
                    st.write(response.replace("$", "\\$"))
                    st.write("##### Relevant Terms:")
                    st.json(relevant_terms_json)
                # columns=['Task Description','Amount','Compliance','Rationale','Relevant Terms']
                results_df.loc[index] = [
                    task_desc,
                    task_amount,
                    ("\n".join(response.split("\n")[-1:])).replace(
                        "Final answer: ", ""
                    ),
                    "\n".join(response.split("\n")[0:1]),
                    relevant_terms_json,
                ]
            else:
                break

        output_filename = "output/tasks_compliance.xlsx"
        results_df.to_excel(output_filename)
        
        with open(output_filename, "rb") as template_file:
            template_byte = template_file.read()

        st.download_button(label="Click to Download Output File",
                        data=template_byte,
                        file_name=output_filename.split("/")[-1],
                        mime='application/octet-stream')
