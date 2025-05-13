import json
from pathlib import Path
from typing import List, Dict, Any
import os
from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from semantic.modeling_definition_language.mdl_search import Mdl_Search
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory



class Scheduler:
    def __init__(self):
        pass
    def build_prompt(self) -> str:
        return PromptTemplate.from_template(
        """You are an expert data analyst, pls adhere to the following guidelines to answer data analytics question.
            
            Guidelines:
            Question: the question to answer
            Thought: You should always think using below idea and take next action.
                    1. First check if the question is data analytics related, if not, just reject the question and no other steps needed
                    2. Then check if the question is clear enough to start plan, if not, just reject the question and no other steps needed
                    3. Use the last 30 days as the default data range if no specific range is provided in the question
                    4. One data analytics question might need be divided into multiple sub-questions and draw conclusion based on sub question's answer
                    5. If the question is straightforward, you don't need divided it into sub-questions
                    6. For each question or sub-question, please think about what kind of data you need including description of necessary tables and columns with type
                    7. Please always include the analysis logic of dwawing conclusion based on sub-questions' anwser or questions' data query result
            Action: tool name which must be one from [{tool_names}]
            Action Input: tool input
            Observation: tool result
            ... (You could repeate N times for Thought/Action/Action Input/Observation operation)
            Thought: I got the final answer
            Final Answer: final answer to original question

            Tools: {tools}
            Tool names: {tool_names}

            The final answer's output field should contain a json format,  Return only a raw JSON object with no markdown format for the output value like this:
            {{
                // The step-by-step task to answer the question, number of tasks determines how many elements put int the tasks dict
                tasks: [
                    {{
                        // index refer to task requence
                        index: number,
                        // task type must be one of the following: clarify_question, reject_no_analytics_question,query_table,summarize_result
                        task_type: string,
                        // task detail refers to what to do for this task, for task_type as clarify_question, task_detail must contain what need to be clarified;
                        // for task_type as query_table, task_detail must contain description of necessary tables and columns with type together with what to get from querying the tables;
                        // for task_type as summarize_result, task_detail must contain the analysis logic based on query_table task's result
                        task_detail: string
                    }}
                ]
            }}

            Go!
            Question: {input}
            Thought: {agent_scratchpad}
        """)

    def process(self, question: str) -> dict:
        llm = Tongyi(model_name="deepseek-r1", dashscope_api_key=os.environ["DASHSCOPE_API_KEY"], stream=True, verbose=True)

        mdl_search = Mdl_Search()

        # 组合工具
        tools = [
            Tool(
                name=mdl_search.name,
                func=mdl_search.run,
                description=mdl_search.description
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

        scheduler_obj = json.loads(response["output"])

        return scheduler_obj

scheduler = Scheduler()
print(scheduler.process("search tpv(total payment volume) at the year 2024 by month"))