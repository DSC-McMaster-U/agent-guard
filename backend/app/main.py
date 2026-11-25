from datetime import datetime, timezone
import psycopg
from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from psycopg import Connection
from pydantic import ValidationError
from app.database import get_connection
from app.policy import evaluate_policy
from app.schemas import ToolCallRequest, ToolCallSummary
from app.storage import DuplicateRequestError, list_summaries, save_summary
from app.validation import validate_email_arguments
from app.decision import combine_decision
from app.security.prompt_injection import detect_prompt_injection

app = FastAPI()

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.post("/api/v1/tool-calls", response_model=ToolCallSummary)
def create_tool_call(
    request: ToolCallRequest,
    connection: Connection = Depends(get_connection),
):
    if request.tool == "email.send":
        try:
            validate_email_arguments(request.arguments)
        except ValidationError as exc:
            errors = [
                {
                    **{key: value for key, value in error.items() if key != "input"},
                    "loc": ("body", "arguments") + tuple(error["loc"]),
                }
                for error in exc.errors()
            ]
            raise RequestValidationError(errors) from None

    result = evaluate_policy(request.agent_id, request.tool, request.arguments)

    if request.trigger_source is None:
        findings=[]
    else:
        findings=detect_prompt_injection(request.trigger_source.content, request.trigger_source.type)
    final=combine_decision(result,findings)

    summary = ToolCallSummary(
        request_id=request.request_id,
        agent_id=request.agent_id,
        tool=request.tool,
        arguments=request.arguments,
        decision=final["decision"],
        reason=final["reason"],
        timestamp=datetime.now(timezone.utc),
        approval_status="pending" if final["decision"] == "approval_required" else "not_required",
    )

    try:
        with connection:
            save_summary(connection, summary)
    except DuplicateRequestError:
        raise HTTPException(
            status_code=409, detail="A request with this ID already exists"
        ) from None
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return summary

@app.get("/api/v1/tool-calls", response_model=list[ToolCallSummary])
def list_tool_calls(connection: Connection = Depends(get_connection)):
    try:
        return list_summaries(connection, limit=20)
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database unavailable") from None