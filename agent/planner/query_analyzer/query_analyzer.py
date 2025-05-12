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

    def getPromptTemplateStr(self) -> str:
        """Read the prompt template from memory."""
        return '''
                # Instruction
                you are an expert question refiner, please adhere to following guidelines to refine question.

                ## guidelines
                1. firstly find abbreviations in the question according to below abbreviations data, then replace abbreviation with fullname field.
                2. recognize whether the question is a data analytics or not

                The response should be a json format with 2 fields, one is question with refined question value, the other one is is_data_analytics with true or false value.
                Return only a raw JSON object without Markdown formatting, like this:
                {
                    "question":"who are you",
                    "is_data_analytics": True
                }

                # question
                {question}
               '''

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
            input_variables=["question"],
            template=self.getPromptTemplateStr
        )

        # Create the chain
        chain = prompt_template | llm | StrOutputParser()

        # 执行链
        #abbreviations_str = json.dumps(self.get_abbreviations(), indent=2)
        response = chain.invoke({"question": question})

        analyzer_obj = json.loads(response["text"])

        return analyzer_obj

#queryAnalyzer = QueryAnalyzer()
#print(queryAnalyzer.process("search gmv at the year 2024 by month"))