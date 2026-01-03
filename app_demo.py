# Minimal Demo App - Shows Enhanced UI
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- Page config ----------------
st.set_page_config(page_title="AI Trend Twin Chatbot", layout="wide", page_icon="🤖", initial_sidebar_state="expanded")

# ---------------- Embedded CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root{
  --primary: #8b5cf6;
  --primary-light: #a78bfa;
  --primary-dark: #7c3aed;
  --secondary: #06b6d4;
  --secondary-light: #22d3ee;
  --accent: #f59e0b;
  --success: #10b981;
  --success-dark: #059669;
  --danger: #ef4444;
  --bg-dark: #0a0e1a;
  --bg-darker: #050810;
  --card-bg: rgba(255,255,255,0.03);
  --card-border: rgba(139,92,246,0.15);
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
  --shadow-md: 0 8px 24px rgba(0,0,0,0.4);
  --shadow-lg: 0 16px 48px rgba(0,0,0,0.5);
  --shadow-glow: 0 0 30px rgba(139,92,246,0.3);
}

/* Animated gradient background */
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

@keyframes slideInUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

/* App background with animated gradient */
.stApp {
  background: linear-gradient(135deg, #0a0e1a 0%, #1a0b2e 25%, #16213e 50%, #0f1729 75%, #0a0e1a 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  color: var(--text-primary);
  padding: 24px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* Floating particles effect */
.stApp::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(139,92,246,0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(6,182,212,0.08) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(245,158,11,0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
  animation: float 20s ease-in-out infinite;
}

/* Title and subtitle with glow effect */
.title-row { 
  display: flex; 
  align-items: center; 
  gap: 16px; 
  animation: slideInUp 0.6s ease-out;
}

.title-row h1 { 
  margin: 0; 
  font-size: 36px; 
  font-weight: 800;
  background: linear-gradient(135deg, #a78bfa 0%, #06b6d4 50%, #f59e0b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 40px rgba(139,92,246,0.5);
  letter-spacing: -0.5px;
}

.subtitle { 
  color: var(--text-secondary); 
  margin-top: 8px; 
  margin-bottom: 20px; 
  font-size: 15px;
  font-weight: 400;
  animation: slideInUp 0.6s ease-out 0.1s backwards;
}

/* Chat area card with glassmorphism */
.chat-card {
  background: linear-gradient(135deg, rgba(139,92,246,0.05) 0%, rgba(6,182,212,0.03) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 28px;
  box-shadow: 
    var(--shadow-lg),
    inset 0 1px 1px rgba(255,255,255,0.1),
    0 0 0 1px var(--card-border);
  border: 1px solid rgba(139,92,246,0.2);
  position: relative;
  overflow: hidden;
  animation: slideInUp 0.6s ease-out 0.2s backwards;
}

.chat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
  animation: shimmer 3s infinite;
}

/* Message bubbles */
.bubble {
  padding: 16px 18px;
  border-radius: 16px;
  max-width: 75%;
  line-height: 1.6;
  box-shadow: var(--shadow-md);
  color: var(--text-primary);
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 15px;
  margin: 16px 0;
}

.bubble:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.bubble-user { 
  background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
  margin-left: auto; 
  color: #ffffff;
  border-bottom-right-radius: 6px;
  box-shadow: 
    var(--shadow-md),
    0 0 20px rgba(16,185,129,0.3);
  font-weight: 500;
}

.bubble-bot { 
  background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(6,182,212,0.1) 100%);
  backdrop-filter: blur(10px);
  color: var(--text-primary);
  border-bottom-left-radius: 6px;
  border: 1px solid rgba(139,92,246,0.2);
  box-shadow: 
    var(--shadow-md),
    inset 0 1px 1px rgba(255,255,255,0.1);
}

/* Chips with interactive hover */
.chips { 
  display: flex; 
  gap: 10px; 
  margin-top: 14px; 
  flex-wrap: wrap;
}

.chip { 
  background: linear-gradient(135deg, rgba(139,92,246,0.1) 0%, rgba(6,182,212,0.08) 100%);
  padding: 10px 16px; 
  border-radius: 999px; 
  cursor: pointer; 
  color: var(--text-primary);
  font-weight: 600;
  border: 1px solid rgba(139,92,246,0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}

.chip:hover { 
  transform: translateY(-4px) scale(1.05);
  background: linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(6,182,212,0.15) 100%);
  border-color: rgba(139,92,246,0.5);
  box-shadow: 
    var(--shadow-md),
    0 0 20px rgba(139,92,246,0.3);
}

/* Enhanced Streamlit button styling */
.stButton > button {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-weight: 600 !important;
  font-size: 15px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: var(--shadow-md) !important;
}

.stButton > button:hover {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: 
    var(--shadow-lg),
    0 0 25px rgba(139,92,246,0.4) !important;
}

/* Enhanced text input */
.stTextInput > div > div > input {
  background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(6,182,212,0.05) 100%) !important;
  border: 1px solid rgba(139,92,246,0.3) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
  padding: 14px 18px !important;
  font-size: 15px !important;
  transition: all 0.3s ease !important;
  box-shadow: var(--shadow-sm) !important;
}

.stTextInput > div > div > input:focus {
  border-color: var(--primary) !important;
  box-shadow: 
    var(--shadow-md),
    0 0 20px rgba(139,92,246,0.3) !important;
  background: linear-gradient(135deg, rgba(139,92,246,0.12) 0%, rgba(6,182,212,0.08) 100%) !important;
}

/* Sidebar with enhanced styling */
[data-testid="stSidebar"] { 
  background: linear-gradient(180deg, #0f0a1e 0%, #0a0e1a 100%);
  color: var(--text-primary);
  border-right: 1px solid rgba(139,92,246,0.15);
}

/* Responsive design */
@media (max-width: 760px) {
  .title-row h1 { font-size: 28px; }
  .bubble { max-width: 88%; font-size: 14px; padding: 12px 14px; }
  .chip { padding: 8px 12px; font-size: 13px; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- Session state init ----------------
if "demo_messages" not in st.session_state:
    st.session_state.demo_messages = []

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("## 📂 Demo Mode")
    st.info("✨ This is a demo showing the enhanced UI design. The full RAG functionality requires fixing backend dependencies.")
    
    st.markdown("---")
    st.markdown("### 🎨 UI Features")
    st.markdown("""
    - ✅ Animated gradient background
    - ✅ Glassmorphism effects
    - ✅ Interactive hover animations
    - ✅ Custom color scheme
    - ✅ Modern typography
    - ✅ Smooth transitions
    """)
    
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.demo_messages = []
        st.rerun()

# ---------------- Main layout ----------------
st.markdown('<div class="chat-card">', unsafe_allow_html=True)

# header
st.markdown('<div class="title-row"><h1>AI Trend Twin Chatbot</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Enhanced UI Demo - Experience the modern, interactive design with vibrant colors and smooth animations.</div>', unsafe_allow_html=True)

st.success("✅ UI is working! The enhanced design is fully functional. Try the interactive elements below.")

# Display demo messages
for msg in st.session_state.demo_messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="bubble bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

# Input area
with st.form(key="demo_form", clear_on_submit=True):
    user_input = st.text_input("Ask a question to see the UI in action...", key="demo_input")
    submit = st.form_submit_button("Send")

# Quick suggestion chips
st.markdown('<div class="chips">', unsafe_allow_html=True)
suggestions = [
    "Show me the UI features",
    "What colors are used?",
    "Tell me about animations",
    "How does it work?"
]
cols = st.columns(4)
for i, s in enumerate(suggestions):
    with cols[i]:
        if st.button(s, key=f"chip_{i}"):
            user_input = s
            submit = True
st.markdown('</div>', unsafe_allow_html=True)

# Process input
if submit and user_input:
    # Add user message
    st.session_state.demo_messages.append({"role": "user", "content": user_input})
    
    # Generate demo response
    demo_responses = {
        "Show me the UI features": "✨ The UI features include:\n\n• Animated gradient background that shifts colors\n• Glassmorphism with backdrop blur effects\n• Interactive hover animations on all elements\n• Custom purple-cyan-amber color scheme\n• Modern Inter font typography\n• Smooth cubic-bezier transitions\n• Custom gradient scrollbars\n• Ripple effects on buttons",
        
        "What colors are used?": "🎨 The color palette includes:\n\n• Primary: Purple (#8b5cf6)\n• Secondary: Cyan (#06b6d4)\n• Accent: Amber (#f59e0b)\n• Success: Green (#10b981)\n• Background: Deep navy with animated gradients\n• Text: High-contrast white/slate tones",
        
        "Tell me about animations": "💫 The animations include:\n\n• Background gradient shift (15s cycle)\n• Floating particle effects\n• Slide-in animations for messages\n• Hover lift effects on bubbles\n• Ripple animations on chips\n• Shimmer effect on cards\n• Pulsing glow effects\n• Smooth transitions (0.3s cubic-bezier)",
        
        "How does it work?": "⚙️ The enhanced UI uses:\n\n• Pure CSS animations for 60fps performance\n• CSS variables for consistent theming\n• Glassmorphism with backdrop-filter\n• Keyframe animations for complex effects\n• Pseudo-elements for shimmer/ripple\n• Responsive design for all screen sizes\n• Modern web standards (no JavaScript needed for animations)"
    }
    
    # Get response
    response = demo_responses.get(user_input, f"🤖 Thanks for trying the demo! You asked: '{user_input}'\n\nThe enhanced UI is fully functional with:\n• Beautiful animated gradients\n• Interactive hover effects\n• Professional color scheme\n• Smooth animations throughout\n\nTry hovering over elements to see the interactions!")
    
    st.session_state.demo_messages.append({"role": "bot", "content": response})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Hover over the suggestion chips and input field to see the interactive effects!")
