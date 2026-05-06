import pytest
import json
from unittest.mock import MagicMock
from src.hardener import Hardener

def test_filter_history_success_only():
    hardener = Hardener()
    logs = [
        {"step": 1, "action": "click", "success": True},
        {"step": 2, "action": "fill", "success": False},
        {"step": 3, "action": "click", "status": "success"} # Test string status
    ]
    filtered = hardener.filter_history(logs)
    assert len(filtered) == 2
    assert filtered[0]["step"] == 1
    assert filtered[1]["step"] == 3

def test_map_to_semantic_from_instruction():
    hardener = Hardener()
    
    # Test Click
    step1 = {"action": "click", "instruction": "Click Search", "xpath": "//button[1]"}
    mapped1 = hardener.map_to_semantic(step1)
    assert mapped1["text"] == "Search"
    assert "xpath" not in mapped1
    
    # Test Fill
    step2 = {"action": "fill", "instruction": "Fill Employee ID with 123", "xpath": "//input"}
    mapped2 = hardener.map_to_semantic(step2)
    assert mapped2["label"] == "Employee ID"
    assert "xpath" not in mapped2

def test_map_to_semantic_from_html_label():
    hardener = Hardener()
    step = {
        "action": "fill", 
        "element_html": '<div><label>User Name:</label><input></div>',
        "xpath": "//input"
    }
    mapped = hardener.map_to_semantic(step)
    assert mapped["label"] == "User Name"
    assert "xpath" not in mapped

def test_detect_verification_url_change():
    hardener = Hardener()
    history = [
        {"action": "goto", "url": "http://app.com/form", "success": True},
        {"action": "click", "text": "Submit", "success": True, "url": "http://app.com/success"}
    ]
    verified = hardener.detect_verification(history)
    assert len(verified) == 3
    assert verified[-1]["action"] == "verify"
    assert verified[-1]["type"] == "url"
    assert verified[-1]["value"] == "http://app.com/success"

def test_parameterize_mock_llm():
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "parameters": [{"name": "emp_id", "default": "123", "description": "Employee ID"}],
        "steps": [{"action": "fill", "label": "ID", "value": "{{emp_id}}"}]
    })
    mock_llm.complete.return_value = mock_response
    
    mock_context = MagicMock()
    mock_context.llm = mock_llm
    
    hardener = Hardener(context=mock_context)
    history = [{"action": "fill", "label": "ID", "value": "123"}]
    
    result = hardener.parameterize("Update ID 123", history)
    
    assert len(result["parameters"]) == 1
    assert result["parameters"][0]["name"] == "emp_id"
    assert result["steps"][0]["value"] == "{{emp_id}}"
    mock_llm.complete.assert_called_once()

def test_harden_full_orchestration():
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "parameters": [{"name": "emp_id", "default": "123", "description": "ID"}],
        "steps": [
            {"action": "goto", "url": "http://app.com"},
            {"action": "fill", "label": "ID", "value": "{{emp_id}}"},
            {"action": "verify", "type": "text", "value": "Saved"}
        ]
    })
    mock_llm.complete.return_value = mock_response
    mock_context = MagicMock()
    mock_context.llm = mock_llm
    
    hardener = Hardener(context=mock_context)
    raw_logs = [
        {"action": "goto", "url": "http://app.com", "success": True},
        {"action": "fill", "instruction": "Fill ID with 123", "xpath": "//input", "success": True, "value": "123"},
        {"action": "click", "text": "Save", "success": True, "element_html": "<span>Saved</span>"}
    ]
    
    result = hardener.harden("Update 123", raw_logs)
    
    assert "parameters" in result
    assert "steps" in result
    assert len(result["steps"]) == 3
    assert result["steps"][-1]["action"] == "verify"
