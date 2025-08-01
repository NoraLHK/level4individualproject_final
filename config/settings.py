import os
import openai
from typing import Dict, Any

# Load OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_ENABLED = bool(openai.api_key)
#if not openai.api_key:
#    raise RuntimeError("Missing OPENAI_API_KEY")
if not OPENAI_ENABLED:
    import warnings
    warnings.warn("OPENAI_API_KEY not set. Advanced language features will be disabled.")

# Application Configuration
APP_CONFIG = {
    'name': 'CBT Chatbot Personality Research System',
    'version': '1.0.0',
    'description': 'Research system to evaluate how chatbot personality influences CBT therapeutic writing effectiveness',
    'author': 'Research Team',
    
    # Research Configuration
    'research': {
        'question': 'To what extent does mental health chatbot personalities (neutral extraversion and conscientiousness) influence overall effectiveness of Cognitive Behavioral Therapeutic writing?',
        'personalities': ['neutral', 'conscientiousness', 'extraversion'],
        'conditions': ['stress', 'anxiety', 'lowMood'],
        'data_collection': True,
        'export_enabled': True
    },
    
    # UI Configuration
    'ui': {
        'theme': 'light',
        'sidebar_expanded': True,
        'chat_container_height': 400,
        'input_height': 100,
        'show_progress': True,
        'show_personality_info': True
    },
    
    # Session Configuration
    'session': {
        'auto_save': True,
        'session_timeout': 3600,  # 1 hour in seconds
        'max_response_length': 2000,
        'min_response_length': 10
    },
    
    # File Paths
    'paths': {
        'data_dir': 'data',
        'exports_dir': 'exports',
        'assets_dir': 'assets',
        'cbt_flows_file': 'data/cbt_flows.json',
        'personality_templates_file': 'data/personality_templates.json',
        'styles_file': 'assets/styles.css'
    },
    
    # Export Configuration
    'export': {
        'formats': ['markdown', 'json', 'csv'],
        'include_metadata': True,
        'include_chat_history': True,
        'include_personality_analysis': True,
        'filename_format': 'cbt-journal-{condition}-{personality}-{date}'
    },
    
    # Validation Rules
    'validation': {
        'required_responses': True,
        'min_words_per_response': 3,
        'max_words_per_response': 500,
        'validate_input': True
    },
    
    # Analytics Configuration
    'analytics': {
        'track_response_length': True,
        'track_session_duration': True,
        'track_completion_rate': True,
        'track_personality_engagement': True,
        'export_analytics': True
    }
}

# Personality-specific configurations
PERSONALITY_CONFIG = {
    'neutral': {
        'target_response_length': 'moderate',
        'formality_level': 'balanced',
        'emotional_tone': 'neutral',
        'verbosity': 'moderate',
        'sentence_complexity': 'mixed'
    },
    'conscientiousness': {
        'target_response_length': 'detailed',
        'formality_level': 'formal',
        'emotional_tone': 'achievement_focused',
        'verbosity': 'high',
        'sentence_complexity': 'complex',
        'structure_emphasis': True,
        'planning_focus': True
    },
    'extraversion': {
        'target_response_length': 'enthusiastic',
        'formality_level': 'informal',
        'emotional_tone': 'positive_energetic',
        'verbosity': 'very_high',
        'sentence_complexity': 'varied',
        'social_focus': True,
        'enthusiasm_markers': True
    }
}

# CBT Configuration
CBT_CONFIG = {
    'stress': {
        'total_steps': 28,
        'core_categories': [
            'Situation/Trigger',
            'Thoughts', 
            'Mood',
            'Behaviors',
            'Physical Reactions',
            'Automatic Thoughts',
            'Cognitive Distortions',
            'Examine Evidence',
            'Balanced Thought',
            'Deeper Beliefs',
            'Action Planning',
            'Healthier Beliefs'
        ]
    },
    'anxiety': {
        'total_steps': 30,
        'core_categories': [
            'Situation/Trigger',
            'Thoughts',
            'Emotions', 
            'Behaviors',
            'Physical Reactions',
            'Anxious Predictions',
            'Thinking Traps',
            'Safety Behaviors',
            'Examine Evidence',
            'Balanced Thought',
            'Facing Fears',
            'Coping Strategy',
            'Underlying Beliefs',
            'New Beliefs',
            'Progress'
        ]
    },
    'lowMood': {
        'total_steps': 29,
        'core_categories': [
            'Situation/Trigger',
            'Thoughts',
            'Moods',
            'Behaviors', 
            'Physical Reactions',
            'Core Negative Beliefs',
            'Thinking Errors',
            'Examine Evidence',
            'Balanced Perspective',
            'Activity Review',
            'Behavioral Activation',
            'Deep-Seated Beliefs',
            'Healthier Beliefs',
            'Small Wins',
            'Future Resilience'
        ]
    }
}

# Research Metrics Configuration
METRICS_CONFIG = {
    'response_quality': [
        'word_count',
        'sentence_count',
        'emotional_depth',
        'insight_level',
        'specificity'
    ],
    'engagement_metrics': [
        'completion_rate',
        'response_time',
        'session_duration',
        'voluntary_detail_level'
    ],
    'therapeutic_outcomes': [
        'thought_restructuring_quality',
        'coping_strategy_development',
        'self_awareness_indicators',
        'action_planning_specificity'
    ]
}

def get_config(section: str = None) -> Dict[str, Any]:
    """Get configuration section or entire config"""
    if section:
        return globals().get(f'{section.upper()}_CONFIG', {})
    return APP_CONFIG

def get_file_path(file_key: str) -> str:
    """Get file path from configuration"""
    return APP_CONFIG['paths'].get(file_key, '')

def validate_config() -> bool:
    """Validate configuration completeness"""
    required_sections = ['research', 'ui', 'session', 'paths']
    return all(section in APP_CONFIG for section in required_sections)
