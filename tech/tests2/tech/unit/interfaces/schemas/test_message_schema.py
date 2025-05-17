import pytest
from pydantic import BaseModel, ValidationError
from typing import Dict, Any

class Message(BaseModel):
    message: str

class TestMessage:
    def test_valid_message(self):
        data = {"message": "Hello, World!"}
        message = Message(**data)
        assert message.message == "Hello, World!"
        assert message.model_dump() == data

    def test_empty_message(self):
        data = {"message": ""}
        message = Message(**data)
        assert message.message == ""
        assert message.model_dump() == data

    def test_missing_message_field(self):
        data = {}
        with pytest.raises(ValidationError):
            Message(**data)

    def test_invalid_message_type(self):
        data = {"message": 123}
        with pytest.raises(ValidationError):
            Message(**data)

    def test_extra_fields(self):
        data = {"message": "Test", "extra_field": "value"}
        message = Message(**data)
        assert message.message == "Test"
        assert "extra_field" not in message.model_dump()

    def test_model_dump_json(self):
        message = Message(message="JSON test")
        json_data = message.model_dump_json()
        assert json_data == '{"message":"JSON test"}'

    def test_model_validation_from_raw(self):
        raw_data = '{"message":"Raw data test"}'
        message = Message.model_validate_json(raw_data)
        assert message.message == "Raw data test"

    def test_model_copy(self):
        original = Message(message="Original")
        copy = original.model_copy()
        assert original.message == copy.message
        copy.message = "Modified"
        assert original.message != copy.message

    def test_model_equals(self):
        msg1 = Message(message="Same")
        msg2 = Message(message="Same")
        msg3 = Message(message="Different")
        assert msg1 == msg2
        assert msg1 != msg3