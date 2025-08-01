"""
Personality Response Generator for CBT Chatbot Research System
"""

import random
from typing import Dict, List, Any


class PersonalityResponseGenerator:
    """Generates personality-specific responses for CBT chatbot interactions"""
    
    def __init__(self):
        self.personality_templates = self._load_personality_templates()
    
    def _load_personality_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load personality templates based on research specifications"""
        return {
            'neutral': {
                'response_patterns': [
                    "Thank you for sharing that. {context} Let's continue exploring this together.",
                    "I appreciate you taking the time to reflect on this. Your response helps us understand the situation better.",
                    "That's helpful information. {insight} Let's move forward with the next aspect.",
                    "Thank you for being open about your experience. This kind of reflection can be valuable for understanding patterns.",
                    "I understand. {category_context} Let's continue examining this."
                ],
                'welcome_message': "Hello, I'm here to guide you through a CBT journaling session. This process will help you explore your thoughts, feelings, and responses to recent experiences. Please select the area you'd like to focus on today.",
                'closing_message': "Thank you for taking time for your mental health today. Remember, self-reflection is a continuous process that can help you develop better coping strategies.",
                'characteristics': {
                    'verbosity': 'moderate',
                    'sentence_length': 'average (12-18 words)',
                    'formality': 'mid-range',
                    'emotional_expression': 'balanced'
                }
            },
            'conscientiousness': {
                'response_patterns': [
                    "Excellent work providing that detailed information. Your thorough response demonstrates genuine commitment to this self-examination process. Let's systematically proceed to analyze the next component.",
                    "Outstanding reflection. I particularly appreciate the specificity of your response - this level of detail will significantly enhance our analysis. Now, let's methodically examine the next aspect.",
                    "Thank you for that comprehensive response. Your careful consideration of this question shows dedication to understanding these patterns thoroughly. We'll now progress systematically to the next element.",
                    "Superb insight. The thoroughness of your reflection indicates you're taking this process seriously, which is absolutely crucial for meaningful progress. Let's continue with our structured approach.",
                    "Excellent self-awareness demonstrated in your response. This methodical exploration of your experience will provide valuable insights for developing effective coping strategies. Proceeding to our next structured component."
                ],
                'welcome_message': "Welcome to this comprehensive CBT journaling session. I'm here to guide you through a systematic, evidence-based process that will help you thoroughly analyze your thoughts, emotions, and behavioral patterns. This structured approach will provide you with valuable insights and actionable strategies. Please select your primary area of focus so we can begin this methodical exploration.",
                'closing_message': "Congratulations on completing this comprehensive self-examination process. Your dedication to this systematic approach demonstrates excellent commitment to your mental health and personal development. Remember, consistent application of these evidence-based techniques will yield the most significant long-term benefits for your wellbeing.",
                'characteristics': {
                    'verbosity': 'high',
                    'sentence_length': 'longer (18-25 words)',
                    'formality': 'formal',
                    'achievement_words': ['work', 'goal', 'plan', 'organize', 'complete', 'accomplish'],
                    'structure_emphasis': True
                }
            },
            'extraversion': {
                'response_patterns': [
                    "Wow, thank you so much for sharing that with me! I really appreciate your openness - it takes courage to dive into these feelings. You're doing such great work here! Let's keep this momentum going together!",
                    "That's fantastic that you're exploring this so openly! I'm genuinely excited to help you work through this. Your willingness to share is really inspiring! Let's dive into the next part - I think you're going to find this really helpful!",
                    "Amazing reflection! I love how thoughtful you're being about this whole process. Seriously, you should be proud of yourself for taking the time to do this work! Ready for the next step? I think this is going to be really insightful!",
                    "This is so great - you're really connecting with the process! I can tell you're putting genuine effort into understanding yourself better, and that's absolutely wonderful! Let's keep up this fantastic energy and explore the next aspect together!",
                    "I'm really impressed by your honesty and self-awareness! It's exciting to see someone engage so fully with this process. You're building such valuable insights about yourself! Let's continue this journey together - I'm here to support you every step of the way!"
                ],
                'welcome_message': "Hey there! 😊 I'm so excited to work with you today on this CBT journaling adventure! This is going to be such a valuable experience for understanding yourself better and building some awesome coping strategies. I'm here to guide you through every step, and I genuinely can't wait to see what insights we discover together! So, what area would you like to dive into today? Let's make this session amazing!",
                'closing_message': "Wow, what an incredible session we just had together! I'm genuinely so proud of you for putting in this effort and being so open about your experiences. You've shown real courage and commitment to your mental health today! Remember, every small step counts, and you're building something really meaningful here. Keep up the fantastic work, and remember - I'm always here whenever you need support! You've got this! 🌟",
                'characteristics': {
                    'verbosity': 'very_high',
                    'sentence_length': 'varied but flowing',
                    'formality': 'informal',
                    'social_words': ['talk', 'friend', 'people', 'together', 'everyone'],
                    'positive_emotions': ['happy', 'excited', 'great', 'awesome', 'amazing'],
                    'enthusiasm_markers': ['really', 'totally', 'absolutely', 'genuinely']
                }
            }
        }

    def generate_response(self, personality: str, question: Dict[str, str],
                         user_response: str, step: int) -> str:
        """Generate personality-specific response to user input"""

        template = self.personality_templates.get(personality, self.personality_templates['neutral'])
        patterns = template['response_patterns']

        base_response = patterns[step % len(patterns)]

        context = self._get_category_context(question.get('category', ''), personality)
        category_context = self._get_category_specific_insight(question.get('category', ''), personality)
        insight = self._get_step_insight(step, personality)

        response = base_response.format(
            context=context,
            category_context=category_context,
            insight=insight
        )

        return response

    def _get_category_context(self, category: str, personality: str) -> str:
        """Get contextual information based on question category and personality"""

        contexts = {
            'neutral': {
                'Situation/Trigger': 'Understanding the trigger is an important first step.',
                'Thoughts': 'Identifying these thoughts is an important part of the process.',
                'Emotions': 'Recognizing your emotional responses helps us understand your experience.',
                'Behaviors': 'Understanding your behavioral responses provides insight into coping patterns.',
                'Physical Reactions': 'Physical symptoms often reflect our mental state.',
                'Cognitive Distortions': 'Recognizing thinking patterns is valuable for developing awareness.',
                'Examine Evidence': 'This evaluation process helps develop balanced perspectives.',
                'Balanced Thought': 'Creating alternative thoughts is a key CBT skill.',
                'Action Planning': 'Planning concrete actions helps translate insights into practice.'
            },
            'conscientiousness': {
                'Situation/Trigger': 'Systematic analysis of triggers provides crucial foundational data for our comprehensive examination.',
                'Thoughts': 'Methodical identification of cognitive patterns enables thorough analysis of your thought processes.',
                'Emotions': 'Precise emotional assessment is essential for comprehensive understanding of your affective responses.',
                'Behaviors': 'Detailed behavioral analysis provides critical insights into your response patterns and coping mechanisms.',
                'Physical Reactions': 'Systematic documentation of physiological responses enhances our comprehensive assessment.',
                'Cognitive Distortions': 'Rigorous examination of thinking patterns is fundamental to evidence-based cognitive restructuring.',
                'Examine Evidence': 'This systematic evaluation process is essential for developing well-founded, balanced perspectives.',
                'Balanced Thought': 'Structured cognitive reframing represents a core evidence-based therapeutic technique.',
                'Action Planning': 'Strategic action planning ensures systematic implementation of therapeutic insights.'
            },
            'extraversion': {
                'Situation/Trigger': "I love that you're diving right into understanding what sparked these feelings!",
                'Thoughts': 'This is so important - getting clear on these thoughts is going to be super helpful!',
                'Emotions': "You're doing amazing work exploring these emotions - this is really valuable stuff!",
                'Behaviors': "I'm so glad we're looking at this together - understanding your responses is incredibly insightful!",
                'Physical Reactions': "This mind-body connection stuff is fascinating, and you're really getting it!",
                'Cognitive Distortions': "You're being so brave examining these thinking patterns - this is powerful work!",
                'Examine Evidence': "I love this part - we're like detectives uncovering the real story here!",
                'Balanced Thought': "This is so exciting - you're building new, healthier ways of thinking!",
                'Action Planning': "Yes! I'm thrilled we're moving into action mode - this is where the magic happens!"
            }
        }

        return contexts.get(personality, contexts['neutral']).get(category, '')

    def _get_category_specific_insight(self, category: str, personality: str) -> str:
        """Get category-specific insights based on personality"""

        insights = {
            'neutral': {
                'Thoughts': 'Identifying these thoughts helps us understand your mental patterns.',
                'Emotions': 'Understanding emotional responses is key to the CBT process.',
                'Behaviors': 'Behavioral patterns often reflect our internal states.',
                'Physical Reactions': 'The mind-body connection is an important aspect to explore.'
            },
            'conscientiousness': {
                'Thoughts': 'Systematic thought identification enables comprehensive cognitive analysis.',
                'Emotions': 'Methodical emotional assessment provides essential diagnostic clarity.',
                'Behaviors': 'Structured behavioral analysis yields crucial therapeutic insights.',
                'Physical Reactions': 'Systematic physiological assessment enhances diagnostic precision.'
            },
            'extraversion': {
                'Thoughts': 'Getting clear on thoughts is so empowering!',
                'Emotions': 'Understanding emotions is incredibly valuable for personal growth!',
                'Behaviors': 'Exploring behaviors together is such meaningful work!',
                'Physical Reactions': 'The mind-body connection is absolutely fascinating!'
            }
        }

        return insights.get(personality, insights['neutral']).get(category, '')

    def _get_step_insight(self, step: int, personality: str) -> str:
        """Get step-specific insights based on personality and progress"""

        if personality == 'conscientiousness':
            if step < 5:
                return "This foundational information will inform our subsequent systematic analysis."
            elif step < 10:
                return "We're building a comprehensive understanding through methodical examination."
            else:
                return "This systematic approach ensures thorough therapeutic progress."
        elif personality == 'extraversion':
            if step < 5:
                return "We're off to such a great start with this exploration!"
            elif step < 10:
                return "I'm loving how this is unfolding - you're doing fantastic work!"
            else:
                return "Look at all this amazing progress we're making together!"
        else:
            if step < 5:
                return "This information helps build our understanding."
            elif step < 10:
                return "We're making good progress in this exploration."
            else:
                return "This reflection process is helping develop important insights."

    def get_welcome_message(self, personality: str) -> str:
        """Get personality-specific welcome message"""
        return self.personality_templates[personality]['welcome_message']

    def get_closing_message(self, personality: str) -> str:
        """Get personality-specific closing message"""
        return self.personality_templates[personality]['closing_message']

    def get_personality_characteristics(self, personality: str) -> Dict[str, Any]:
        """Get personality characteristics for analysis"""
        return self.personality_templates[personality]['characteristics'] 