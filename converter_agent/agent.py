from google.adk.agents import SequentialAgent
from google.adk.agents import LlmAgent
from .sub_agents.code_conversion.agent import code_conversion
from .sub_agents.fetch_code.agent import fetch_code
from .sub_agents.test_creation.agent import test_creation
from .sub_agents.test_execution.agent import test_execution
from google.adk.tools.agent_tool import AgentTool
from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.tools import ToolContext

# test_execution_tool = AgentTool(test_execution)
def get_java_test_file(tool_context=ToolContext) -> dict:
    try:
        # Load the artifact file path
        all_artifacts = tool_context.list_artifacts() 
        print(f"All artifacts: {all_artifacts}")
        java_test_artifacts = {}
        for index, item in enumerate(all_artifacts):
            if "Test.java" in item:
                java_test_artifacts[item] = tool_context.load_artifact(item).inline_data.data.decode("utf-8")
        if len(java_test_artifacts) == 0:
            return {"status": "error", "message": "Could not find Java file in artifact list"}
        return {"status": "success", "files": java_test_artifacts}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def get_ruby_test_file(tool_context=ToolContext) -> dict:
    try:
        # Load the artifact file path
        all_artifacts = tool_context.list_artifacts() 
        artifact_name = ""
        for index, item in enumerate(all_artifacts):
            if "_test.rb" in item or "_test.ruby" in item:
                artifact_name = item
        if artifact_name == "":
            return {"status": "error", "message": "Could not find Ruby file in artifact list"}
        part = tool_context.load_artifact(artifact_name)
        print(f"part: {part}")
        # Extract bytes and decode to string
        byte_data = part.inline_data.data
        content_str = byte_data.decode("utf-8")
        return {"status": "success", "contents": content_str, "filename": artifact_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}

sequential_agent = SequentialAgent(
    name="sequential_agent",
    description="Executes a sequence of code fetching, conversion, test generation and test execution",
    sub_agents=[fetch_code, code_conversion, test_creation],
)

root_agent = LlmAgent(
    name="converter_agent",
    description="Executes a sequence of code fetching, conversion, test generation and test execution",
    model="gemini-2.0-flash",
    instruction="""
    1. Run sequential agent (sub agent). After the sequential agent has finished continue with the steps. If you ever regain control from the sequential agent and don't know 
    what to do, run the following steps anyways,
    2. Fetch the Ruby and Java test files using the get_ruby_test_file and get_java_test_file tools accordingly. get_java_test_file will return an object containing several
    files and their contents as key-value pairs.The key is the filename and the value is the content of the file.
    3. Use the code executor to execute the Ruby and Java test files to test the Ruby and Java files present in artifacts storage.
    4. Report back the results, and whether or not both test files yielded the same results for the Java and Ruby files. Our aim was to create two files that do
    the same thing in different languages so it is crucial to test them both the same way. Also report if there were any errors running the files and what the error message
    says. Give any input you have on how to resolve the error if any are present.
    """,
    sub_agents=[sequential_agent],
    code_executor=VertexAiCodeExecutor(),
    # tools=[test_execution_tool],
    tools=[get_ruby_test_file, get_java_test_file],
)