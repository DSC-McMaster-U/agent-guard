from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.policy import evaluate_policy
from app.schemas import ToolCallRequest, ToolCallSummary
from app.validation import validate_email_arguments

app = FastAPI()

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.post("/api/v1/tool-calls", response_model=ToolCallSummary)
def create_tool_call(request: ToolCallRequest):
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

    return ToolCallSummary(
        request_id=request.request_id,
        agent_id=request.agent_id,
        tool=request.tool,
        arguments=request.arguments,
        decision=result["decision"],
        reason=result["reason"],
        timestamp=datetime.now(timezone.utc),
        approval_status="pending" if result["decision"] == "approval_required" else "not_required",
    )
