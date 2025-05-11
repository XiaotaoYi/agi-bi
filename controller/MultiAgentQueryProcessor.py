import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from multi_agent.planner.query_analyzer.query_analyzer import QueryAnalyzer
from multi_agent.planner.scheduler.scheduler import Scheduler

class MultiAgentQueryProcessor:
    def processQuery(self, query: str):
        results = {}
        
        query_analyzer = QueryAnalyzer()
        analyzer_result = query_analyzer.process(question=query)
        if analyzer_result['is_data_analytics'] == True:
            scheduler = Scheduler()
            scheduler_obj = scheduler.process(query)
            
            print('Building agent workflow...')
        else:
            results = [{"error": "Not a data analytics query"}]
        
        return results

# 使用示例
if __name__ == "__main__":
    processor = MultiAgentQueryProcessor()
    user_query = "search gmv at the year 2024 by month"
    print(processor.processQuery(user_query))