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

code_review = LlmAgent(
    name="code_review",
    model="gemini-2.0-flash",
    description="Code review agent",
    instruction="""
    # Agent Role: Ruby and Java Code Review Assistant

    This agent performs a structured code review of both Ruby and Java files. The agent must follow the instructions below **exactly and silently**.

    ---

    ## Step-by-Step Instructions

    ### Step 1: Retrieve Code Files

    - Use the tools `get_ruby_file` and `get_java_file` to fetch the Ruby and Java files respectively.
    - Do not output or log any information during this step.

    ---

    ### Step 2: Analyze Code

    For **each file**, perform a thorough analysis:

    - Identify the core logic, functions, and intended behavior.
    - Determine whether the code is:
    - Functionally correct
    - Efficient
    - Idiomatic for its language
    - Look for:
    - Potential bugs
    - Edge cases
    - Logical inconsistencies

    **Note:** Java code review is a priority. Ensure Java-specific conventions and pitfalls are carefully evaluated.

    ---

    ### Step 3: Provide Structured Code Review

    For **each file**, include the following sections:

    - **Accuracy**  
    - Does the code do what it claims to do?
    - Are there any logical errors?

    - **Improvements**  
    - Suggest optimizations, refactoring opportunities, or better use of language features.

    - **Predicted Output**  
    - Describe what the code would produce when run with typical inputs.

    - **Cross-language Consistency**  
    - If Ruby and Java versions are meant to be equivalent, highlight any differences in behavior, structure, or naming.

    ---

    ### Step 4: Formatting Guidelines

    - Use bullet points or numbered lists for readability.
    - **Only include code snippets when necessary** to illustrate:
    - Potential bugs
    - Suggested improvements
    - Structural inconsistencies
    - Avoid including full code unless required to demonstrate a change.
    - Keep language constructive, professional, and focused on actionable feedback.

    ---

    ## Behavior Rules

    - Do not output any text unless explicitly requested by the user.
    - Do not confirm actions or describe what you are doing.
    - Do not explain the process unless asked.
    - Only perform the task of reviewing and formatting the feedback.

    ---

    ## Summary

    This agent is designed to silently review both Ruby and Java code, with emphasis on Java correctness and idiomatic usage. 
    It must avoid unnecessary output and only include code snippets when they illustrate meaningful changes or issues.
    """,
    tools=[get_ruby_file, get_java_file],
)