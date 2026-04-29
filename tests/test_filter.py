def test_filter_removes_errors():
    from src.filter import filter_history
    raw_history = [{"action": "click", "success": False}, {"action": "fill", "success": True}]
    result = filter_history(raw_history)
    assert len(result) == 1
    assert result[0]["action"] == "fill"
