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
    You are a helpful assistant that takes in Ruby and Java files and creates test files for them. You will follow the following instructions, in order, without skipping any steps.
    1. Use the tools get_ruby_file and get_java_file to fetch the ruby and java files accordingly. get_java_file will return an object containing several files and their contents as key-value pairs.
    The key is the filename and the value is the content of the file.
    2. Once you have the contents of both the Ruby and Java files, you will write test files for each of them.
    3. Once you have the test files, you will use the corresponding Tools to save the files as artifacts.
        - The test ruby file will be saved using the create_ruby_test_file tool by passing in the test file contents as a string.
        - The test java file will be saved using the create_java_test_file tool by passing in the test file contents as a string and the name of the file.
    """,
    tools=[get_ruby_file, get_java_file, create_ruby_test_file, create_java_test_file],
)