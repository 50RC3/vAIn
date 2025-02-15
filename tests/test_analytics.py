import pytest
import pandas as pd
from modules.analytics.insights import Insights
from pathlib import Path

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'task_type': ['NLP', 'Vision', 'NLP'],
        'status': ['success', 'failure', 'success'],
        'execution_time': [1.2, 2.3, 1.5],
        'interaction_timestamp': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'user_id': [1, 2, 1]
    })

@pytest.fixture
def insights(tmp_path, sample_data):
    # Create a temporary CSV file with sample data
    data_path = tmp_path / "test_data.csv"
    sample_data.to_csv(data_path, index=False)
    return Insights(str(data_path))

def test_insights_initialization(insights):
    assert isinstance(insights.data, pd.DataFrame)
    assert not insights.data.empty
    assert isinstance(insights.cleaned_data, pd.DataFrame)

def test_generate_performance_report(insights):
    report = insights.generate_performance_report()
    assert isinstance(report, pd.DataFrame)
    assert not report.empty
    assert 'execution_time' in report.columns.levels[1]

def test_analyze_user_interactions(insights):
    interactions = insights.analyze_user_interactions()
    assert isinstance(interactions, pd.Series)
    assert not interactions.empty

def test_invalid_data_source():
    with pytest.raises(FileNotFoundError):
        Insights("nonexistent_file.csv")

def test_generate_task_summary(insights):
    summary = insights.generate_task_summary()
    assert isinstance(summary, pd.DataFrame)
    assert not summary.empty
