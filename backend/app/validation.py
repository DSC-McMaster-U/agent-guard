"""Validate supported-tool arguments before policy evaluation."""

from typing import Any

from app.schemas import EmailSendArguments


def validate_email_arguments(arguments: Any) -> EmailSendArguments:
    """Return validated ``email.send`` arguments.

    Args:
        arguments: Tool arguments object from the normalized request.

    Returns:
        The validated ``EmailSendArguments``. The input is not modified.

    Raises:
        pydantic.ValidationError: If the arguments do not match
            ``EmailSendArguments``. The caller translates this into an HTTP error.
    """
    return EmailSendArguments.model_validate(arguments)
