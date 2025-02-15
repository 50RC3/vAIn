import pytest
from modules.language.chatbot import (
    clean_user_input,
    process_nlp_input,
    get_response_from_intent,
    handle_user_message
)

@pytest.fixture
def user_id():
    return "test_user_123"

def test_clean_user_input():
    test_input = "  Hello, World!  "
    result = clean_user_input(test_input)
    assert isinstance(result, str)
    assert result == "hello, world!"

    with pytest.raises(ValueError):
        clean_user_input(None)

def test_get_response_from_intent():
    hello_input = "hello there"
    help_input = "i need help"
    
    hello_response = get_response_from_intent(hello_input)
    help_response = get_response_from_intent(help_input)
    
    assert isinstance(hello_response, str)
    assert isinstance(help_response, str)
    assert "hello" in hello_response.lower()
    assert "help" in help_response.lower()

def test_handle_user_message(user_id):
    test_message = "Hello, what can you do?"
    response = handle_user_message(user_id, test_message)
    
    assert isinstance(response, str)
    assert len(response) > 0

def test_process_nlp_input():
    test_input = "Test processing this text"
    result = process_nlp_input(test_input)
    
    assert isinstance(result, dict)
    assert "status" in result
