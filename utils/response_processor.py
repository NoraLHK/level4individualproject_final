"""
Response processing utilities for CBT Chatbot Research System
"""

import re
import json
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import streamlit as st


class ResponseProcessor:
    """Processes and analyzes user responses for therapeutic content"""
    
    def __init__(self):
        self.therapeutic_indicators = self._load_therapeutic_indicators()
        self.validation_rules = self._load_validation_rules()
        
    def _load_therapeutic_indicators(self) -> Dict[str, List[str]]:
        """Load indicators of therapeutic engagement and insight"""
        return {
            'self_awareness': [
                'i realize', 'i notice', 'i understand', 'i recognize', 'i see',
                'pattern', 'connection', 'relationship', 'impact', 'effect',
                'trigger', 'cause', 'lead to', 'result in'
            ],
            'emotional_processing': [
                'feel', 'felt', 'emotion', 'emotional', 'mood', 'feelings',
                'anxious', 'sad', 'angry', 'frustrated', 'overwhelmed',
                'hopeful', 'calm', 'peaceful', 'content', 'relieved'
            ],
            'cognitive_restructuring': [
                'thought', 'think', 'believe', 'assumption', 'expectation',
                'realistic', 'balanced', 'alternative', 'different way',
                'perspective', 'viewpoint', 'evidence', 'proof'
            ],
            'behavioral_insight': [
                'behavior', 'action', 'reaction', 'response', 'habit',
                'avoid', 'escape', 'withdraw', 'engage', 'participate',
                'cope', 'manage', 'handle', 'deal with'
            ],
            'future_orientation': [
                'will', 'plan', 'goal', 'hope', 'expect', 'next time',
                'future', 'tomorrow', 'later', 'going to', 'intend'
            ],
            'self_compassion': [
                'kind to myself', 'forgive myself', 'understanding',
                'gentle', 'patient', 'compassionate', 'accepting',
                'human', 'normal', 'understandable'
            ]
        }
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load response validation rules"""
        return {
            'min_length': 10,
            'max_length': 2000,
            'min_words': 3,
            'max_words': 500,
            'required_engagement': True,
            'block_inappropriate': True
        }
    
    def validate_response(self, response: str) -> Tuple[bool, Optional[str]]:
        """Validate user response and return validation result with message"""
        
        if not response or not response.strip():
            return False, "Please provide a response to continue."
        
        response = response.strip()
        
        if len(response) < self.validation_rules['min_length']:
            return False, f"Please provide a more detailed response (at least {self.validation_rules['min_length']} characters)."
        
        if len(response) > self.validation_rules['max_length']:
            return False, f"Response is too long. Please keep it under {self.validation_rules['max_length']} characters."
        
        word_count = len(response.split())
        if word_count < self.validation_rules['min_words']:
            return False, f"Please provide at least {self.validation_rules['min_words']} words in your response."
        
        if word_count > self.validation_rules['max_words']:
            return False, f"Response is too long. Please keep it under {self.validation_rules['max_words']} words."
        
        if self.validation_rules['block_inappropriate']:
            is_appropriate, message = self._check_appropriate_content(response)
            if not is_appropriate:
                return False, message
        
        if self.validation_rules['required_engagement']:
            is_engaged, message = self._check_engagement_level(response)
            if not is_engaged:
                return False, message
        
        return True, None
    
    def _check_appropriate_content(self, response: str) -> Tuple[bool, Optional[str]]:
        """Check if response contains appropriate content for therapeutic context"""
        
        inappropriate_patterns = [
            r'\b(kill|die|death|suicide|harm)\s+myself\b',
            r'\bsuicide\b',
            r'\bharm\s+others\b',
            r'\bviolent\b.*\bthoughts\b',
            r'\bsubstance\s+abuse\b'
        ]
        
        response_lower = response.lower()
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, response_lower):
                return False, "Your response contains content that requires professional support. Please consider reaching out to a mental health professional or crisis helpline."
        
        return True, None
    
    def _check_engagement_level(self, response: str) -> Tuple[bool, Optional[str]]:
        """Check if response shows adequate engagement with the question"""
        
        minimal_responses = [
            'yes', 'no', 'maybe', 'idk', "i don't know", 'nothing',
            'not sure', 'dunno', 'nope', 'yep', 'fine', 'ok', 'okay'
        ]
        
        response_words = response.lower().split()
        
        if len(response_words) <= 2 and any(word in minimal_responses for word in response_words):
            return False, "Please provide a more detailed response to help us understand your experience better."
        
        unique_words = set(response_words)
        if len(response_words) > 5 and len(unique_words) / len(response_words) < 0.3:
            return False, "Please provide a more varied response with different thoughts and details."
        
        return True, None
    
    def analyze_response_quality(self, response: str, question_category: str) -> Dict[str, Any]:
        """Analyze response quality and therapeutic indicators"""
        
        analysis = {
            'word_count': len(response.split()),
            'character_count': len(response),
            'sentence_count': len(re.split(r'[.!?]+', response)) - 1,
            'therapeutic_indicators': self._count_therapeutic_indicators(response),
            'emotional_depth': self._assess_emotional_depth(response),
            'specificity_score': self._assess_specificity(response),
            'insight_level': self._assess_insight_level(response),
            'category_relevance': self._assess_category_relevance(response, question_category),
            'readability_score': self._calculate_readability(response)
        }
        
        analysis['overall_quality_score'] = self._calculate_quality_score(analysis)
        
        return analysis
    
    def _count_therapeutic_indicators(self, response: str) -> Dict[str, int]:
        """Count therapeutic indicators in response"""
        response_lower = response.lower()
        indicator_counts = {}
        
        for category, indicators in self.therapeutic_indicators.items():
            count = 0
            for indicator in indicators:
                count += len(re.findall(r'\b' + re.escape(indicator) + r'\b', response_lower))
            indicator_counts[category] = count
        
        return indicator_counts
    
    def _assess_emotional_depth(self, response: str) -> float:
        """Assess emotional depth and processing in response"""
        
        emotion_words = [
            'feel', 'felt', 'emotion', 'emotional', 'mood', 'feelings',
            'anxious', 'nervous', 'worried', 'scared', 'afraid',
            'sad', 'depressed', 'hopeless', 'empty', 'numb',
            'angry', 'frustrated', 'irritated', 'annoyed',
            'happy', 'joyful', 'content', 'peaceful', 'calm',
            'excited', 'enthusiastic', 'motivated', 'hopeful',
            'overwhelmed', 'stressed', 'tense', 'relaxed'
        ]
        
        response_lower = response.lower()
        emotion_count = sum(1 for word in emotion_words if word in response_lower)
        
        personal_emotion_patterns = [
            r'i feel', r'i felt', r'i am', r"i'm", r'i was',
            r'made me feel', r'it feels', r'feeling'
        ]
        
        personal_count = sum(1 for pattern in personal_emotion_patterns 
                           if re.search(pattern, response_lower))
        
        word_count = len(response.split())
        depth_score = min(100, ((emotion_count + personal_count * 2) / max(word_count / 10, 1)) * 100)
        
        return depth_score
    
    def _assess_specificity(self, response: str) -> float:
        """Assess specificity and detail in response"""
        
        specificity_indicators = [
            'when', 'where', 'how', 'why', 'what', 'who',
            'because', 'since', 'due to', 'as a result',
            'for example', 'such as', 'like', 'including',
            'specifically', 'particularly', 'especially'
        ]
        
        response_lower = response.lower()
        specificity_count = sum(1 for indicator in specificity_indicators 
                              if indicator in response_lower)
        
        concrete_patterns = [
            r'\b\d+\b',
            r'\b(yesterday|today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(morning|afternoon|evening|night)\b',
            r'\b(home|work|school|office|gym|store)\b'
        ]
        
        concrete_count = sum(1 for pattern in concrete_patterns 
                           if re.search(pattern, response_lower))
        
        word_count = len(response.split())
        specificity_score = min(100, ((specificity_count + concrete_count) / max(word_count / 15, 1)) * 100)
        
        return specificity_score
    
    def _assess_insight_level(self, response: str) -> float:
        """Assess level of insight and self-awareness in response"""
        
        insight_patterns = [
            r'i realize', r'i understand', r'i see', r'i notice',
            r'i recognize', r'i learned', r'i discovered',
            r'pattern', r'connection', r'relationship',
            r'this shows', r'this means', r'this suggests',
            r'because', r'since', r'as a result', r'therefore',
            r'leads to', r'causes', r'triggers', r'affects'
        ]
        
        response_lower = response.lower()
        insight_count = sum(1 for pattern in insight_patterns 
                          if re.search(pattern, response_lower))
        
        causal_patterns = [
            r'if.*then', r'when.*i', r'because.*i',
            r'this makes me', r'which leads to', r'resulting in'
        ]
        
        causal_count = sum(1 for pattern in causal_patterns 
                         if re.search(pattern, response_lower))
        
        word_count = len(response.split())
        insight_score = min(100, ((insight_count + causal_count * 2) / max(word_count / 20, 1)) * 100)
        
        return insight_score
    
    def _assess_category_relevance(self, response: str, category: str) -> float:
        """Assess how well response addresses the question category"""
        
        category_keywords = {
            'Situation/Trigger': ['situation', 'event', 'happened', 'occurred', 'trigger', 'when'],
            'Thoughts': ['thought', 'think', 'believe', 'mind', 'ideas', 'opinion'],
            'Emotions': ['feel', 'emotion', 'mood', 'emotional', 'feelings'],
            'Behaviors': ['did', 'action', 'behavior', 'react', 'response', 'avoid'],
            'Physical Reactions': ['body', 'physical', 'symptoms', 'tension', 'heart', 'breathing'],
            'Cognitive Distortions': ['thinking', 'pattern', 'assumption', 'belief'],
            'Examine Evidence': ['evidence', 'proof', 'support', 'fact', 'true', 'reality'],
            'Balanced Thought': ['balanced', 'realistic', 'alternative', 'different', 'helpful'],
            'Action Planning': ['plan', 'action', 'step', 'do', 'will', 'going to']
        }
        
        keywords = category_keywords.get(category, [])
        if not keywords:
            return 50.0
        
        response_lower = response.lower()
        relevance_count = sum(1 for keyword in keywords if keyword in response_lower)
        
        relevance_score = min(100, (relevance_count / len(keywords)) * 100)
        
        return relevance_score
    
    def _calculate_readability(self, response: str) -> float:
        """Calculate readability score"""
        
        sentences = len(re.split(r'[.!?]+', response)) - 1
        words = len(response.split())
        syllables = self._count_syllables(response)
        
        if sentences == 0 or words == 0:
            return 0.0
        
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        
        return max(0, min(100, score))
    
    def _count_syllables(self, text: str) -> int:
        """Estimate syllable count in text"""
        words = re.findall(r'\b\w+\b', text.lower())
        syllable_count = 0
        
        for word in words:
            vowels = 'aeiouy'
            count = 0
            prev_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    count += 1
                prev_was_vowel = is_vowel
            
            if word.endswith('e') and count > 1:
                count -= 1
            
            syllable_count += max(1, count)
        
        return syllable_count
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall response quality score"""
        
        weights = {
            'word_count': 0.1,
            'emotional_depth': 0.25,
            'specificity_score': 0.2,
            'insight_level': 0.25,
            'category_relevance': 0.2
        }
        
        word_score = min(100, max(0, (analysis['word_count'] - 5) / 95 * 100))
        
        quality_score = (
            weights['word_count'] * word_score +
            weights['emotional_depth'] * analysis['emotional_depth'] +
            weights['specificity_score'] * analysis['specificity_score'] +
            weights['insight_level'] * analysis['insight_level'] +
            weights['category_relevance'] * analysis['category_relevance']
        )
        
        return quality_score
    
    def generate_feedback_suggestions(self, analysis: Dict[str, Any], 
                                    personality: str) -> List[str]:
        """Generate personality-appropriate feedback suggestions"""
        
        suggestions = []
        
        if analysis['emotional_depth'] < 30:
            if personality == 'extraversion':
                suggestions.append("I'd love to hear more about what you were feeling! Emotions are such an important part of understanding our experiences.")
            elif personality == 'conscientiousness':
                suggestions.append("To enhance our analysis, consider providing more detailed information about your emotional responses to this situation.")
            else:
                suggestions.append("Consider sharing more about the emotions you experienced in this situation.")
        
        if analysis['specificity_score'] < 40:
            if personality == 'extraversion':
                suggestions.append("Can you paint me a picture with more details? I'm really interested in the specifics of what happened!")
            elif personality == 'conscientiousness':
                suggestions.append("Providing more specific details will significantly improve our systematic analysis of this situation.")
            else:
                suggestions.append("Adding more specific details would help us better understand your experience.")
        
        if analysis['insight_level'] < 30:
            if personality == 'extraversion':
                suggestions.append("What insights are coming up for you? I'm excited to hear what connections you're making!")
            elif personality == 'conscientiousness':
                suggestions.append("Consider examining the patterns and connections between your thoughts, emotions, and behaviors in this situation.")
            else:
                suggestions.append("Try to explore what patterns or connections you notice in this experience.")
        
        return suggestions
    
    def export_response_analytics(self, responses: Dict[str, str], 
                                personality: str, condition: str) -> Dict[str, Any]:
        """Export comprehensive response analytics for research"""
        
        analytics = {
            'session_metadata': {
                'personality': personality,
                'condition': condition,
                'total_responses': len(responses),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'aggregate_metrics': {},
            'response_details': {},
            'therapeutic_analysis': {},
            'personality_insights': {}
        }
        
        total_quality = 0
        total_depth = 0
        total_insight = 0
        
        for response_id, response_text in responses.items():
            analysis = self.analyze_response_quality(response_text, 'General')
            analytics['response_details'][response_id] = analysis
            
            total_quality += analysis['overall_quality_score']
            total_depth += analysis['emotional_depth']
            total_insight += analysis['insight_level']
        
        response_count = len(responses)
        if response_count > 0:
            analytics['aggregate_metrics'] = {
                'avg_quality_score': total_quality / response_count,
                'avg_emotional_depth': total_depth / response_count,
                'avg_insight_level': total_insight / response_count,
                'total_word_count': sum(len(r.split()) for r in responses.values()),
                'avg_response_length': sum(len(r.split()) for r in responses.values()) / response_count
            }
        
        analytics['therapeutic_analysis'] = self._analyze_therapeutic_progress(responses)
        
        analytics['personality_insights'] = self._analyze_personality_influence(
            responses, personality, analytics['aggregate_metrics']
        )
        
        return analytics
    
    def _analyze_therapeutic_progress(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """Analyze therapeutic progress indicators across responses"""
        
        all_text = ' '.join(responses.values()).lower()
        
        progress_indicators = {
            'self_awareness_growth': len(re.findall(r'i (realize|understand|see|notice)', all_text)),
            'emotional_processing': len(re.findall(r'(feel|felt|emotion)', all_text)),
            'behavioral_insights': len(re.findall(r'(behavior|action|react|response)', all_text)),
            'future_planning': len(re.findall(r'(will|plan|going to|next time)', all_text)),
            'coping_strategies': len(re.findall(r'(cope|manage|handle|strategy)', all_text))
        }
        
        return progress_indicators
    
    def _analyze_personality_influence(self, responses: Dict[str, str], 
                                     personality: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how personality might have influenced responses"""
        
        personality_analysis = {
            'response_style_indicators': {},
            'engagement_patterns': {},
            'therapeutic_alignment': {}
        }
        
        if personality == 'extraversion':
            all_text = ' '.join(responses.values()).lower()
            social_words = ['people', 'friends', 'together', 'share', 'talk']
            enthusiasm_markers = ['excited', 'great', 'amazing', 'love', 'awesome']
            
            personality_analysis['response_style_indicators'] = {
                'social_references': sum(1 for word in social_words if word in all_text),
                'enthusiasm_markers': sum(1 for word in enthusiasm_markers if word in all_text),
                'avg_response_length': metrics.get('avg_response_length', 0)
            }
        
        elif personality == 'conscientiousness':
            all_text = ' '.join(responses.values()).lower()
            structure_words = ['plan', 'organize', 'systematic', 'goal', 'achieve']
            detail_indicators = ['specifically', 'detailed', 'thorough', 'comprehensive']
            
            personality_analysis['response_style_indicators'] = {
                'structure_references': sum(1 for word in structure_words if word in all_text),
                'detail_indicators': sum(1 for word in detail_indicators if word in all_text),
                'formal_language_score': metrics.get('avg_quality_score', 0)
            }
        
        else:
            personality_analysis['response_style_indicators'] = {
                'balanced_approach': True,
                'moderate_engagement': metrics.get('avg_quality_score', 0)
            }
        
        return personality_analysis