import openai
from dotenv import load_dotenv
from typing_extensions import override
from openai import AssistantEventHandler

load_dotenv()
client = openai.OpenAI()

# model = "gpt-4-1106-preview"  # "gpt-3.5-turbo-16k"
#
# # Step 1. Upload a file to OpenaI embeddings ===
# filepath = r"C:\Users\aeous\OneDrive - C2 Group\Old\Mavic+2+Pro+Zoom+User+Manual+V1.4.pdf"
# file_object = client.files.create(file=open(filepath, "rb"), purpose="assistants")
#
# # Step 2 - Create an assistant and get the assistant ID
# assistant = client.beta.assistants.create(
#     name="Mavic Pro Assistant",
#     instructions="""You are a helpful study assistant who knows a lot about understanding manuals.
#     Your role is to summarize papers, clarify terminology within context, and extract key figures and data.
#     Cross-reference information for additional insights and answer related questions comprehensively.
#     Analyze the papers, noting strengths and limitations.
#     Respond to queries effectively, incorporating feedback to enhance your accuracy.
#     Handle data securely and update your knowledge base with the latest research.
#     Adhere to ethical standards, respect intellectual property, and provide users with guidance on any limitations.
#     Maintain a feedback loop for continuous improvement and user support.
#     Your ultimate goal is to facilitate a deeper understanding of complex scientific material, making it more accessible
#     and comprehensible.""",
#     tools=[{"type": "retrieval"}],
#     model=model,
#     file_ids=[file_object.id],
# )
#
# assistant_id = assistant.id
# print(assistant_id)
#
# # Step 3. Create a Thread and get the thread ID
#
# thread = client.beta.threads.create()
# thread_id = thread.id
# print(thread_id)

# == Hardcoded ids to be used once the first code run is done and the assistant was created
thread_id = "thread_xKQlOAXQngf8X96HX2ANvrvD"
assistant_id = "asst_uAEAtjI2kV15ZL2qyfZZa5Jc"

# == Step 4. Start the thread with a message
message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content="What is this manual about?"
)


# Step 5. Run the Assistant
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


# Then, we use the `create_and_stream` SDK helper
# with the `EventHandler` class to create the Run
# and stream the response.

with client.beta.threads.runs.create_and_stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user as Jane Doe. The user has a premium account.",
        event_handler=EventHandler(),
) as stream:
    stream.until_done()

# # === Check the Run Steps - LOGS ===
# run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
# print(f"Run Steps --> {run_steps.data[0]}")