from fastapi import APIRouter, HTTPException
from app.model.schemas import ClassSchema, DataSchema, QuerySchema
from app.services.weaviate_client import get_weaviate_session

router = APIRouter()

@router.post("/weaviate/schema")
async def create_schema(schema: ClassSchema):
    session = get_weaviate_session()
    payload = {
        "class": schema.class_name,
        "properties": [prop.dict() for prop in schema.properties]
    }
    response = session.post(f"{session.base_url}/v1/schema", json=payload)
    response.raise_for_status()
    return {"message": "Schema created successfully", "response": response.json()}

@router.post("/weaviate/data")
async def add_data(data: DataSchema):
    session = get_weaviate_session()
    payload = {
        "class": data.class_name,
        "properties": data.properties
    }
    response = session.post(f"{session.base_url}/v1/objects", json=payload)
    response.raise_for_status()
    return {"message": "Data added successfully", "response": response.json()}

@router.post("/weaviate/query")
async def query_data(query: QuerySchema):
    session = get_weaviate_session()
    graphql_query = {
        "query": f"{{ Get {{ {query.class_name} {{ {', '.join(query.properties)} }} }} }}"
    }
    response = session.post(f"{session.base_url}/v1/graphql", json=graphql_query)
    response.raise_for_status()
    return {"message": "Query executed successfully", "response": response.json()}