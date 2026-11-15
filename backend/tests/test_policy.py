import pytest

from app.policy import evaluate_policy


def email_args(recipient="teammate@example.com", **extra):
    return {"recipient": recipient, "subject": "Notes", "body": "Hi.", **extra}


@pytest.mark.parametrize(
    ("recipient", "decision"),
    [
        ("teammate@example.com", "allow"),
        ("blocked@example.net", "block"),
        ("partner@example.org", "approval_required"),
    ],
)
def test_demo_recipients(recipient, decision):
    result = evaluate_policy("assistant_2", "email.send", email_args(recipient))
    assert result["decision"] == decision
    assert result["reason"]
    assert set(result) == {"decision", "reason"}


def test_support_assistant_is_permitted():
    result = evaluate_policy("support-assistant", "email.send", email_args())
    assert result["decision"] == "allow"


def test_unknown_agent_is_blocked():
    result = evaluate_policy("intruder", "email.send", email_args())
    assert result["decision"] == "block"
    assert "intruder" in result["reason"]


def test_unsupported_tool_is_blocked():
    result = evaluate_policy("assistant_2", "email.forward_all", email_args())
    assert result["decision"] == "block"
    assert "email.forward_all" in result["reason"]


def test_tool_name_is_case_sensitive():
    result = evaluate_policy("assistant_2", "Email.Send", email_args())
    assert result["decision"] == "block"


def test_caller_permission_list_grants_nothing():
    arguments = email_args(permitted_tools=["email.send"])
    result = evaluate_policy("intruder", "email.send", arguments)
    assert result["decision"] == "block"


@pytest.mark.parametrize(
    "recipient",
    ["TEAMMATE@EXAMPLE.COM", "teammate@Example.Com"],
)
def test_internal_domain_matches_case_insensitively(recipient):
    result = evaluate_policy("assistant_2", "email.send", email_args(recipient))
    assert result["decision"] == "allow"


@pytest.mark.parametrize(
    "recipient",
    [
        "x@example.com.evil",
        "x@evil-example.com",
        "x@notexample.com",
        "x@mail.example.com",
        "x@exаmple.com",  # Cyrillic "а" lookalike
    ],
)
def test_lookalike_internal_domain_is_not_allowed(recipient):
    result = evaluate_policy("assistant_2", "email.send", email_args(recipient))
    assert result["decision"] == "approval_required"


@pytest.mark.parametrize(
    "recipient",
    ["x@EXAMPLE.NET", "x@mail.example.net", "x@a.b.example.net"],
)
def test_denied_domain_covers_case_and_subdomains(recipient):
    result = evaluate_policy("assistant_2", "email.send", email_args(recipient))
    assert result["decision"] == "block"


def test_denied_match_respects_label_boundary():
    result = evaluate_policy("assistant_2", "email.send", email_args("x@notexample.net"))
    assert result["decision"] == "approval_required"


@pytest.mark.parametrize(
    "recipient",
    [
        None,
        42,
        "",
        "partner-at-example.org",
        "a@b@example.com",
        "@example.com",
        "teammate@",
        "teammate@localhost",
        "teammate@.example.com",
        "teammate@example.com.",
        "teammate@example..com",
        " teammate@example.com",
        "team mate@example.com",
    ],
)
def test_malformed_recipient_is_blocked(recipient):
    result = evaluate_policy("assistant_2", "email.send", email_args(recipient))
    assert result["decision"] == "block"


def test_missing_recipient_is_blocked():
    result = evaluate_policy("assistant_2", "email.send", {"subject": "Hi", "body": "Hi."})
    assert result["decision"] == "block"


@pytest.mark.parametrize("arguments", [None, [], "teammate@example.com"])
def test_non_object_arguments_are_blocked(arguments):
    result = evaluate_policy("assistant_2", "email.send", arguments)
    assert result["decision"] == "block"


@pytest.mark.parametrize("key", ["cc", "bcc", "attachments"])
def test_unexpected_email_argument_is_blocked(key):
    arguments = email_args(**{key: "outsider@example.org"})
    result = evaluate_policy("assistant_2", "email.send", arguments)
    assert result["decision"] == "block"
    assert key in result["reason"]


def test_unsupported_tool_reason_wins_over_unknown_agent():
    result = evaluate_policy("intruder", "email.forward_all", email_args())
    assert "email.forward_all" in result["reason"]
