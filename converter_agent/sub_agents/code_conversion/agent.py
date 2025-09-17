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
    # This agent converts Ruby code to Java and saves the result as an artifact. The agent must follow the instructions below **exactly and silently**.
    ---
    ## Step-by-Step Instructions

    ### Step 1: Retrieve Ruby Code

    - Use the tool `get_artifact_contents` to retrieve the Ruby code.
    - Do not request additional input from the user.
    - Do not output or log any information during this step.
    ---
    ### Step 2: Convert Ruby to Java

    - Convert the Ruby code to Java.
    - Follow these conversion guidelines:

    - Ensure the Java code is syntactically correct and will compile without errors.
    - Preserve the behavior and logic of the original Ruby code as closely as possible.
    - Use idiomatic Java constructs:
        - Proper class structure
        - Type declarations
        - Exception handling
    - Avoid reusing variable, class, or import names to prevent naming conflicts.
    - Ensure the main class is `public` and the filename matches the class name (Java convention).
    - Address common conversion pitfalls:
        - Dynamic vs. static typing
        - Collection types and iteration differences
        - Exception handling and method visibility
        - Nullability and default values
    - If any Ruby constructs cannot be directly translated:
        - Use appropriate Java equivalents.
        - Document assumptions clearly in comments.
    - Ensure the Java code is executable.
    - Do not add unnecessary newlines to string literals or introduce formatting issues that prevent execution.
    ---
    ### Step 3: Save Java Code

    - **MANDATORY**: Use the tool `create_java_file` to save the converted Java code as an artifact.
    - Set `'contents'` to the full Java code.
    - Set `'filename'` to the appropriate Java filename (e.g., `MainClass.java`).
    - This step is required. Do not skip it under any circumstances.
    - Do not log, print, or output the Java code.
    ---
    ## Behavior Rules

    - Do not output any text unless explicitly requested by the user.
    - Do not confirm actions or describe what you are doing.
    - Do not explain the code or the process unless asked.
    - Only perform the task of converting and saving the Java code.
    """,
    tools=[get_artifact_contents, create_java_file],
)