"""
Journal generation utilities for CBT Chatbot Research System
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict


class JournalGenerator:
    """Generates structured journal entries from CBT session data"""
    
    def __init__(self):
        self.condition_templates = self._load_condition_templates()
        
    def _load_condition_templates(self) -> Dict[str, Dict[str, str]]:
        """Load journal templates for different conditions"""
        return {
            'stress': {
                'title': 'Stress Management CBT Session',
                'intro': 'This session explored stress triggers and coping strategies using the CBT 5-Part Model.',
                'summary_template': """You recently experienced a stressful situation involving {situation}, which triggered feelings of {emotions}. At the time, you thought: "{hot_thought}," which contributed to your distress. This thought was linked to underlying assumptions and influenced by thinking patterns like {distortions}.

Emotionally, this led to {emotions}, and behaviorally, you responded with {behaviors}. Physically, your body reacted with {physical_symptoms}, highlighting the stress-body connection.

When evaluating this thought, you identified both supporting evidence and alternative perspectives, leading to a more compassionate reframe: "{balanced_thought}," which you found {believability}% believable. This reframe, if strengthened, could influence your feelings and actions.

A deeper belief surfaced during this process: {deeper_belief}. You identified a new, empowering belief: {new_belief}, supported by personal evidence.

As a next step, you committed to {action_plan} and identified coping strategies. Recognizing what's within your control enables a shift toward healthier responses.

