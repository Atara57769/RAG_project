import json
from llama_index.core.selectors import PydanticSingleSelector
from llama_index.core.tools import  ToolMetadata
from config.rag_config import llm

STRUCTURED_DATA = json.loads(
    open("data/structured_data.json", encoding="utf-8").read()
)
def structured_data_query_engine(query_str: str):
    data = STRUCTURED_DATA
    prompt = f"""
    You are an assistant that answers questions using structured project data.

    The data contains:
    - decisions
    - rules
    - warnings
    - dependencies

    Structured data:
    {json.dumps(data, indent=2, ensure_ascii=False)}

    User question:
    {query_str}

    Instructions:
    - Only use the structured data
    - If not found → say "NOT_FOUND"
    - Be concise
    """
    response = llm.complete(prompt)
    return str(response)

selector = PydanticSingleSelector.from_defaults()
choices = [
    ToolMetadata(
        name="structured",
        description="Questions about decisions, rules, warnings, dependencies"
    ),
    ToolMetadata(
        name="semantic",
        description="Questions about code, architecture, or general documentation"
    ),
]