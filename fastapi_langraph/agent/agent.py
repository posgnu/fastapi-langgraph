import operator
from typing import Annotated, Any, AsyncGenerator, Dict, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from fastapi_langraph.agent.tools.mock_search import mock_search


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ReActAgent:
    def __init__(self) -> None:
        llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)
        self.tools = [mock_search]
        self.llm = llm.bind_tools(self.tools)
        self.tool_node = ToolNode(self.tools)
        self.graph: Runnable = self._create_graph()

    def _create_graph(self) -> Runnable:
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self.tool_node)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        workflow.add_edge("tools", "agent")
        return workflow.compile()

    def _agent_node(self, state: AgentState) -> Dict[str, Any]:
        result = self.llm.invoke(state["messages"])
        return {"messages": [result]}

    def _should_continue(self, state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        return "end"

    async def stream(self, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        # Use astream_events to get token-level streaming
        async for event in self.graph.astream_events(
            {"messages": [("user", query)]}, version="v1"
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    # Yield each token as it arrives
                    yield {"agent": {"messages": [{"content": content}]}}


react_agent: "ReActAgent" = ReActAgent()
