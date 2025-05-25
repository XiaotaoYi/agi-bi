from fastapi import APIRouter, Request, HTTPException
from controller.QueryProcessor import SQLProcessor
from agent.ChatQueryParseEngine import *

router = APIRouter()
@router.post("/query/parse")
async def process_parse(request: Request):
    """API endpoint to process user queries"""

    data = await request.json()
    query = data.get('query', '')
    if not query:
        raise HTTPException(status_code=400, detail="查询不能为空")
    try:
        chatQueryParseEngine = ChatQueryParseEngine()
        agent_workflow = chatQueryParseEngine.build_chat_query_parse_workflow()

        print("LangGraph Mermaid workflow:")
        print(agent_workflow.get_graph().draw_mermaid())
        
        initial_state = {
        "query": query,
        "mapping_info": None,
        "parsing_info": None,
        "correction_info": None,
        "transition_info": None,
        "result_info": None,
        "current_phase": "start",
        "error": None
    }
        results = agent_workflow.invoke(initial_state)
        
        return {"result": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.post("/query/execute")
async def process_execute(request: Request):
    """API endpoint to process user queries"""
    data = await request.json()
    query = data.get('query', '')
    if not query:
        raise HTTPException(status_code=400, detail="查询不能为空")
    try:
        results = processor.process(query)
        return {"result": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 