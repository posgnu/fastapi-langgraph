from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode
from fastapi_langraph.agent.tools.web_search import web_search_tool

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

class ReActAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.tools = [web_search_tool]
        self.tool_node = ToolNode(self.tools)
        self.prompt = self._create_prompt()
        self.graph = self._create_graph()

    def _create_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Please respond to the user's request only based on the given context.",
                ),
                ("user", "{input}"),
            ]
        )

    def _create_graph(self):
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

    def _agent_node(self, state):
        return {"messages": [self.llm.invoke(state["messages"])]}

    def _should_continue(self, state):
        if "tool_calls" in state["messages"][-1].additional_kwargs:
            return "continue"
        return "end"

    def stream(self, query: str):
        return self.graph.stream({"messages": [("user", query)]})

react_agent = ReActAgent()
