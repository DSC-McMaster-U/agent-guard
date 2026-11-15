import pytest
from pydantic import ValidationError

from app.schemas import EmailSendArguments
from app.validation import validate_email_arguments


def valid_arguments():
    return {
        "recipient": "teammate@example.com",
        "subject": "Hi",
        "body": "Hello",
    }


def test_valid_arguments_are_accepted():
    result = validate_email_arguments(valid_arguments())
    assert isinstance(result, EmailSendArguments)


def test_missing_subject_is_rejected():
    data = valid_arguments()
    del data["subject"]
    with pytest.raises(ValidationError):
        validate_email_arguments(data)


def test_missing_body_is_rejected():
    data = valid_arguments()
    del data["body"]
    with pytest.raises(ValidationError):
        validate_email_arguments(data)


def test_malformed_recipient_is_rejected():
    data = valid_arguments()
    data["recipient"] = "not-an-email"
    with pytest.raises(ValidationError):
        validate_email_arguments(data)


def test_extra_key_is_rejected():
    data = valid_arguments()
    data["cc"] = "someone@example.com"
    with pytest.raises(ValidationError):
        validate_email_arguments(data)


def test_input_dictionary_is_not_changed():
    data = valid_arguments()
    validate_email_arguments(data)
    assert data == valid_arguments()
