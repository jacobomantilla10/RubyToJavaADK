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
    
def save_code(contents: Part, tool_context=ToolContext) -> dict:
    try: 
        tool_context.save_artifact(filename="snippet.rb", artifact=contents)
        print("Artifact Saved")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": f"Exception: {e}"}
    

fetch_code = LlmAgent(
    name="fetch_code",
    model="gemini-2.0-flash",
    description="Code fetching and saving agent",
    instruction="""
    You are a helpful assistant that takes a Github repository (or github repository information) or code snippets and saves it to an artifact.
    You will follow the following instructions, in order, without skipping any steps.
    1. If the user passes in a code snippet and not a repository, then pass the contents to the save_code Tool to create a file for it in artifacts.
        - If the user gives you a github user name or owner, a repo name, and a path to the file, use the tool get_code 
        with the owner, repo name, and path as parameters as well tool context. This will save the file as an artifact.
            - The user might give this file as a URL, in that case, extract the Owner, repo, and path.
            - e.g.: https://github.com/jacobomantilla10/TestRepo/blob/main/test2.rb -> owner: jacobomantilla10, repo: TestRepo, path: test.rb
            - If the user gives you owner, repo, and path outright, use those parameters for the tool call.
    """,
    tools=[get_code],
)