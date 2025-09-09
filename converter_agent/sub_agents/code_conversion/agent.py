from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.genai.types import Part
    
def get_artifact_contents(tool_context=ToolContext) -> dict:
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
    
def create_java_file(filename: str, contents: str, tool_context=ToolContext) -> dict:
    try:
        ## Convert contents into bytes
        print(f"Saving file: {filename}")
        artifact = Part.from_bytes(data=contents.encode('utf_8'), mime_type="text/plain")
        tool_context.save_artifact(filename=filename, artifact=artifact)
        print(f"Successfully saved file: {filename}")
        return {"status": "success", "message": f"Successfully saved file: {filename}"}
    except Exception as e:
        return {"status": "error", "message": f"Exception: {e}"}

code_conversion = LlmAgent(
    name="code_conversion",
    model="gemini-2.0-flash",
    description="Code conversion agent",
    instruction="""
    You will follow the following instructions, in order, without skipping any steps:
    1. Use the tool get_artifact_contents to get Ruby code.
    2. Once you have the contents of the ruby file, convert it to Java and pass it into the create_java_file tool as 'contents' 
    along with the name of the file as 'filename' (according to Java file naming convention) 
    which will create an artifact of the name you passed. ** DO NOT SKIP THIS STEP **.
    """,
    tools=[get_artifact_contents, create_java_file],
)