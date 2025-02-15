import pytest
from modules.language.nlp_pipeline import (
    clean_text,
    tokenize_text,
    perform_ner,
    pos_tagging,
    remove_stopwords
)

@pytest.fixture
def sample_text():
    return "John Doe works at Google in New York. He loves programming."

def test_clean_text():
    text = "Hello! This is a test... 123"
    result = clean_text(text)
    assert isinstance(result, str)
    assert "123" not in result
    assert "..." not in result

def test_tokenize_text():
    text = "Hello world"
    tokens = tokenize_text(text)
    assert isinstance(tokens, list)
    assert len(tokens) == 2
    assert "Hello" in tokens
    assert "world" in tokens

def test_perform_ner(sample_text):
    entities = perform_ner(sample_text)
    assert isinstance(entities, list)
    assert len(entities) > 0
    assert all(isinstance(e, dict) for e in entities)
    assert all("text" in e and "label" in e for e in entities)

def test_pos_tagging():
    tokens = ["I", "love", "programming"]
    tagged = pos_tagging(tokens)
    assert isinstance(tagged, list)
    assert len(tagged) == 3
    assert all(isinstance(t, tuple) and len(t) == 2 for t in tagged)

def test_remove_stopwords():
    tokens = ["I", "am", "a", "programmer"]
    filtered = remove_stopwords(tokens)
    assert isinstance(filtered, list)
    assert "programmer" in filtered
    assert "a" not in filtered
