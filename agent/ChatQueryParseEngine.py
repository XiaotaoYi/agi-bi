from typing import Dict, List, Any, Literal, TypedDict, Optional
from langgraph.graph import StateGraph, END, START

class ChatQueryParseState(TypedDict):
    """context used in parsing phrase for chat scene"""
    # input
    query: str # user question

    # processing state
    mapping_info: Optional[Dict[str, Any]]  # map node output
    parsing_info: Optional[Dict[str, Any]]  # parse node output
    correction_info: Optional[Dict[str, Any]]  # correction node output
    transition_info: Optional[Dict[str, Any]]  # transition node output

    # output
    result_info: Optional[Dict[str, Any]]  # result

    # control flow
    current_phase: Optional[str]
    error: Optional[str]


class ChatQueryParseEngine:
    def process_mapping(self, state: ChatQueryParseState) -> ChatQueryParseState:
        pass
    def process_parsing(self, state: ChatQueryParseState) -> ChatQueryParseState:
        pass
    def process_correction(self, state: ChatQueryParseState) -> ChatQueryParseState:
        pass
    def process_transition(self, state: ChatQueryParseState) -> ChatQueryParseState:
        pass
    def process_result(self, state: ChatQueryParseState) -> ChatQueryParseState:
        pass

    def build_chat_query_parse_workflow(self) -> StateGraph:
        """create query parsing in chat scene"""

        workflow = StateGraph(ChatQueryParseState)
        workflow.add_node('start', START)
        workflow.add_node('mapping', self.process_mapping)
        workflow.add_node('parsing', self.process_parsing)
        workflow.add_node('correction', self.process_correction)
        workflow.add_node('transition', self.process_transition)
        workflow.add_node('result', self.process_result)
        workflow.add_node('end', END)

        workflow.add_edge('start', 'mapping')
        workflow.add_edge('mapping', 'parsing')
        workflow.add_edge('parsing', 'correction')
        workflow.add_edge('correction', 'transition')
        workflow.add_edge('transition', 'result')
        workflow.add_edge('result', 'end')

        return workflow.compile()

    
