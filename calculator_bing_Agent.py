import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool, FunctionTool, ToolSet
from user_functions import user_functions

# Initialize the Azure AI Project Client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# Retrieve Bing connection ID
bing_connection = project_client.connections.get(
    connection_name=os.environ["BING_CONNECTION_NAME"]
)
conn_id = bing_connection.id

# Initialize Bing grounding tool
bing = BingGroundingTool(connection_id=conn_id)

# Initialize function tool with user-defined functions
functions = FunctionTool(functions=user_functions)

# Combine tools into a toolset
toolset = ToolSet()
toolset.add(bing)
toolset.add(functions)

# Create the agent with the combined toolset
with project_client:
    agent = project_client.agents.create_agent(
        model="gpt-4o",
        name="my-assistant",
        instructions="You are a helpful assistant capable of performing web searches and mathematical calculations. Decide which tool to use based on the user's query.",
        toolset=toolset,
        headers={"x-ms-enable-preview": "true"}
    )
    print(f"Created agent, ID: {agent.id}")

    # Create a communication thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # User's message
    user_input = "what is the capital of australia?"
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )
    print(f"Created message, ID: {message.id}")

    # Process the agent run
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Retrieve and display messages in chronological order
    messages_response = project_client.agents.list_messages(thread_id=thread.id)
    messages_data = messages_response["data"]
    sorted_messages = sorted(messages_data, key=lambda x: x["created_at"])

    print("\n--- Thread Messages (sorted) ---")
    for msg in sorted_messages:
        role = msg["role"].upper()
        content_blocks = msg.get("content", [])
        text_value = ""
        if content_blocks and content_blocks[0]["type"] == "text":
            text_value = content_blocks[0]["text"]["value"]
        print(f"{role}: {text_value}")

    # Delete the agent after completion
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
