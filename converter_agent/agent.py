from google.adk.agents import SequentialAgent
from google.adk.agents import LlmAgent
from .sub_agents.code_conversion.agent import code_conversion
from .sub_agents.fetch_code.agent import fetch_code
from .sub_agents.test_creation.agent import test_creation
from .sub_agents.test_execution.agent import test_execution
from .sub_agents.code_review.agent import code_review

root_agent = SequentialAgent(
    name="converter_agent",
    description="Executes a sequence of code fetching, conversion, review, and unit test creation",
    sub_agents=[fetch_code, code_conversion, code_review, test_creation],
)