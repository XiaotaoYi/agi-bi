# The main goal of query analyzer is to enrich questions to be more understandable by LLM to ensure it can make accurate and comprehensive plan.

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import os

class QueryAnalyzer:
    def __init__(self, db_path: str = "semantic/glossary/glossary.db"):
        self.db_path = db_path
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

    def get_abbreviations(self) -> List[Dict[str, str]]:
        """Read abbreviations from glossary database.
        
        Returns:
            List of dictionaries containing abbreviation data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT abbr, fullname, description FROM glossary_tbl")
        abbreviations = []
        for row in cursor.fetchall():
            abbreviations.append({
                "abbr": row[0],
                "fullname": row[1],
                "description": row[2]
            })
        
        conn.close()
        return abbreviations

    def build_prompt(self, question: str) -> str:
        """Build the prompt by combining template, task, abbreviations and question.
        
        Args:
            question: The user's question to analyze
            
        Returns:
            The complete prompt string
        """
        abbreviations = self.get_abbreviations()
        abbreviations_str = json.dumps(abbreviations, indent=2)
        
        prompt = self.prompt_template.replace("${task}", self.task)
        prompt = prompt.replace("${abbreviations}", abbreviations_str)
        prompt = prompt.replace("${question}", question)
        
        return prompt
    
    def process(self, question: str) -> str:
        

        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        from langchain_openai import ChatOpenAI

        DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your_deepseek_api_key")

        # 定义模板
        prompt_template = PromptTemplate(
            input_variables=["task", "abbreviations", "question"],
            template=self.prompt_template
        )

        # 创建链
        chain = LLMChain(
            llm=ChatOpenAI(temperature=0.7, openai_api_base='https://api.deepseek.com/v1', openai_api_key=DEEPSEEK_API_KEY, model="deepseek-chat"),
            prompt=prompt_template,
            verbose=True
        )

        # 执行链
        abbreviations_str = json.dumps(self.get_abbreviations(), indent=2)
        response = chain.invoke({"task": self.task, "abbreviations": abbreviations_str, "question": question})
        return response["text"]

#queryAnalyzer = QueryAnalyzer()
#print(queryAnalyzer.process("search gmv at the year 2024 by month"))