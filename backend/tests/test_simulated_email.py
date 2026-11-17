import json

import pytest

from app.schemas import EmailSendArguments
from app.tools import email as email_tool
from app.tools.email import (
    APPROVAL_REQUIRED_REASON,
    BLOCKED_REASON,
    INVALID_ARGUMENTS_REASON,
    UNKNOWN_DECISION_REASON,
    dispatch_simulated_email,
    simulate_email_send,
)


def make_arguments():
    return EmailSendArguments(
        recipient="alex@example.com",
        subject="Quarterly report",
        body="Please find the summary attached.",
    )


@pytest.fixture
def spy(monkeypatch):
    calls = []
    real = email_tool.simulate_email_send

    def record(arguments):
        calls.append(arguments)
        return real(arguments)

    monkeypatch.setattr(email_tool, "simulate_email_send", record)
    return calls


def test_simulate_email_send_returns_simulated_result():
    assert simulate_email_send(make_arguments()) == {
        "tool": "email.send",
        "delivery_status": "simulated",
        "recipient": "alex@example.com",
        "subject": "Quarterly report",
        "body": "Please find the summary attached.",
    }


def test_simulate_email_send_returns_new_dictionary_each_call():
    arguments = make_arguments()
    first = simulate_email_send(arguments)
    first["recipient"] = "attacker@example.net"
    assert simulate_email_send(arguments)["recipient"] == "alex@example.com"


def test_allow_dispatches_to_simulated_send(spy):
    arguments = make_arguments()
    result = dispatch_simulated_email(arguments, "allow")
    assert spy == [arguments]
    assert result == simulate_email_send(arguments)


@pytest.mark.parametrize(
    ("decision", "reason"),
    [
        ("block", BLOCKED_REASON),
        ("approval_required", APPROVAL_REQUIRED_REASON),
        ("Allow", UNKNOWN_DECISION_REASON),
        (" allow", UNKNOWN_DECISION_REASON),
        ("approved", UNKNOWN_DECISION_REASON),
        ("", UNKNOWN_DECISION_REASON),
        (None, UNKNOWN_DECISION_REASON),
        (True, UNKNOWN_DECISION_REASON),
        (1, UNKNOWN_DECISION_REASON),
        (["allow"], UNKNOWN_DECISION_REASON),
        ({"decision": "allow", "reason": "Recipient is inside the organization."}, UNKNOWN_DECISION_REASON),
    ],
)
def test_non_allow_decisions_never_execute(spy, decision, reason):
    result = dispatch_simulated_email(make_arguments(), decision)
    assert spy == []
    assert result == {"tool": "email.send", "delivery_status": "not_executed", "reason": reason}


class AllowLike(str):
    """A str subclass that claims equality with anything."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


def test_str_subclass_decision_never_executes(spy):
    result = dispatch_simulated_email(make_arguments(), AllowLike("block"))
    assert spy == []
    assert result["delivery_status"] == "not_executed"


@pytest.mark.parametrize(
    "arguments",
    [
        {"recipient": "alex@example.com", "subject": "Hi", "body": "Hello"},
        EmailSendArguments.model_construct(recipient="not-an-email", subject="", body=""),
        None,
    ],
)
def test_unvalidated_arguments_never_execute(spy, arguments):
    result = dispatch_simulated_email(arguments, "allow")
    assert spy == []
    assert result == {
        "tool": "email.send",
        "delivery_status": "not_executed",
        "reason": INVALID_ARGUMENTS_REASON,
    }


@pytest.mark.parametrize("decision", ["allow", "block", "approval_required", None])
def test_dispatch_leaves_arguments_unchanged(decision):
    arguments = make_arguments()
    before = arguments.model_dump()
    result = dispatch_simulated_email(arguments, decision)
    result["recipient"] = "attacker@example.net"
    assert arguments.model_dump() == before


@pytest.mark.parametrize("decision", ["allow", "block", "approval_required", None])
def test_results_are_json_serializable(decision):
    result = dispatch_simulated_email(make_arguments(), decision)
    assert json.loads(json.dumps(result)) == result
