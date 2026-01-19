import os
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import opik
from strands.telemetry import StrandsTelemetry

from test_opik.agent.orchestrator import get_orchestrator_agent
import logging

logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    message: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    opik.configure(
        api_key=os.environ.get("OPIK_API_KEY"),
        workspace="opik-test",
        automatic_approvals=True,
    )
    strands_telemetry = StrandsTelemetry()
    strands_telemetry.setup_otlp_exporter(
        endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
        headers=os.environ.get("OTEL_EXPORTER_OTLP_HEADERS"),
    )

    # Optional: Also log to console for debugging
    strands_telemetry.setup_console_exporter()
    yield


@app.post("/llm")
async def query_agent(
    request: MessageRequest, orchestrator_agent=Depends(get_orchestrator_agent)
):
    """Query the orchestrator agent with a natural language question about the data."""
    if not request.message:
        return {
            "message": "Pass a question to the LLM agent via the 'message' field in JSON body.",
            "example": '{"message": "What are the top 5 records by value?"}',
        }

    if orchestrator_agent is None:
        raise HTTPException(
            status_code=503, detail="Orchestrator agent not initialized"
        )

    try:
        result = await orchestrator_agent.run(request.message)
        return {
            "query": request.message,
            "result": result.message["content"][0]["text"],
        }
    except Exception as e:
        print(f"Error processing query: {result.__dict__}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/")
async def root() -> str:
    return "test"
