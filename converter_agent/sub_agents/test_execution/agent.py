import requests
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.adk.code_executors import VertexAiCodeExecutor
    
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
    
def run_tests(language: str, filename: str, contents: str):
    # TODO add Access Token
    url = "https://onecompiler-onecompiler-default.p.rapidapi.com/run"
    key = "0b2c052ee6mshdd2d12a7f8b1d92p1fffe0jsn96410d3d8aca"
    data = {
        "language": language,
        "files": [
            {
            "name": filename,
            "content": contents
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "onecompiler-onecompiler-default.p.rapidapi.com"
    }
    print(f"Querying URL: {url}")
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        # Extract and return relevant info
        return {
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "status": result.get("status", "error"),
            "exception": result.get("exception", None),
            "executionTime": result.get("executionTime", None)
        }
    except requests.exceptions.RequestException as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "status": "error",
            "exception": None,
            "executionTime": None
        }


test_execution = LlmAgent(
    name="test_execution",
    model="gemini-2.0-flash",
    description="Test execution agent",
    code_executor=VertexAiCodeExecutor(),
    instruction="""
    You are a helpful assistant that takes in Ruby and Java test files and executes them to verify that both implementations produce the same results for the same inputs. Follow the instructions below in order, without skipping any steps:

    1. Fetch the Ruby and Java test files using the tools `get_ruby_test_file` and `get_java_test_file`.
    - `get_java_test_file` returns an object containing multiple files, where each key is a filename and each value is the file's content.

    2. For each test file:
    - Use the `run_tests` tool to execute the test file.
    - Pass the appropriate language ("ruby" or "java"), the filename, and the full contents of the test file.

    3. Compare the outputs:
    - If both test files produce the same results (e.g., identical "PASS"/"FAIL" sequences), report that the Ruby and Java implementations are behaviorally equivalent.
    - If the outputs differ, report the mismatch and describe the differences clearly.

    4. Also report:
    - Any errors encountered during execution (e.g., compilation errors, runtime exceptions).
    - The error messages returned by the `run_tests` tool.
    - Suggestions for resolving the errors, if possible.

    Your goal is to validate that the Ruby and Java files behave identically under the same test conditions. Be thorough and clear in your comparison and reporting.
    """,
    tools=[get_ruby_test_file, get_java_test_file, run_tests],
)