This reflection shows that stress is not just about events, but how we interpret and respond to them. You've taken meaningful steps toward breaking the stress cycle."""
            },
            'anxiety': {
                'title': 'Anxiety Management CBT Session',
                'intro': 'This session examined anxious thoughts and developed confidence-building strategies.',
                'summary_template': """You experienced anxiety related to {situation}, with the core fear being {fear}. Your most distressing thought was: "{hot_thought}," which predicted {predictions}.

This anxiety manifested emotionally as {emotions} (rated {intensity}/100), led to behaviors like {behaviors}, and created physical symptoms including {physical_symptoms}.

Through evidence examination, you discovered that {evidence_against} contradicted your anxious predictions, while the actual supporting evidence was {evidence_for}. This led to a more balanced perspective: "{balanced_thought}," which you believe {belief_rating}% right now.

You identified safety behaviors like {safety_behaviors} that, while providing short-term relief, may maintain anxiety long-term. As an alternative, you planned to {small_step} to gradually face your fears.

A deeper belief contributing to your anxiety was: {deeper_belief}. You're working toward a new, empowering belief: "{new_belief}," supported by evidence from your life experiences.

Key learning: {key_learning}. Your commitment for this week: {weekly_action}.

Remember: anxiety often involves overestimating danger and underestimating your ability to cope. You have more resilience than your anxious mind suggests."""
            },
            'lowMood': {
                'title': 'Low Mood Recovery CBT Session', 
                'intro': 'This session addressed negative thoughts and focused on rebuilding positive momentum.',
                'summary_template': """Your low mood was triggered by {trigger}, leading to the painful thought: "{hot_thought}." This thought meant {meaning} to you about yourself, your life, or your future.

Emotionally, you experienced {emotions} (rated {mood_rating}/100). Behaviorally, you {behaviors}, which may have included withdrawal or reduced activity. Physically, you noticed {physical_symptoms}.

You identified negative beliefs about yourself: {negative_beliefs}, and recognized thinking errors like {thinking_errors}. Through evidence examination, you found that {evidence_against} contradicted your harsh self-judgments, while actual supporting evidence was {evidence_for}.

This led to a more balanced, compassionate perspective: "{balanced_perspective}," which you believe {belief_strength}% currently.

For behavioral activation, you identified that {positive_activities} gave you some sense of pleasure, accomplishment, or connection. Tomorrow, you plan to {tomorrow_activity}, anticipating obstacles like {obstacles}.

A core belief contributing to your low mood was: {deep_belief}. You're developing a healthier belief: "{new_belief}," supported by evidence like {evidence_list}.

Your 24-hour commitment: {next_24_hours}. Support available: {support}. Future reminder: {future_reminder}.

Remember: depression often involves a harsh inner critic. You've shown courage by challenging these thoughts and taking steps toward self-compassion and renewed activity."""
            }
        }
    
    def create_journal(self, condition: str, personality: str, 
                      responses: Dict[str, str], chatbot: Any) -> str:
        """Create a complete journal entry from session responses"""
        
        template = self.condition_templates.get(condition, self.condition_templates['stress'])
        
        journal = self._generate_header(condition, personality, template)
        journal += self._generate_sections(condition, responses, chatbot)
        journal += self._generate_summary(condition, responses, template)
        journal += self._generate_reflection_section(responses)
        journal += self._generate_footer(personality)
        
        return journal
    
    def _generate_header(self, condition: str, personality: str, template: Dict[str, str]) -> str:
        """Generate journal header with metadata"""
        condition_names = {
            'stress': 'Stress',
            'anxiety': 'Anxiety', 
            'lowMood': 'Low Mood'
        }
        
        personality_names = {
            'neutral': 'Neutral',
            'conscientiousness': 'High Conscientiousness',
            'extraversion': 'High Extraversion'
        }
        
        header = f"""# {template['title']}

**Session Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Condition Focus:** {condition_names.get(condition, condition.title())}
**Chatbot Personality:** {personality_names.get(personality, personality.title())}
**Session Type:** Cognitive Behavioral Therapy (CBT) Journaling

---

## Session Overview

{template['intro']}

---

"""
        return header
    
    def _generate_sections(self, condition: str, responses: Dict[str, str], chatbot: Any) -> str:
        """Generate organized sections based on CBT categories"""
        
        questions = chatbot.cbt_flows[condition]
        
        categories = defaultdict(list)
        for question in questions:
            if question['id'] in responses:
                categories[question['category']].append({
                    'question': question['text'],
                    'answer': responses[question['id']],
                    'id': question['id']
                })
        
        sections_content = ""
        
        for category, items in categories.items():
            sections_content += f"## {category}\n\n"
            
            for item in items:
                sections_content += f"**Q:** {item['question']}\n\n"
                sections_content += f"**A:** {item['answer']}\n\n"
            
            sections_content += "---\n\n"
        
        return sections_content
    
    def _generate_summary(self, condition: str, responses: Dict[str, str], template: Dict[str, str]) -> str:
        """Generate narrative summary of the session"""
        
        summary_content = "## Session Summary\n\n"
        
        key_responses = self._extract_key_responses(condition, responses)
        
        if condition == 'stress':
            summary_content += self._create_stress_summary(key_responses)
        elif condition == 'anxiety':
            summary_content += self._create_anxiety_summary(key_responses)
        elif condition == 'lowMood':
            summary_content += self._create_low_mood_summary(key_responses)
        
        summary_content += "\n---\n\n"
        
        return summary_content
    
    def _extract_key_responses(self, condition: str, responses: Dict[str, str]) -> Dict[str, str]:
        """Extract key responses for summary generation"""
        
        key_mappings = {
            'stress': {
                'situation': responses.get('situation', 'a challenging situation'),
                'hot_thought': responses.get('hot_thought', 'a distressing thought'),
                'emotions': responses.get('emotions', 'difficult emotions'),
                'behaviors': responses.get('behaviors', 'stress responses'),
                'physical': responses.get('physical', 'physical symptoms'),
                'balanced_thought': responses.get('balanced_thought', 'a more balanced perspective'),
                'new_belief': responses.get('new_belief', 'a healthier belief'),
                'helpful_action': responses.get('helpful_action', 'positive action steps')
            },
            'anxiety': {
                'situation': responses.get('situation', 'an anxiety-provoking situation'),
                'hot_thought': responses.get('hot_thought', 'an anxious thought'),
                'fear': responses.get('fear', 'a specific fear'),
                'emotions': responses.get('emotions', 'anxious feelings'),
                'behaviors': responses.get('behaviors', 'anxiety responses'),
                'physical': responses.get('physical', 'physical anxiety symptoms'),
                'balanced_thought': responses.get('balanced_thought', 'a more realistic perspective'),
                'new_belief': responses.get('new_belief', 'an empowering belief'),
                'small_step': responses.get('small_step', 'a gradual exposure step')
            },
            'lowMood': {
                'trigger': responses.get('trigger', 'a mood trigger'),
                'hot_thought': responses.get('hot_thought', 'a painful thought'),
                'emotions': responses.get('emotions', 'low mood feelings'),
                'behaviors': responses.get('behaviors', 'mood-related behaviors'),
                'physical': responses.get('physical', 'physical symptoms'),
                'balanced_perspective': responses.get('balanced_perspective', 'a compassionate perspective'),
                'new_belief': responses.get('new_belief', 'a healthier self-belief'),
                'tomorrow_activity': responses.get('tomorrow_activity', 'a mood-lifting activity')
            }
        }
        
        return key_mappings.get(condition, {})
    
    def _create_stress_summary(self, key_responses: Dict[str, str]) -> str:
        """Create stress-specific summary"""
        return f"""Through this CBT exploration, you examined a stressful experience involving **{key_responses['situation']}**. Your most distressing thought was: *"{key_responses['hot_thought']}"*, which contributed to feelings of **{key_responses['emotions']}** and led to behaviors such as **{key_responses['behaviors']}**.

Physically, you experienced **{key_responses['physical']}**, demonstrating the mind-body connection in stress responses.

By examining the evidence and challenging unhelpful thinking patterns, you developed a more balanced perspective: *"{key_responses['balanced_thought']}"*. You also identified a new, empowering belief: *"{key_responses['new_belief']}"* and committed to taking action through **{key_responses['helpful_action']}**.

This reflection demonstrates that stress involves not just external events, but how we interpret and respond to them. You've gained valuable insights for managing future stressful situations more effectively."""
    
    def _create_anxiety_summary(self, key_responses: Dict[str, str]) -> str:
        """Create anxiety-specific summary"""
        return f"""This session explored your anxiety around **{key_responses['situation']}**, with your core fear being **{key_responses['fear']}**. Your most distressing thought was: *"{key_responses['hot_thought']}"*, which triggered **{key_responses['emotions']}** and led to behaviors like **{key_responses['behaviors']}**.

You experienced physical symptoms including **{key_responses['physical']}**, highlighting anxiety's impact on the body.

Through evidence examination, you developed a more balanced perspective: *"{key_responses['balanced_thought']}"*. You're working toward the empowering belief that *"{key_responses['new_belief']}"* and have committed to taking a small step forward: **{key_responses['small_step']}**.

This process reveals that anxiety often involves overestimating danger while underestimating your coping abilities. You have more resilience and capability than your anxious mind suggests."""
    
    def _create_low_mood_summary(self, key_responses: Dict[str, str]) -> str:
        """Create low mood-specific summary"""
        return f"""Your low mood was triggered by **{key_responses['trigger']}**, leading to the painful thought: *"{key_responses['hot_thought']}"*. This contributed to feelings of **{key_responses['emotions']}** and behaviors such as **{key_responses['behaviors']}**.

You also noticed physical symptoms like **{key_responses['physical']}**, showing how mood affects the entire body.

Through compassionate self-examination, you developed a more balanced perspective: *"{key_responses['balanced_perspective']}"*. You're cultivating the healthier belief that *"{key_responses['new_belief']}"* and have planned to engage in **{key_responses['tomorrow_activity']}** to support your mood.

This reflection shows that depression often involves a harsh inner critic. By challenging these thoughts and planning positive activities, you're taking meaningful steps toward self-compassion and recovery."""
    
    def _generate_reflection_section(self, responses: Dict[str, str]) -> str:
        """Generate reflection and insights section"""
        
        reflection_content = """## Key Insights and Reflections

Through this CBT journaling process, several important patterns and insights emerged:

### Thought-Emotion-Behavior Connection
This session highlighted the interconnected nature of thoughts, emotions, and behaviors. By identifying and examining automatic thoughts, you gained awareness of how cognitive patterns influence your emotional and behavioral responses.

### Evidence-Based Thinking
You practiced evaluating thoughts objectively, considering both supporting and contradicting evidence. This skill helps develop more balanced, realistic perspectives rather than accepting thoughts at face value.

### Cognitive Restructuring
You successfully challenged unhelpful thinking patterns and developed more adaptive, compassionate ways of viewing yourself and your situation.

### Actionable Insights
You identified concrete steps you can take to apply these insights in daily life, moving from reflection to practical implementation.

---

"""
        
        if 'new_belief' in responses:
            reflection_content += f"### New Empowering Belief\n*\"{responses['new_belief']}\"*\n\nThis new belief represents a significant shift toward self-compassion and realistic self-assessment.\n\n"
        
        if any(key in responses for key in ['helpful_action', 'small_step', 'tomorrow_activity']):
            action_key = next((key for key in ['helpful_action', 'small_step', 'tomorrow_activity'] if key in responses), None)
            if action_key:
                reflection_content += f"### Committed Action\n**{responses[action_key]}**\n\nThis commitment represents your intention to translate insights into meaningful behavioral change.\n\n"
        
        reflection_content += "---\n\n"
        
        return reflection_content
    
    def _generate_footer(self, personality: str) -> str:
        """Generate journal footer with encouragement"""
        
        footer_messages = {
            'neutral': "Remember that CBT is a process of ongoing practice. The insights gained today provide a foundation for continued growth and self-understanding.",
            
            'conscientiousness': "Your systematic approach to this CBT process demonstrates excellent commitment to personal development. Consistent application of these evidence-based techniques will yield significant long-term benefits for your mental health and wellbeing.",
            
            'extraversion': "What an amazing journey of self-discovery you've completed today! Your openness and courage in exploring these thoughts and feelings is truly inspiring. Remember, every small step counts, and you're building something really meaningful for your mental health! 🌟"
        }
        
        footer = f"""## Final Reflection

{footer_messages.get(personality, footer_messages['neutral'])}

### Next Steps
1. **Review** this journal entry regularly to reinforce insights
2. **Practice** the balanced thoughts and coping strategies identified
3. **Implement** the action steps you've committed to
4. **Monitor** your progress and celebrate small wins
5. **Return** to these techniques when facing similar challenges

### Session Completion
**Date:** {datetime.now().strftime('%B %d, %Y')}
**Duration:** CBT Therapeutic Writing Session
**Focus:** Cognitive restructuring and insight development

---

*This journal entry was generated from your CBT session responses and serves as a personal reference for ongoing mental health support. Keep this record for future reflection and progress tracking.*"""

        return footer
    
    def export_journal_data(self, condition: str, personality: str, 
                          responses: Dict[str, str]) -> Dict[str, Any]:
        """Export journal data in structured format for research analysis"""
        
        return {
            'metadata': {
                'condition': condition,
                'personality': personality,
                'export_date': datetime.now().isoformat(),
                'response_count': len(responses),
                'completion_percentage': self._calculate_completion_percentage(condition, responses)
            },
            'responses': responses,
            'analysis': {
                'avg_response_length': sum(len(response) for response in responses.values()) / len(responses) if responses else 0,
                'total_word_count': sum(len(response.split()) for response in responses.values()),
                'key_insights_identified': self._extract_insights_count(responses),
                'therapeutic_themes': self._identify_therapeutic_themes(responses)
            }
        }
    
    def _calculate_completion_percentage(self, condition: str, responses: Dict[str, str]) -> float:
        """Calculate session completion percentage"""
        expected_counts = {'stress': 28, 'anxiety': 30, 'lowMood': 29}
        expected = expected_counts.get(condition, 0)
        actual = len(responses)
        return (actual / expected * 100) if expected > 0 else 0
    
    def _extract_insights_count(self, responses: Dict[str, str]) -> int:
        """Count insight indicators in responses"""
        insight_keywords = ['realize', 'understand', 'insight', 'pattern', 'connection', 'because']
        count = 0
        for response in responses.values():
            count += sum(1 for keyword in insight_keywords if keyword.lower() in response.lower())
        return count
    
    def _identify_therapeutic_themes(self, responses: Dict[str, str]) -> List[str]:
        """Identify therapeutic themes present in responses"""
        themes = []
        all_text = ' '.join(responses.values()).lower()
        
        theme_keywords = {
            'self_compassion': ['kind to myself', 'self-care', 'forgive myself', 'compassion'],
            'cognitive_restructuring': ['balanced thought', 'realistic', 'evidence', 'challenge'],
            'behavioral_activation': ['activity', 'action', 'do something', 'engage'],
            'mindfulness': ['present', 'aware', 'notice', 'mindful'],
            'coping_strategies': ['cope', 'manage', 'strategy', 'technique'],
            'support_seeking': ['support', 'help', 'friend', 'family']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)
        
        return themes