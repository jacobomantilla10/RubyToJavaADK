from google.adk.agents import LlmAgent
import base64
from google.adk.tools import ToolContext
from google.genai.types import Part
import requests

def get_code(owner: str, repo:str, path:str, tool_context=ToolContext) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    print(f"Querying URL: {url}")
    response = requests.get(url)
    print(f"response {response.json()["content"]}")
    if response.status_code == 200:
        try: 
            artifact = Part.from_bytes(data=base64.b64decode(response.json()["content"]), mime_type="text/plain")
            tool_context.save_artifact(filename="snippet.rb", artifact=artifact)
        except Exception as e:
            print(e)
            return {"status": "error", "message": f"Exception: {e}"}
    else:
        print("test 3")
        return {"status": "error", "message": f"Failed to fetch file: {response.status_code}"}
    
def save_code(contents: str, tool_context=ToolContext) -> dict:
    try: 
        artifact = Part.from_bytes(data=contents.encode('utf_8'), mime_type="text/plain")
        tool_context.save_artifact(filename="snippet.rb", artifact=artifact)
        print("Artifact Saved")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": f"Exception: {e}"}
    

fetch_code = LlmAgent(
    name="fetch_code",
    model="gemini-2.0-flash",
    description="Code fetching and saving agent",
    instruction="""
    # This agent accepts either:
    - A GitHub repository URL or metadata, or  
    - A raw Ruby code snippet,  
    and creates a structured artifact from it. The agent must follow the steps below exactly and silently.
    ---
    ## Step-by-Step Instructions

    ### Step 1: Input Handling

    **If the user provides a Ruby code snippet:**

    - Accept any phrasing that introduces the snippet (e.g., “Can you convert this Ruby code…”).
    - Extract the Ruby code from the message.
    - Clean the code if it contains characters that don’t conform to `.rb` syntax.
    - Pass the cleaned code as a string to the `save_code` tool to create a file in artifacts.

    **If the user provides a GitHub URL:**
    
    - Extract the following from the URL:
    - `owner`
    - `repo`
    - `path`
    - Example:  
    `https://github.com/jacobomantilla10/TestRepo/blob/main/test2.rb`  
    → owner: `jacobomantilla10`, repo: `TestRepo`, path: `test2.rb`
    - Use the `get_code` tool with these parameters to fetch and save the file as an artifact.

    **If the user provides owner, repo, and path directly:**

    - Use those values with the `get_code` tool to fetch and save the file.
    ---
    ## Behavior Rules
    - Do not output any text unless explicitly requested by the user.
    - Do not confirm actions or describe what you are doing.
    - Do not explain the code or the process unless asked.
    - Only perform the task of saving the Ruby code as an artifact.
    ---
    ## Cleanup Guidelines
    - If the Ruby code contains non-standard characters or formatting issues:
    - Remove or correct them before saving.
    - Ensure the file is valid `.rb` syntax.
    ---
    """,
    tools=[get_code, save_code],
)