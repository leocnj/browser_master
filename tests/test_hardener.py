import pytest
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

def test_map_to_semantic_from_html_sibling():
    hardener = Hardener()
    step = {
        "action": "fill", 
        "element_html": '<div><span>Password</span><input></div>',
        "xpath": "//input"
    }
    mapped = hardener.map_to_semantic(step)
    assert mapped["label"] == "Password"
