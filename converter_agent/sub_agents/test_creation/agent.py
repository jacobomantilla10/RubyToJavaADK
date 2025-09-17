from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.genai.types import Part
    
def get_java_file(tool_context=ToolContext) -> dict:
    try:
        # Load the artifact file path
        all_artifacts = tool_context.list_artifacts() 
        print(f"All artifacts: {all_artifacts}")
        java_artifacts = {}
        for index, item in enumerate(all_artifacts):
            if ".java" in item:
                java_artifacts[item] = tool_context.load_artifact(item).inline_data.data.decode("utf-8")
        if len(java_artifacts) == 0:
            return {"status": "error", "message": "Could not find Java file in artifact list"}
        # Extract bytes and decode to string
        return {"status": "success", "files": java_artifacts}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def get_ruby_file(tool_context: ToolContext) -> dict:
    try:
        # Load the artifact file path
        part = tool_context.load_artifact("snippet.rb")
        print(f"part: {part}")
        # Extract bytes and decode to string
        byte_data = part.inline_data.data
        content_str = byte_data.decode("utf-8")
        return {"status": "success", "contents": content_str}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def create_ruby_test_file(contents: str, tool_context: ToolContext) -> dict:
    try:
        ## Convert contents into bytes
        artifact = Part.from_bytes(data=contents.encode('utf_8'), mime_type="text/plain")
        tool_context.save_artifact(filename="snippet_test.ruby", artifact=artifact)
    except Exception as e:
        return {"status": "error", "message": f"Exception: {e}"}
    
def create_java_test_file(filename: str, contents: str, tool_context: ToolContext) -> dict:
    try:
        ## Convert contents into bytes
        artifact = Part.from_bytes(data=contents.encode('utf_8'), mime_type="text/plain")
        tool_context.save_artifact(filename=f"{filename}", artifact=artifact)
    except Exception as e:
        return {"status": "error", "message": f"Exception: {e}"}

test_creation = LlmAgent(
    name="test_creation",
    model="gemini-2.0-flash",
    description="Test file generation agent",
    instruction="""           
    # Agent Role: Unit Test Generator for Ruby and Java.

    Your only job is to generate unit tests for both Ruby and Java source files and save them as artifacts. Do not output anything to the console. Do not skip any language. Do not log or describe your actions.
    ---
    ## Instructions

    ### 1. Fetch Source Files

    - Use the tools `get_ruby_file` and `get_java_file` to fetch the Ruby and Java files respectively.
    - Do not output or log any information during this step.

    ### 2. Generate Unit Tests

    - Generate unit tests using `Minitest` or `RSpec` for Ruby and `JUnit` for Java.
    - Make sure the tests cover logic and expected behavior, are deterministic and executable, cover edge cases and typical inputs and incluse assertions for outputs and exceptions.

    ### 3. Save Unit Tests

    - Use `create_ruby_test_file` to save the Ruby test file. Pass the full test code as `contents`.
    - Use `create_java_test_file` to save the Java test file. Pass the full test code as `contents` and the test file name as `filename`.
    ---
    ## Behavior Rules
    - Do not print anything unless explicitly asked.
    - Do not describe what you are doing.
    - Only fetch code, generate tests, and save them as artifacts.
    ---
    """,
    tools=[get_ruby_file, get_java_file, create_ruby_test_file, create_java_test_file],
)