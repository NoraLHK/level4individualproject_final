import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import openai
from config.personalities import PersonalityResponseGenerator
from textblob import TextBlob
import random

st.set_page_config(
    page_title="CBT Chatbot Research System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_personality_css(personality: str):
    """Injects personality-specific CSS into the Streamlit app."""
    colors = {
        'neutral': {'border': '#6b7280', 'bg': '#f9fafb', 'header': '#333333', 'progress': '#6b7280'},
        'conscientiousness': {'border': '#1d4ed8', 'bg': '#eef6ff', 'header': '#1d4ed8', 'progress': '#1d4ed8'},
        'extraversion': {'border': '#ea580c', 'bg': '#fff7ed', 'header': '#ea580c', 'progress': '#ea580c'}
    }
    
    selected_colors = colors.get(personality, colors['neutral'])
    
    css = f"""
    <style>
        /* Assistant Message Bubble */
        div[data-testid="chat-message-container"] div[data-testid="stChatMessageContent-assistant"] {{
            background-color: {selected_colors['bg']} !important;
            border-left: 5px solid {selected_colors['border']} !important;
            border-radius: 0.5rem !important;
        }}
        
        /* User Message Bubble */
        div[data-testid="chat-message-container"] div[data-testid="stChatMessageContent-user"] {{
             background-color: #F0F2F6 !important;
        }}
        
        div[data-testid="chat-message-container"] div[data-testid="stChatMessageContent-user"] .stMarkdown p {{
             color: #111827 !important;
        }}

        h1 {{
            color: #1e3a8a !important;
        }}
        
        h2 {{
            color: {selected_colors['header']} !important;
        }}

        .stProgress > div > div > div > div {{
            background-color: {selected_colors['progress']} !important;
        }}
        
        .stAlert {{
            border-left-color: {selected_colors['border']} !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# CBT Flow Data (embedded to avoid import issues)
CBT_FLOWS = {
    "stress": [
        {"id": "situation", "text": "What happened recently that triggered your stress?", "category": "Situation/Trigger"},
        {"id": "specific_event", "text": "Was there a specific event, deadline, interaction, or change?", "category": "Situation/Trigger"},
        {"id": "personal_stress", "text": "What made this situation feel stressful to you personally?", "category": "Situation/Trigger"},
        {"id": "similar_before", "text": "Have you faced a similar situation before? What happened then?", "category": "Situation/Trigger"},
        {"id": "thoughts_moment", "text": "What went through your mind at the moment you started feeling stressed?", "category": "Thoughts"},
        {"id": "hot_thought", "text": "What was the most distressing or believable thought? (Your \"hot thought\")", "category": "Thoughts"},
        {"id": "emotions", "text": "What emotions did you feel? (e.g., anxious, overwhelmed, frustrated, helpless)", "category": "Mood"},
        {"id": "mood_rating", "text": "Rate each mood from 0–100%.", "category": "Mood"},
        {"id": "behaviors", "text": "What did you do (or avoid doing) as a result of feeling stressed?", "category": "Behaviors"},
        {"id": "avoidance", "text": "Did you procrastinate, shut down, lash out, overwork, or escape?", "category": "Behaviors"},
        {"id": "physical", "text": "What physical symptoms did you notice? (e.g., muscle tension, headache, fatigue, nausea, racing heart)", "category": "Physical Reactions"},
        {"id": "assumptions", "text": "What assumptions were you making about yourself, others, or the situation?", "category": "Automatic Thoughts"},
        {"id": "distortions", "text": "Are you using any of these common thinking traps? (Catastrophizing, All-or-Nothing, Mind Reading, Overgeneralization, Shoulds/Musts)", "category": "Cognitive Distortions"},
        {"id": "evidence_for", "text": "What is the factual evidence that supports this thought?", "category": "Examine Evidence"},
        {"id": "evidence_against", "text": "What is the evidence that challenges or contradicts this thought?", "category": "Examine Evidence"},
        {"id": "friend_advice", "text": "What would you say to a friend if they were thinking the same thing in this situation?", "category": "Examine Evidence"},
        {"id": "balanced_thought", "text": "Based on the evidence, what's a more realistic or helpful way of viewing this situation?", "category": "Balanced Thought"},
        {"id": "believability", "text": "How believable is this new thought to you right now? (0–100%)", "category": "Balanced Thought"},
        {"id": "emotional_change", "text": "What would change for you emotionally or behaviorally if you believed this new thought more often?", "category": "Balanced Thought"},
        {"id": "small_action", "text": "What is one small action you could take that reflects this new thought?", "category": "Balanced Thought"},
        {"id": "deeper_belief", "text": "Is there a deeper belief making this harder to cope with? (e.g., \"If I don't achieve, I'm worthless\")", "category": "Deeper Beliefs"},
        {"id": "belief_origin", "text": "Where do you think this belief came from—family, school, culture, or past experiences?", "category": "Deeper Beliefs"},
        {"id": "belief_influence", "text": "How has this belief influenced your life over time?", "category": "Deeper Beliefs"},
        {"id": "belief_meaning_self", "text": "If this belief were true, what would it mean about you?", "category": "Deeper Beliefs"},
        {"id": "belief_meaning_others", "text": "What would it mean about others?", "category": "Deeper Beliefs"},
        {"id": "belief_meaning_world", "text": "What would it mean about the world or your future?", "category": "Deeper Beliefs"},
        {"id": "helpful_action", "text": "What's one small, specific action you can take this week to reduce your stress?", "category": "Action Planning"},
        {"id": "action_steps", "text": "List a few manageable steps to help you follow through.", "category": "Action Planning"},
        {"id": "control_parts", "text": "What parts of this situation are within your control, and what parts are outside of your control?", "category": "Action Planning"},
        {"id": "past_strategies", "text": "What strengths or past strategies have helped you manage similar stress before?", "category": "Action Planning"},
        {"id": "stress_meaning", "text": "Is your stress telling you something meaningful—like a personal value or unmet need?", "category": "Action Planning"},
        {"id": "belief_review", "text": "Review the negative belief you uncovered. Is this a belief you've noticed coming up often in your life?", "category": "Healthier Beliefs"},
        {"id": "belief_outcome", "text": "When you challenged this belief, did the outcome match your prediction? Did anything positive or unexpected happen?", "category": "Healthier Beliefs"},
        {"id": "new_belief", "text": "What new belief would you like to adopt about yourself, others, or life?", "category": "Healthier Beliefs"},
        {"id": "belief_evidence", "text": "Write down 10 small pieces of evidence that support this new belief.", "category": "Healthier Beliefs"}
    ],
    "anxiety": [
        {"id": "situation", "text": "What recent situation or event made you feel anxious?", "category": "Situation/Trigger"},
        {"id": "anticipation", "text": "Was there something you were anticipating, avoiding, or fearing?", "category": "Situation/Trigger"},
        {"id": "thoughts", "text": "What thoughts were running through your mind at that time?", "category": "Thoughts"},
        {"id": "hot_thought", "text": "What was the most distressing or believable thought? (\"hot thought\")", "category": "Thoughts"},
        {"id": "fear", "text": "What were you afraid might happen?", "category": "Thoughts"},
        {"id": "emotions", "text": "What emotions did you feel? (e.g., nervous, scared, panicky, uneasy)", "category": "Emotions"},
        {"id": "emotion_intensity", "text": "Rate the intensity of each emotion from 0–100%.", "category": "Emotions"},
        {"id": "behaviors", "text": "What did you do—or avoid doing—because of the anxiety?", "category": "Behaviors"},
        {"id": "safety_behaviors", "text": "Did you engage in safety behaviors (e.g., checking, avoiding, escaping, seeking reassurance)?", "category": "Behaviors"},
        {"id": "physical", "text": "What physical symptoms did you notice? (e.g., tight chest, rapid heartbeat, sweating, dizziness, nausea)", "category": "Physical Reactions"},
        {"id": "predictions", "text": "What did you think would go wrong? What's the worst-case scenario your mind predicted?", "category": "Anxious Predictions"},
        {"id": "thinking_traps", "text": "Are you experiencing thinking patterns like catastrophizing, fortune telling, mind reading, overgeneralizing, intolerance of uncertainty, or shoulds/musts?", "category": "Thinking Traps"},
        {"id": "coping_strategies", "text": "What do you usually do to cope with anxiety (e.g., avoid, seek reassurance, prepare excessively)?", "category": "Safety Behaviors"},
        {"id": "strategy_effectiveness", "text": "Do these strategies reduce anxiety in the long run—or maintain it?", "category": "Safety Behaviors"},
        {"id": "evidence_for", "text": "What is the actual evidence that supports your anxious thought or prediction?", "category": "Examine Evidence"},
        {"id": "evidence_against", "text": "What is the evidence that contradicts it or offers another explanation?", "category": "Examine Evidence"},
        {"id": "friend_perspective", "text": "If a friend had this thought, what would you say to help them gain perspective?", "category": "Examine Evidence"},
        {"id": "balanced_thought", "text": "What's a more balanced way to think about this situation?", "category": "Balanced Thought"},
        {"id": "belief_rating", "text": "On a scale of 0–100%, how much do you believe this new thought?", "category": "Balanced Thought"},
        {"id": "avoidance", "text": "Is there something you've been avoiding due to fear?", "category": "Facing Fears"},
        {"id": "small_step", "text": "What is one small step you could take to face this fear gradually?", "category": "Facing Fears"},
        {"id": "coping_strategy", "text": "What calming strategy might help you in similar situations? (e.g., breathing, grounding, mindfulness)", "category": "Coping Strategy"},
        {"id": "different_response", "text": "What could you do differently next time to feel more in control?", "category": "Coping Strategy"},
        {"id": "deeper_belief", "text": "Is there a deeper belief behind your anxiety? (e.g., \"If I'm not in control, something bad will happen\")", "category": "Underlying Beliefs"},
        {"id": "belief_origin", "text": "Where might this belief come from—past experiences, upbringing, messages from others?", "category": "Underlying Beliefs"},
        {"id": "belief_impact", "text": "How has this belief shaped your reactions and decisions over time?", "category": "Underlying Beliefs"},
        {"id": "new_belief", "text": "What is a new, empowering belief you'd like to hold? (e.g., \"Uncertainty is uncomfortable but tolerable\")", "category": "New Beliefs"},
        {"id": "supporting_evidence", "text": "List 10 small experiences or facts from your life that support this new belief.", "category": "New Beliefs"},
        {"id": "life_change", "text": "What would change in your life if you believed this more often?", "category": "New Beliefs"},
        {"id": "key_learning", "text": "What's one thing you learned from this reflection that you want to remember?", "category": "Progress"},
        {"id": "weekly_action", "text": "What can you do this week to reinforce your progress?", "category": "Progress"}
    ],
    "lowMood": [
        {"id": "trigger", "text": "What situation, interaction, or thought triggered your low mood recently?", "category": "Situation/Trigger"},
        {"id": "familiarity", "text": "Was this a familiar or recurring type of situation for you?", "category": "Situation/Trigger"},
        {"id": "thoughts", "text": "What was going through your mind at that moment?", "category": "Thoughts"},
        {"id": "hot_thought", "text": "What was the most painful or convincing thought? (\"hot thought\")", "category": "Thoughts"},
        {"id": "meaning", "text": "What did that thought mean about you, your life, or your future?", "category": "Thoughts"},
        {"id": "emotions", "text": "What emotions did you feel? (e.g., sad, hopeless, empty, guilty, numb)", "category": "Moods"},
        {"id": "mood_rating", "text": "Rate each mood from 0–100%.", "category": "Moods"},
        {"id": "behaviors", "text": "What did you do—or avoid doing—because you felt this way?", "category": "Behaviors"},
        {"id": "withdrawal", "text": "Did you withdraw, isolate, stop doing enjoyable or necessary activities?", "category": "Behaviors"},
        {"id": "physical", "text": "What physical symptoms did you notice? (e.g., fatigue, heaviness, sleep or appetite changes, slowed movement)", "category": "Physical Reactions"},
        {"id": "negative_beliefs", "text": "What were you telling yourself about your worth, future, or abilities? (e.g., \"I'm a failure,\" \"Nothing will change\")", "category": "Core Negative Beliefs"},
        {"id": "thinking_errors", "text": "Were you making thinking errors like all-or-nothing thinking, mental filter, overgeneralization, labeling, or hopelessness?", "category": "Thinking Errors"},
        {"id": "evidence_for", "text": "What is the factual evidence that supports this thought?", "category": "Examine Evidence"},
        {"id": "evidence_against", "text": "What evidence contradicts it or offers a different view?", "category": "Examine Evidence"},        
        {"id": "friend_advice", "text": "If a friend said this about themselves, what would you say to them?", "category": "Examine Evidence"},
        {"id": "balanced_perspective", "text": "Based on the evidence, what's a more balanced or constructive way to view the situation or yourself?", "category": "Balanced Perspective"},
        {"id": "belief_strength", "text": "How much do you believe this new thought (0–100%)?", "category": "Balanced Perspective"},
        {"id": "recent_activities", "text": "What activities (if any) did you do today or recently?", "category": "Activity Review"},
        {"id": "positive_activities", "text": "Which activities gave you even a small sense of pleasure, accomplishment, or connection?", "category": "Activity Review"},
        {"id": "tomorrow_activity", "text": "What is one small, meaningful activity you could do tomorrow that may improve your mood?", "category": "Behavioral Activation"},
        {"id": "obstacles", "text": "What obstacles might make it hard to follow through—and how could you handle them?", "category": "Behavioral Activation"},
        {"id": "deep_belief", "text": "What belief do you hold about yourself that may be contributing to your mood? (e.g., \"I'm not good enough\")", "category": "Deep-Seated Beliefs"},
        {"id": "belief_source", "text": "Where do you think that belief came from—family, experiences, rejection, failure?", "category": "Deep-Seated Beliefs"},
        {"id": "belief_impact", "text": "How has this belief impacted your life and relationships over time?", "category": "Deep-Seated Beliefs"},
        {"id": "new_belief", "text": "What new belief would you like to hold about yourself? (e.g., \"I have value regardless of what I achieve\")", "category": "Healthier Beliefs"},
        {"id": "evidence_list", "text": "List 10 small pieces of evidence or moments that support this new belief.", "category": "Healthier Beliefs"},
        {"id": "life_difference", "text": "What would be different in your life if you believed this more deeply?", "category": "Healthier Beliefs"},
        {"id": "next_24_hours", "text": "What's one thing you can do in the next 24 hours to support your mental health or lift your mood?", "category": "Small Wins"},
        {"id": "support", "text": "Who or what could support you in doing this?", "category": "Small Wins"},
        {"id": "future_reminder", "text": "What reminder would you like to give yourself next time your mood feels low?", "category": "Future Resilience"}
    ]
}

# Personality Response Templates
PERSONALITY_RESPONSES = {
    'neutral': {
        'responses': [
            "Thank you for sharing that. {context} Let's continue exploring this together.",
            "I appreciate you taking the time to reflect on this. Your response helps us understand the situation better.",
            "That's helpful information. Let's move forward with the next aspect.",
            "Thank you for being open about your experience. This kind of reflection can be valuable for understanding patterns.",
            "I understand. Let's continue examining this."
        ],
        'welcome': "Hello, I'm here to guide you through a CBT journaling session. This process will help you explore your thoughts, feelings, and responses to recent experiences. Please select the area you'd like to focus on today.",
        'closing': "Thank you for taking time for your mental health today. Remember, self-reflection is a continuous process that can help you develop better coping strategies."
    },
    'conscientiousness': {
        'responses': [
            "Excellent work providing that detailed information. Your thorough response demonstrates genuine commitment to this self-examination process. Let's systematically proceed to analyze the next component.",
            "Outstanding reflection. I particularly appreciate the specificity of your response - this level of detail will significantly enhance our analysis. Now, let's methodically examine the next aspect.",
            "Thank you for that comprehensive response. Your careful consideration of this question shows dedication to understanding these patterns thoroughly. We'll now progress systematically to the next element.",
            "Superb insight. The thoroughness of your reflection indicates you're taking this process seriously, which is absolutely crucial for meaningful progress. Let's continue with our structured approach.",
            "Excellent self-awareness demonstrated in your response. This methodical exploration of your experience will provide valuable insights for developing effective coping strategies."
        ],
        'welcome': "Welcome to this comprehensive CBT journaling session. I'm here to guide you through a systematic, evidence-based process that will help you thoroughly analyze your thoughts, emotions, and behavioral patterns. This structured approach will provide you with valuable insights and actionable strategies. Please select your primary area of focus so we can begin this methodical exploration.",
        'closing': "Congratulations on completing this comprehensive self-examination process. Your dedication to this systematic approach demonstrates excellent commitment to your mental health and personal development. Remember, consistent application of these evidence-based techniques will yield the most significant long-term benefits for your wellbeing."
    },
    'extraversion': {
        'responses': [
            "Wow, thank you so much for sharing that with me! I really appreciate your openness - it takes courage to dive into these feelings. You're doing such great work here! Let's keep this momentum going together!",
            "That's fantastic that you're exploring this so openly! I'm genuinely excited to help you work through this. Your willingness to share is really inspiring! Let's dive into the next part - I think you're going to find this really helpful!",
            "Amazing reflection! I love how thoughtful you're being about this whole process. Seriously, you should be proud of yourself for taking the time to do this work! Ready for the next step? I think this is going to be really insightful!",
            "This is so great - you're really connecting with the process! I can tell you're putting genuine effort into understanding yourself better, and that's absolutely wonderful! Let's keep up this fantastic energy and explore the next aspect together!",
            "I'm really impressed by your honesty and self-awareness! It's exciting to see someone engage so fully with this process. You're building such valuable insights about yourself! Let's continue this journey together!"
        ],
        'welcome': "Hey there! 😊 I'm so excited to work with you today on this CBT journaling adventure! This is going to be such a valuable experience for understanding yourself better and building some awesome coping strategies. I'm here to guide you through every step, and I genuinely can't wait to see what insights we discover together! So, what area would you like to dive into today? Let's make this session amazing!",
        'closing': "Wow, what an incredible session we just had together! I'm genuinely so proud of you for putting in this effort and being so open about your experiences. You've shown real courage and commitment to your mental health today! Remember, every small step counts, and you're building something really meaningful here. Keep up the fantastic work! 🌟"
    }
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "cbt_templates.txt")
BIG5_TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "big5_personality_templates.txt")

class CBTChatbotApp:
    def __init__(self):
        self.generator = PersonalityResponseGenerator()
        self.init_session_state()
        self.condition_templates = self.load_condition_templates()
        self.big5_templates = self.load_big5_templates()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'current_personality' not in st.session_state:
            st.session_state.current_personality = 'neutral'
        if 'current_condition' not in st.session_state:
            st.session_state.current_condition = None
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
        if 'responses' not in st.session_state:
            st.session_state.responses = {}
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'session_complete' not in st.session_state:
            st.session_state.session_complete = False
        if 'journal_generated' not in st.session_state:
            st.session_state.journal_generated = False
        if 'openai_key' not in st.session_state:
            st.session_state.openai_key = os.getenv("OPENAI_API_KEY", "")
            if st.session_state.openai_key:
                openai.api_key = st.session_state.openai_key

    def reset_session(self):
        """Reset all session variables"""
        st.session_state.current_condition = None
        st.session_state.current_step = 0
        st.session_state.responses = {}
        st.session_state.chat_history = []
        st.session_state.session_complete = False
        st.session_state.journal_generated = False
        st.rerun()

    def render_header(self):
        st.title("🧠 CBT Chatbot Personality Research System")
        st.markdown(
            "**Research Question:** *To what extent does mental health chatbot personalities "
            "(neutral extraversion and conscientiousness) influence overall effectiveness "
            "of Cognitive Behavioral Therapeutic writing?*"
        )
        st.divider()

    def render_personality_selector(self):
        st.sidebar.header("🎭 Chatbot Personality")
        
        personality_options = {
            'neutral': 'Neutral',
            'conscientiousness': 'High Conscientiousness', 
            'extraversion': 'High Extraversion'
        }
        
        selected = st.sidebar.selectbox(
            "Select Personality Type:",
            options=list(personality_options.keys()),
            format_func=lambda x: personality_options[x],
            index=list(personality_options.keys()).index(st.session_state.current_personality)
        )
        
        if selected != st.session_state.current_personality:
            st.session_state.current_personality = selected
            self.reset_session()
            
        descriptions = {
            'neutral': "Balanced communication style with moderate verbosity and consistent tone.",
            'conscientiousness': "Organized, detailed responses with achievement-oriented language and structured approach.",
            'extraversion': "Enthusiastic, energetic communication with high verbosity and positive emotional expressions."
        }
        
        st.sidebar.info(f"**Current Style:** {descriptions[selected]}")
        
        if st.sidebar.button("🔄 Reset Session", use_container_width=True):
            self.reset_session()

    def render_api_key_input(self):
        with st.sidebar.expander("🔑 OpenAI API Key", expanded=False):
            key_input = st.text_input(
                "Enter your OpenAI API Key (kept in this session only):",
                value=st.session_state.get("openai_key", ""),
                type="password",
                placeholder="sk-...",
            )
            if key_input != st.session_state.get("openai_key", ""):
                st.session_state.openai_key = key_input.strip()
                openai.api_key = st.session_state.openai_key
                if openai.api_key:
                    st.success("API key saved for this session.")
                else:
                    st.info("API key cleared; using local analysis only.")

    def render_condition_selector(self):
        if st.session_state.current_condition is None:
            st.header("📋 Select Your Focus Area")
            st.markdown("Choose the area you'd like to explore in today's CBT session:")
            
            col1, col2, col3 = st.columns(3)
            
            conditions = [
                {
                    'key': 'stress',
                    'title': '😰 Stress',
                    'description': 'Explore stress triggers and develop coping strategies using the CBT 5-Part Model'
                },
                {
                    'key': 'anxiety', 
                    'title': '😟 Anxiety',
                    'description': 'Examine anxious thoughts and build confidence through exposure strategies'
                },
                {
                    'key': 'lowMood',
                    'title': '😔 Low Mood', 
                    'description': 'Address negative thoughts and rebuild positive momentum with behavioral activation'
                }
            ]
            
            for i, condition in enumerate(conditions):
                with [col1, col2, col3][i]:
                    if st.button(
                        f"{condition['title']}\n\n{condition['description']}", 
                        key=f"condition_{condition['key']}",
                        use_container_width=True
                    ):
                        self.start_condition(condition['key'])

    def start_condition(self, condition: str):
        st.session_state.current_condition = condition
        st.session_state.current_step = 0
        st.session_state.chat_history = []
        st.session_state.responses = {}
        st.session_state.session_complete = False
        st.session_state.journal_generated = False
        
        welcome_msg = PERSONALITY_RESPONSES[st.session_state.current_personality]['welcome']
        
        condition_intros = {
            'stress': "Great choice! Let's explore your stress using the CBT 5-Part Model.",
            'anxiety': "Perfect! We'll examine your anxiety using CBT's comprehensive framework.", 
            'lowMood': "Excellent! Let's understand your low mood through the CBT 5-Part Model."
        }
        
        first_question = CBT_FLOWS[condition][0]
        
        st.session_state.chat_history.extend([
            {'type': 'bot', 'message': welcome_msg, 'personality': st.session_state.current_personality},
            {'type': 'bot', 'message': condition_intros[condition], 'personality': st.session_state.current_personality},
            {'type': 'bot', 'message': self._style_question_with_personality(st.session_state.current_personality, first_question['text']), 'personality': st.session_state.current_personality}
        ])
        
        st.rerun()

    def render_chat_interface(self):
        if st.session_state.current_condition is None:
            return
            
        condition_names = {'stress': 'Stress', 'anxiety': 'Anxiety', 'lowMood': 'Low Mood'}
        personality_names = {
            'neutral': 'Neutral',
            'conscientiousness': 'High Conscientiousness',
            'extraversion': 'High Extraversion'
        }
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header(f"💬 CBT Session: {condition_names[st.session_state.current_condition]}", anchor=False)
            st.caption(f"Personality: {personality_names[st.session_state.current_personality]}")
        
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chat_history:
                if chat['type'] == 'user':
                    with st.chat_message("user"):
                        st.write(chat['message'])
                else:
                    with st.chat_message("assistant"):
                        st.write(chat['message'])
        
        if not st.session_state.session_complete:
            total_questions = len(CBT_FLOWS[st.session_state.current_condition])
            progress = (st.session_state.current_step + 1) / total_questions
            st.progress(progress, text=f"Progress: {st.session_state.current_step + 1}/{total_questions}")
        
        if not st.session_state.session_complete:
            self.render_input_interface()
        else:
            self.render_completion_interface()

    def render_input_interface(self):
        with st.form("response_form", clear_on_submit=True):
            user_input = st.text_area(
                "Your response:",
                placeholder="Type your response here...",
                height=100,
                key="user_input"
            )
            submitted = st.form_submit_button("Submit Response", use_container_width=True)
            
            if submitted and user_input.strip():
                self.process_user_response(user_input.strip())

    def process_user_response(self, user_input: str):
        current_question = CBT_FLOWS[st.session_state.current_condition][st.session_state.current_step]
        
        st.session_state.chat_history.append({
            'type': 'user', 
            'message': user_input
        })
        
        st.session_state.responses[current_question['id']] = user_input
        
        gpt_success = False
        if openai.api_key:
            feedback = self.generate_gpt_feedback(
                st.session_state.current_personality,
                current_question,
                user_input,
                st.session_state.current_step
            )
            if not feedback:
                feedback = self.generator.generate_response(
                    st.session_state.current_personality,
                    current_question,
                    user_input,
                    st.session_state.current_step
                )
            else:
                gpt_success = True
        else:
            base_feedback = self.generator.generate_response(
                st.session_state.current_personality,
                current_question,
                user_input,
                st.session_state.current_step
            )
            sentiment, keywords = self.analyze_user_input(user_input)
            extra = ""
            if sentiment:
                extra += f" I sense you may be feeling **{sentiment}**."
            if keywords:
                extra += f" Key themes I noticed: *{keywords}*."
            feedback = base_feedback + extra

        st.session_state.chat_history.append({
            'type': 'bot',
            'message': feedback,
            'personality': st.session_state.current_personality
        })
        
        total_questions = len(CBT_FLOWS[st.session_state.current_condition])
        
        if st.session_state.current_step < total_questions - 1:
            st.session_state.current_step += 1
            if not gpt_success:
                next_question = CBT_FLOWS[st.session_state.current_condition][st.session_state.current_step]
                styled_q = self._style_question_with_personality(st.session_state.current_personality, next_question['text'])
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'message': styled_q,
                    'personality': st.session_state.current_personality
                })
        else:
            st.session_state.session_complete = True
            st.session_state.chat_history.append({
                'type': 'bot',
                'message': "You've completed the CBT reflection process! Would you like me to generate a journal summary of your session?",
                'personality': st.session_state.current_personality
            })
        
        st.rerun()

    def render_completion_interface(self):
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.journal_generated:
                if st.button("📝 Generate Journal Entry", use_container_width=True):
                    self.generate_journal()
            else:
                if st.button("💾 Download Journal", use_container_width=True):
                    self.download_journal()
        
        with col2:
            if st.button("🔄 Try Different Condition", use_container_width=True):
                conditions = ['stress', 'anxiety', 'lowMood']
                current_idx = conditions.index(st.session_state.current_condition)
                next_condition = conditions[(current_idx + 1) % len(conditions)]
                self.start_condition(next_condition)

    def generate_journal(self):
        journal_content = self.create_journal()
        st.session_state.journal_content = journal_content
        st.session_state.journal_generated = True
        
        closing_msg = PERSONALITY_RESPONSES[st.session_state.current_personality]['closing']
        st.session_state.chat_history.append({
            'type': 'bot',
            'message': f"I've generated your journal entry! {closing_msg}",
            'personality': st.session_state.current_personality
        })
        
        st.rerun()

    def create_journal(self):
        condition_names = {'stress': 'Stress', 'anxiety': 'Anxiety', 'lowMood': 'Low Mood'}
        personality_names = {
            'neutral': 'Neutral',
            'conscientiousness': 'High Conscientiousness',
            'extraversion': 'High Extraversion'
        }
        
        journal = f"""# CBT Journal Entry - {condition_names[st.session_state.current_condition]} Session

**Session Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Condition Focus:** {condition_names[st.session_state.current_condition]}
**Chatbot Personality:** {personality_names[st.session_state.current_personality]}

---

## Session Responses

"""
        
        questions = CBT_FLOWS[st.session_state.current_condition]
        current_category = ""
        
        for question in questions:
            if question['id'] in st.session_state.responses:
                if question['category'] != current_category:
                    current_category = question['category']
                    journal += f"\n### {current_category}\n\n"
                
                journal += f"**Q:** {question['text']}\n\n"
                journal += f"**A:** {st.session_state.responses[question['id']]}\n\n"
        
        journal += f"""---

## Session Summary

This CBT session helped me explore the connections between my situation, thoughts, emotions, and behaviors. Through systematic examination, I identified key patterns and developed more balanced perspectives. The insights gained from this session provide a foundation for implementing healthier coping strategies.

**Next Steps:** Continue practicing the balanced thoughts and coping strategies identified in this session.

---

*Session completed on {datetime.now().strftime('%B %d, %Y')} using {personality_names[st.session_state.current_personality]} personality style.*
"""
        
        return journal

    def download_journal(self):
        if st.session_state.journal_generated:
            filename = f"cbt-journal-{st.session_state.current_condition}-{st.session_state.current_personality}-{datetime.now().strftime('%Y-%m-%d')}.md"
            
            st.download_button(
                label="💾 Download Journal Entry",
                data=st.session_state.journal_content,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True
            )

    def render_sidebar_info(self):
        st.sidebar.divider()
        st.sidebar.header("📊 Session Info")
        
        if st.session_state.current_condition:
            condition_names = {'stress': 'Stress', 'anxiety': 'Anxiety', 'lowMood': 'Low Mood'}
            st.sidebar.metric("Current Condition", condition_names[st.session_state.current_condition])
            
            total_questions = len(CBT_FLOWS[st.session_state.current_condition])
            st.sidebar.metric("Questions Answered", f"{st.session_state.current_step + 1}/{total_questions}")
            
            if st.session_state.responses:
                avg_length = sum(len(response) for response in st.session_state.responses.values()) // len(st.session_state.responses)
                st.sidebar.metric("Avg Response Length", f"{avg_length} chars")
        
        st.sidebar.divider()
        st.sidebar.header("ℹ️ About")
        st.sidebar.info(
            "This system is designed for research on how chatbot personality "
            "affects CBT therapeutic writing effectiveness. Each personality "
            "follows the same CBT structure but with different communication styles."
        )

    def run(self):
        inject_personality_css(st.session_state.current_personality)
        self.render_header()
        self.render_personality_selector()
        
        if st.session_state.current_condition is None:
            self.render_condition_selector()
        else:
            self.render_chat_interface()
        
        if st.session_state.journal_generated and 'journal_content' in st.session_state:
            st.divider()
            st.header("📝 Your CBT Journal Entry")
            st.markdown(st.session_state.journal_content)
        
        self.render_sidebar_info()
        self.render_api_key_input()

    def analyze_user_input(self, text: str):
        """Return sentiment and keywords using OpenAI if available, otherwise TextBlob"""
        sentiment = ""
        keywords = ""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts sentiment (positive, neutral, negative) and 3 main keywords from user text, return JSON with 'sentiment' and 'keywords' (comma-separated)."},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=30,
                    temperature=0.0,
                )
                import json
                content = completion.choices[0].message.content
                data = json.loads(content)
                sentiment = data.get("sentiment", "")
                keywords = data.get("keywords", "")
            except Exception:
                pass
        if not sentiment:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.2:
                sentiment = "positive"
            elif polarity < -0.2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            try:
                keywords = ", ".join(blob.noun_phrases[:3])
            except Exception:
                words = [w.strip('.,!?').lower() for w in text.split()]
                unique = []
                for w in words:
                    if w.isalpha() and len(w) > 3 and w not in unique:
                        unique.append(w)
                    if len(unique) == 3:
                        break
                keywords = ", ".join(unique)
        return sentiment, keywords

    def generate_gpt_feedback(self, personality: str, question: dict, user_input: str, step: int) -> str:
        """Get feedback from OpenAI based on personality style"""
        if not openai.api_key:
            return ""

        style_guide = self.big5_templates.get(personality, "")
        if not style_guide:
            print(f"Warning: Could not find style guide for personality '{personality}'")

        system_prompt = (
            "You are a compassionate CBT journaling assistant. Your primary goal is to help the user through a structured CBT session. "
            "You MUST adopt the following personality style when crafting your response. This style guide is your highest priority. "
            "Follow all lexical, syntactic, and behavioral patterns described.\n\n"
            f"--- PERSONALITY STYLE GUIDE ---\n{style_guide}\n--- END STYLE GUIDE ---\n\n"
            "Acknowledge the user's input, provide a brief reflective statement, and encourage them to answer the next question. "
            "Your response should seamlessly transition to the next step of the CBT flow."
        )

        template_ref = self.condition_templates.get(st.session_state.current_condition, "")

        user_msg = (
            f"Current CBT Session Context:\n{template_ref[:1000]}\n\n"
            f"The user is on step {step + 1}. The current question was: '{question.get('text')}'\n"
            f"The user's answer is: '{user_input}'\n\n"
            "Now, generate a response that helps the user and perfectly matches the personality style guide."
        )
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=120,
                temperature=0.7,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print("GPT feedback error", e)
            return ""

    def load_condition_templates(self):
        templates = {}
        try:
            with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                text = f.read()
            sections = {
                'stress': 'User with stress condition:',
                'anxiety': 'User with anxious condition:',
                'lowMood': 'User with low mood condition:'
            }
            for key, marker in sections.items():
                start = text.find(marker)
                if start != -1:
                    end = min(len(text), start + 1500)
                    templates[key] = text[start:end]
        except Exception as e:
            print("Could not load templates", e)
        return templates

    def load_big5_templates(self):
        """Load Big Five personality templates"""
        templates = {}
        try:
            with open(BIG5_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                text = f.read()
            
            conscientious_marker = "2. HIGH CONSCIENTIOUSNESS TEMPLATE"
            extraversion_marker = "3. HIGH EXTRAVERSION TEMPLATE"
            
            parts = text.split(conscientious_marker)
            templates['neutral'] = parts[0].strip()
            
            remaining = parts[1]
            parts = remaining.split(extraversion_marker)
            templates['conscientiousness'] = conscientious_marker + '\n' + parts[0].strip()
            templates['extraversion'] = extraversion_marker + '\n' + parts[1].strip()

        except Exception as e:
            print(f"Could not load Big 5 personality templates: {e}")
        return templates

    def _style_question_with_personality(self, personality: str, question_text: str) -> str:
        """Apply personality-specific styling to questions"""
        if personality == 'extraversion':
            intros = [
                "Awesome, let's keep the ball rolling!",
                "Great job! Let's jump into the next part.",
                "Okay, let's get to the next exciting bit!",
                "This is so insightful! Next up:",
            ]
            return f"{random.choice(intros)} {question_text}"

        elif personality == 'conscientiousness':
            intros = [
                "Proceeding to the next logical step:",
                "For our next point of analysis:",
                "To continue our systematic review:",
                "The next item on our agenda is:",
            ]
            return f"{random.choice(intros)} {question_text}"
        
        else:
            return question_text

if __name__ == "__main__":
    app = CBTChatbotApp()
    app.run()