"""
Data module for CBT Chatbot Research System
Contains CBT flows and personality templates
"""

import json
import os
from typing import Dict, List, Any

def load_cbt_flows() -> Dict[str, List[Dict[str, str]]]:
    """Load CBT flow questions from JSON file"""
    file_path = os.path.join(os.path.dirname(__file__), 'cbt_flows.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_personality_templates() -> Dict[str, Dict[str, Any]]:
    """Load personality templates from JSON file"""
    file_path = os.path.join(os.path.dirname(__file__), 'personality_templates.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Export data loading functions
__all__ = ['load_cbt_flows', 'load_personality_templates']