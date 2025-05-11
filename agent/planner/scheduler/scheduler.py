import json
from pathlib import Path
from typing import List, Dict, Any
import os
from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class Scheduler:
    def __init__(self):
        self.prompt_template = self._read_prompt_template()
        self.task = self._read_task()

    def _read_prompt_template(self) -> str:
        """Read the prompt template from file."""
        template_path = Path(__file__).parent / "prompt_template.txt"
        with open(template_path, "r") as f:
            return f.read().strip()

    def _read_task(self) -> str:
        """Read the task instructions from file."""
        task_path = Path(__file__).parent / "task.txt"
        with open(task_path, "r") as f:
            return f.read().strip()

    def get_knowlege(self) -> str:
        """Read the semantic knowledge from file."""
        task_path = 'semantic/modeling_definition_language/user_order.yml'
        with open(task_path, "r") as f:
            return f.read().strip()
    def process(self, question: str) -> dict:
        llm = Tongyi(model_name="qwen-turbo", dashscope_api_key=os.environ["DASHSCOPE_API_KEY"], stream=True, verbose=True)

        # 定义模板
        prompt_template = PromptTemplate(
            input_variables=["task", "knowledge", "question"],
            template=self.prompt_template
        )
        
        # Create the chain
        chain = prompt_template | llm | StrOutputParser()
        
        # Prepare the input
        input_data = {
            "task": self.task,
            "knowledge": self.get_knowlege(),
            "question": question
        }
        
        # Run the chain
        response = chain.invoke(input_data)
        scheduler_obj = json.loads(response)

        return scheduler_obj

#scheduler = Scheduler()
#print(scheduler.process("search Gross Merchandise Volume at the year 2024 by month"))