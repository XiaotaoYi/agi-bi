from fastapi import APIRouter, Request, HTTPException
from controller.QueryProcessor import SQLProcessor

router = APIRouter()

db_path = "tools/sql_executor/order.db"  # Use your database path
processor = SQLProcessor(db_path)

@router.post("/api/query")
async def process_query(request: Request):
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