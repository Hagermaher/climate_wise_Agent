"""Builds the RAG index and the agent."""
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.tools import QueryEngineTool, FunctionTool
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.groq import Groq
from llama_index.embeddings.fastembed import FastEmbedEmbedding

from config import KNOWLEDGE_DIR, LLM_MODEL, EMBED_MODEL, SYSTEM_PROMPT
from tools import (
    get_yearly_stats,
    get_temperature_trend,
    get_hottest_days,
    calculate_carbon_footprint,
)


def build_index():
    """Read the text files in /knowledge and build a vector index (RAG)."""
    Settings.embed_model = FastEmbedEmbedding(model_name=EMBED_MODEL)
    docs = SimpleDirectoryReader(str(KNOWLEDGE_DIR)).load_data()
    return VectorStoreIndex.from_documents(docs)


def build_agent(index, api_key: str) -> FunctionAgent:
    """Create the agent with the RAG tool + the function tools."""
    llm = Groq(model=LLM_MODEL, api_key=api_key, temperature=0.1)

    rag_tool = QueryEngineTool.from_defaults(
        query_engine=index.as_query_engine(llm=llm, similarity_top_k=3),
        name="climate_knowledge_base",
        description=(
            "Science facts about climate change: causes, effects (sea level, heat, "
            "agriculture, health, ecosystems), solutions, and what the dataset variables mean."
        ),
    )
    function_tools = [
        FunctionTool.from_defaults(fn=fn)
        for fn in (get_yearly_stats, get_temperature_trend, get_hottest_days, calculate_carbon_footprint)
    ]
    return FunctionAgent(tools=[rag_tool] + function_tools, llm=llm, system_prompt=SYSTEM_PROMPT)


async def ask(agent: FunctionAgent, question: str, history: list):
    """Run the agent. Returns (answer_text, list_of_tool_names_used)."""
    response = await agent.run(user_msg=question, chat_history=history)
    tools_used = []
    for call in response.tool_calls:
        if call.tool_name not in tools_used:
            tools_used.append(call.tool_name)
    return str(response), tools_used
