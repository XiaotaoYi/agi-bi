import json
from pathlib import Path
from typing import List, Dict, Any
import os
import sys

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import Tool, AgentExecutor, create_react_agent
from tools.glossary.glossary_db import *
from tools.ml_model.glossary_detector.glossary_detector import *
from langchain.memory import ConversationBufferMemory

class QueryAnalyzer:
    def __init__(self):
        pass
    def build_prompt(self) -> str:
        return PromptTemplate.from_template(
        """You are an expert at refining user question, please adhere to following guidelines to refine question.
            
            Guidelines:
            Question: the question to answer
            Thought: You should always think which action to take. the action sequence is as follows.
                     1. Detect abbreviations, terminologies, jargons in a user question which is used to query business metrics.
                     2. Query abbreviation/terminology/jargon description from glossary database according to the result of step one.
                     3. Refine user question according to the result of step two. If the question is still not clear, please ask clarification from user who raise the question.
                     4. Decide whether the question is a data analysis question.
                        The question should contain at least one keyword from show me/trend/query/select/metric/metrics if it's a data analysis question.
            Action: tool name which must be one from [{tool_names}]
            Action Input: tool input
            Observation: tool result
            ... (You could repeate N times for Thought/Action/Action Input/Observation operation)
            Thought: I got the final answer
            Final Answer: final answer to original question

            Tools: {tools}
            Tool names: {tool_names}

            The final answer's output field should contain a json format with 3 fields, one is question with original question value, one is refined_question with the refined question value.
            one is is_data_analytics with true or false value. Return only a raw JSON object for the output value, like this:
            {{
                "question":"Show me tpv at the year 2024 by month",
                "refined_question":"Show me total payment volume at the year 2024 by month",
                "is_data_analytics": true
            }}

            Go!
            Question: {input}
            Thought: {agent_scratchpad}
        """
    )
    
    def process(self, question: str) -> dict:
        llm = Tongyi(model_name="qwen-turbo", dashscope_api_key=os.environ["DASHSCOPE_API_KEY"], stream=True, verbose=True)

        glossary_detector = Glossary_detector()
        glossary_db = Glossary_db()

        # 组合工具
        tools = [
            Tool(
                name=glossary_detector.name,
                func=glossary_detector.run,
                description=glossary_detector.description
            ),
            Tool(
                name=glossary_db.name,
                func=glossary_db.get_abbreviations,
                description=glossary_db.description
            )
        ]
        
        agent = create_react_agent(llm, tools, self.build_prompt())

        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=ConversationBufferMemory(memory_key="chat_history"),
            verbose=True,
            handle_parsing_errors=False  # 关闭自动重试, True会严格检查重试
        )

        response = agent_executor.invoke({"input": question})

        analyzer_obj = json.loads(response["output"])

        return analyzer_obj

queryAnalyzer = QueryAnalyzer()
print(queryAnalyzer.process("search tpv at the year 2024 by month"))