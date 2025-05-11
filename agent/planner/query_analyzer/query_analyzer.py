import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import os
from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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
    
    def process(self, question: str) -> dict:
        llm = Tongyi(model_name="qwen-turbo", dashscope_api_key=os.environ["DASHSCOPE_API_KEY"], stream=True, verbose=True)

        # 定义模板
        prompt_template = PromptTemplate(
            input_variables=["task", "abbreviations", "question"],
            template=self.prompt_template
        )

        # Create the chain
        chain = prompt_template | llm | StrOutputParser()

        # 执行链
        abbreviations_str = json.dumps(self.get_abbreviations(), indent=2)
        response = chain.invoke({"task": self.task, "abbreviations": abbreviations_str, "question": question})

        analyzer_obj = json.loads(response["text"])

        return analyzer_obj

#queryAnalyzer = QueryAnalyzer()
#print(queryAnalyzer.process("search gmv at the year 2024 by month"))