"""
CBT Chatbot model with personality-driven responses
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from data import load_cbt_flows, load_personality_templates
from config.personalities import PersonalityResponseGenerator
from utils.session_manager import SessionManager
from utils.response_processor import ResponseProcessor


class CBTChatbot:
    """Main chatbot class for CBT conversations"""
    
    def __init__(self):
        self.cbt_flows = load_cbt_flows()
        self.personality_templates = load_personality_templates()
        self.personality_generator = PersonalityResponseGenerator()
        self.session_manager = SessionManager()
        self.response_processor = ResponseProcessor()
        
        self.current_personality = 'neutral'
        self.current_condition = None
        self.current_step = 0
        self.conversation_history = []
        self.user_responses = {}
        
    def set_personality(self, personality: str) -> bool:
        """Set the chatbot personality"""
        if personality in ['neutral', 'conscientiousness', 'extraversion']:
            self.current_personality = personality
            return True
        return False
    
    def start_session(self, condition: str) -> Tuple[bool, str]:
        """Start a new CBT session for the specified condition"""
        if condition not in self.cbt_flows:
            return False, f"Unknown condition: {condition}"
        
        self.current_condition = condition
        self.current_step = 0
        self.conversation_history = []
        self.user_responses = {}
        
        session_id = self.session_manager.create_session(
            self.current_personality, 
            condition
        )
        
        welcome_msg = self.personality_generator.get_welcome_message(self.current_personality)
        condition_intro = self._get_condition_introduction(condition)
        first_question = self.get_current_question()
        
        self.conversation_history.extend([
            {'type': 'bot', 'message': welcome_msg, 'timestamp': datetime.now()},
            {'type': 'bot', 'message': condition_intro, 'timestamp': datetime.now()},
            {'type': 'bot', 'message': first_question['text'], 'timestamp': datetime.now()}
        ])
        
        return True, f"Started {condition} session with {self.current_personality} personality"
    
    def _get_condition_introduction(self, condition: str) -> str:
        """Get introduction message for the condition"""
        introductions = {
            'stress': "Great choice! Let's explore your stress using the CBT 5-Part Model. We'll examine how your situation, thoughts, emotions, behaviors, and physical reactions are all connected.",
            'anxiety': "Perfect! We'll examine your anxiety using CBT's comprehensive framework. This will help us understand your fears and develop strategies to manage them effectively.",
            'lowMood': "Excellent! Let's understand your low mood through the CBT 5-Part Model. We'll explore the connections between your thoughts, feelings, and behaviors to find pathways to feeling better."
        }
        return introductions.get(condition, f"Let's begin exploring your {condition} using CBT techniques.")
    
    def process_user_response(self, user_input: str) -> Tuple[bool, str, bool]:
        """Process user response and return (success, bot_response, session_complete)"""
        is_valid, validation_message = self.response_processor.validate_response(user_input)
        if not is_valid:
            return False, validation_message, False
        
        current_question = self.get_current_question()
        if not current_question:
            return False, "Session error: No current question found.", False
        
        self.user_responses[current_question['id']] = user_input
        
        self.conversation_history.append({
            'type': 'user',
            'message': user_input,
            'question_id': current_question['id'],
            'timestamp': datetime.now()
        })
        
        self.session_manager.add_response(
            current_question['id'],
            current_question['text'],
            user_input,
            current_question['category']
        )
        
        bot_response = self.personality_generator.generate_response(
            self.current_personality,
            current_question,
            user_input,
            self.current_step
        )
        
        self.conversation_history.append({
            'type': 'bot',
            'message': bot_response,
            'timestamp': datetime.now()
        })
        
        self.current_step += 1
        
        is_complete = self.current_step >= len(self.cbt_flows[self.current_condition])
        
        if not is_complete:
            next_question = self.get_current_question()
            if next_question:
                self.conversation_history.append({
                    'type': 'bot',
                    'message': next_question['text'],
                    'timestamp': datetime.now()
                })
                bot_response += f"\n\n{next_question['text']}"
        else:
            completion_message = "You've completed the CBT reflection process! This is a significant accomplishment. Would you like me to generate a journal summary of your session?"
            self.conversation_history.append({
                'type': 'bot',
                'message': completion_message,
                'timestamp': datetime.now()
            })
            bot_response += f"\n\n{completion_message}"
        
        return True, bot_response, is_complete
    
    def get_current_question(self) -> Optional[Dict[str, str]]:
        """Get the current question based on session state"""
        if not self.current_condition or self.current_step >= len(self.cbt_flows[self.current_condition]):
            return None
        
        return self.cbt_flows[self.current_condition][self.current_step]
    
    def get_question(self, condition: str, step: int) -> Optional[Dict[str, str]]:
        """Get a specific question by condition and step"""
        if condition not in self.cbt_flows or step >= len(self.cbt_flows[condition]):
            return None
        
        return self.cbt_flows[condition][step]
    
    def get_session_progress(self) -> Dict[str, Any]:
        """Get current session progress information"""
        if not self.current_condition:
            return {}
        
        total_questions = len(self.cbt_flows[self.current_condition])
        progress_percentage = (self.current_step / total_questions) * 100
        
        return {
            'condition': self.current_condition,
            'personality': self.current_personality,
            'current_step': self.current_step,
            'total_steps': total_questions,
            'progress_percentage': progress_percentage,
            'responses_completed': len(self.user_responses),
            'session_complete': self.current_step >= total_questions
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.conversation_history.copy()
    
    def get_user_responses(self) -> Dict[str, str]:
        """Get all user responses"""
        return self.user_responses.copy()
    
    def generate_session_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive session summary"""
        if not self.current_condition:
            return {}
        
        session_data = self.session_manager.complete_session()
        
        response_analytics = self.response_processor.export_response_analytics(
            self.user_responses,
            self.current_personality,
            self.current_condition
        )
        
        summary = {
            'session_metadata': {
                'condition': self.current_condition,
                'personality': self.current_personality,
                'start_time': self.conversation_history[0]['timestamp'] if self.conversation_history else None,
                'end_time': datetime.now(),
                'completion_status': 'complete' if self.current_step >= len(self.cbt_flows[self.current_condition]) else 'incomplete'
            },
            'progress_metrics': self.get_session_progress(),
            'conversation_analysis': {
                'total_exchanges': len([h for h in self.conversation_history if h['type'] == 'user']),
                'total_bot_responses': len([h for h in self.conversation_history if h['type'] == 'bot']),
                'conversation_length': len(self.conversation_history)
            },
            'response_analytics': response_analytics,
            'session_data': session_data,
            'therapeutic_outcomes': self._assess_therapeutic_outcomes()
        }
        
        return summary
    
    def _assess_therapeutic_outcomes(self) -> Dict[str, Any]:
        """Assess therapeutic outcomes based on response patterns"""
        if not self.user_responses:
            return {}
        
        outcomes = {
            'cognitive_restructuring_evidence': 0,
            'emotional_processing_depth': 0,
            'behavioral_insights': 0,
            'self_awareness_growth': 0,
            'coping_strategy_development': 0
        }
        
        for response_text in self.user_responses.values():
            response_lower = response_text.lower()
            
            if any(phrase in response_lower for phrase in ['balanced', 'realistic', 'alternative', 'different way']):
                outcomes['cognitive_restructuring_evidence'] += 1
            
            if any(phrase in response_lower for phrase in ['feel', 'emotion', 'mood', 'feelings']):
                outcomes['emotional_processing_depth'] += 1
            
            if any(phrase in response_lower for phrase in ['behavior', 'action', 'react', 'response']):
                outcomes['behavioral_insights'] += 1
            
            if any(phrase in response_lower for phrase in ['realize', 'understand', 'notice', 'pattern']):
                outcomes['self_awareness_growth'] += 1
            
            if any(phrase in response_lower for phrase in ['cope', 'manage', 'strategy', 'plan']):
                outcomes['coping_strategy_development'] += 1
        
        total_responses = len(self.user_responses)
        for key in outcomes:
            outcomes[key] = (outcomes[key] / total_responses) * 100 if total_responses > 0 else 0
        
        return outcomes
    
    def reset_session(self):
        """Reset the current session"""
        self.current_condition = None
        self.current_step = 0
        self.conversation_history = []
        self.user_responses = {}
        self.session_manager.clear_session_data()
    
    def switch_condition(self, new_condition: str) -> Tuple[bool, str]:
        """Switch to a different condition while maintaining personality"""
        if new_condition not in self.cbt_flows:
            return False, f"Unknown condition: {new_condition}"
        
        if self.current_condition and self.user_responses:
            self.session_manager.complete_session()
        
        return self.start_session(new_condition)
    
    def get_available_conditions(self) -> List[str]:
        """Get list of available CBT conditions"""
        return list(self.cbt_flows.keys())
    
    def get_available_personalities(self) -> List[str]:
        """Get list of available personalities"""
        return list(self.personality_templates.keys())
    
    def get_personality_info(self, personality: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific personality"""
        return self.personality_templates.get(personality)
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export complete session data for research purposes"""
        return {
            'session_summary': self.generate_session_summary(),
            'conversation_history': self.get_conversation_history(),
            'user_responses': self.get_user_responses(),
            'cbt_flow_data': {
                'condition': self.current_condition,
                'questions_asked': [
                    self.cbt_flows[self.current_condition][i] 
                    for i in range(min(self.current_step, len(self.cbt_flows[self.current_condition])))
                ] if self.current_condition else []
            },
            'personality_data': {
                'current_personality': self.current_personality,
                'personality_template': self.get_personality_info(self.current_personality)
            },
            'export_timestamp': datetime.now().isoformat()
        }