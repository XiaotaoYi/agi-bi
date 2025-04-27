import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import os

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
    def process(self, question: str) -> str:

        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        from langchain_openai import ChatOpenAI

        DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your_deepseek_api_key")

        # 定义模板
        prompt_template = PromptTemplate(
            input_variables=["task", "knowledge", "question"],
            template=self.prompt_template
        )

        # 创建链
        chain = LLMChain(
            llm=ChatOpenAI(temperature=0.7, openai_api_base='https://api.deepseek.com/v1', openai_api_key=DEEPSEEK_API_KEY, model="deepseek-reasoner"),
            prompt=prompt_template,
            verbose=True
        )

        # 执行链
        response = chain.invoke({"task": self.task, "knowledge": self.get_knowlege(), "question": question})
        return response["text"]

scheduler = Scheduler()
print(scheduler.process("search Gross Merchandise Volume at the year 2024 by month"))