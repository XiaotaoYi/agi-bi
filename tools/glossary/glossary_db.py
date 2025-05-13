import sqlite3
from typing import List, Dict, Any

class Glossary_db:
    def __init__(self, db_path: str = "semantic/glossary/glossary.db"):
        self.db_path = db_path
        self.name = "glossary data"
        self.description = "glossary data including abbreviation, terminology, jargon"
    
    def get_abbreviations(self, glossary: str) -> List[Dict[str, str]]:
        """Read abbreviation, terminology, jargon from glossary database.
        
        Returns:
            List of dictionaries containing abbreviation, terminology, jargon data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT abbr, description FROM glossary_tbl where abbr = '{glossary}'")
        abbreviations = []
        for row in cursor.fetchall():
            abbreviations.append({
                "abbr": row[0],
                "description": row[1]
            })
        
        conn.close()
        return abbreviations