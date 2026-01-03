# Chat/app.py
import streamlit as st
import os
import io
import time
import uuid
import html
import pyperclip
import pandas as pd
import plotly.express as px
from datetime import datetime

# Try to import RAG chatbot, handle errors gracefully
RAG_AVAILABLE = True
RAG_ERROR = None
try:
    from rag_chatbot import load_vector_store, query_dataset
except Exception as e:
    RAG_AVAILABLE = False
    RAG_ERROR = str(e)
    # Create dummy functions
    def load_vector_store(dataset_name):
        return None
    def query_dataset(question, retriever):
        return f"RAG system unavailable: {RAG_ERROR}. Please check your dependencies."

# Optional PDF export - will fail gracefully if reportlab isn't installed
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
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

/* Scrollable chat column with custom scrollbar */
.chat-area {
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 12px;
  scroll-behavior: smooth;
}

.chat-area::-webkit-scrollbar {
  width: 8px;
}

.chat-area::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.02);
  border-radius: 10px;
}

.chat-area::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--primary), var(--secondary));
  border-radius: 10px;
  transition: all 0.3s ease;
}

.chat-area::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, var(--primary-light), var(--secondary-light));
}

/* Message row with animation */
.msg-row { 
  display: flex; 
  gap: 14px; 
  align-items: flex-end; 
  margin: 16px 0;
  animation: slideInUp 0.4s ease-out;
}

/* Avatar with glow effect */
.avatar { 
  width: 48px; 
  height: 48px; 
  border-radius: 12px; 
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(139,92,246,0.4);
  border: 2px solid rgba(139,92,246,0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.avatar:hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 8px 24px rgba(139,92,246,0.6);
}

/* Bubble with enhanced gradients and shadows */
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

.bubble-user:hover {
  box-shadow: 
    var(--shadow-lg),
    0 0 30px rgba(16,185,129,0.5);
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

.bubble-bot:hover {
  background: linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(6,182,212,0.15) 100%);
  border-color: rgba(139,92,246,0.3);
}

/* Metadata */
.meta { 
  font-size: 13px; 
  color: var(--text-muted); 
  margin-top: 8px;
  font-weight: 500;
  letter-spacing: 0.3px;
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

.chip::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.chip:hover::before {
  width: 300px;
  height: 300px;
}

.chip:hover { 
  transform: translateY(-4px) scale(1.05);
  background: linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(6,182,212,0.15) 100%);
  border-color: rgba(139,92,246,0.5);
  box-shadow: 
    var(--shadow-md),
    0 0 20px rgba(139,92,246,0.3);
}

.chip:active {
  transform: translateY(-2px) scale(1.02);
}

/* Actions */
.actions { 
  display: flex; 
  gap: 12px; 
  margin-top: 10px;
}

.action-btn { 
  background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(6,182,212,0.06) 100%);
  border: 1px solid rgba(139,92,246,0.25);
  padding: 8px 14px; 
  border-radius: 10px; 
  cursor: pointer; 
  color: var(--text-primary);
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
  box-shadow: var(--shadow-sm);
}

.action-btn:hover { 
  transform: translateY(-3px);
  background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(6,182,212,0.12) 100%);
  border-color: rgba(139,92,246,0.4);
  box-shadow: 
    var(--shadow-md),
    0 0 15px rgba(139,92,246,0.2);
}

/* Typing placeholder with pulse animation */
.typing { 
  display: inline-flex; 
  gap: 8px; 
  padding: 12px 16px; 
  background: linear-gradient(135deg, rgba(139,92,246,0.1) 0%, rgba(6,182,212,0.08) 100%);
  border-radius: 12px;
  border: 1px solid rgba(139,92,246,0.2);
}

.dot { 
  width: 10px; 
  height: 10px; 
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: 50%; 
  animation: bounce 1.2s infinite ease-in-out;
  box-shadow: 0 0 10px rgba(139,92,246,0.5);
}

.dot:nth-child(2) { animation-delay: 0.15s; }
.dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes bounce { 
  0%, 100% { transform: translateY(0); opacity: 0.6; } 
  50% { transform: translateY(-10px); opacity: 1; } 
}

/* Input area with glassmorphism */
.input-area { 
  position: sticky; 
  bottom: 0; 
  background: linear-gradient(180deg, rgba(10,14,26,0.0), rgba(10,14,26,0.95));
  backdrop-filter: blur(10px);
  padding: 16px; 
  border-top: 1px solid rgba(139,92,246,0.2);
  margin-top: 20px;
}

/* Collapsible preview */
.short { 
  max-height: 180px; 
  overflow: hidden; 
  position: relative;
}

.fadeout { 
  position: absolute; 
  bottom: 0; 
  left: 0; 
  right: 0; 
  height: 60px; 
  background: linear-gradient(180deg, rgba(10,14,26,0.0), rgba(10,14,26,0.98));
  border-bottom-left-radius: 16px; 
  border-bottom-right-radius: 16px;
}

/* Sidebar with enhanced styling */
[data-testid="stSidebar"] { 
  background: linear-gradient(180deg, #0f0a1e 0%, #0a0e1a 100%);
  color: var(--text-primary);
  border-right: 1px solid rgba(139,92,246,0.15);
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
  position: relative !important;
  overflow: hidden !important;
}

.stButton > button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.stButton > button:hover::before {
  left: 100%;
}

.stButton > button:hover {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: 
    var(--shadow-lg),
    0 0 25px rgba(139,92,246,0.4) !important;
}

.stButton > button:active {
  transform: translateY(-1px) scale(0.98) !important;
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

/* Enhanced selectbox */
.stSelectbox > div > div {
  background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(6,182,212,0.05) 100%) !important;
  border: 1px solid rgba(139,92,246,0.3) !important;
  border-radius: 12px !important;
  transition: all 0.3s ease !important;
}

.stSelectbox > div > div:hover {
  border-color: var(--primary) !important;
  box-shadow: 0 0 15px rgba(139,92,246,0.2) !important;
}

/* Download button styling */
.stDownloadButton > button {
  background: linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(139,92,246,0.1) 100%) !important;
  border: 1px solid rgba(245,158,11,0.4) !important;
  color: var(--text-primary) !important;
  border-radius: 10px !important;
  padding: 10px 18px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.stDownloadButton > button:hover {
  background: linear-gradient(135deg, rgba(245,158,11,0.25) 0%, rgba(139,92,246,0.15) 100%) !important;
  border-color: rgba(245,158,11,0.6) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 20px rgba(245,158,11,0.3) !important;
}

/* Responsive design */
@media (max-width: 760px) {
  .avatar { width: 40px; height: 40px; }
  .bubble { max-width: 88%; font-size: 14px; padding: 12px 14px; }
  .chat-area { max-height: 55vh; }
  .title-row h1 { font-size: 28px; }
  .chip { padding: 8px 12px; font-size: 13px; }
}

/* Loading animation */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Glow effect for important elements */
.glow {
  animation: pulse 2s ease-in-out infinite;
}

/* Smooth transitions for all interactive elements */
* {
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
""", unsafe_allow_html=True)

# ---------------- Helpers ----------------
def escape_html(text: str) -> str:
    return html.escape(text).replace("\n", "<br/>")

def try_parse_table(text: str):
    """Return DataFrame if text is CSV-like, else None"""
    try:
        df = pd.read_csv(io.StringIO(text))
        return df
    except Exception:
        return None

def gen_pdf_from_df(df: pd.DataFrame):
    """Return bytes of a simple PDF for df if reportlab present, else None"""
    if not REPORTLAB_AVAILABLE:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    textobject = c.beginText(40, height - 40)
    textobject.setFont("Helvetica", 10)
    # write a few rows nicely
    textobject.textLine("Table preview")
    textobject.moveCursor(0, 14)
    cols = df.columns.tolist()
    textobject.textLine(" | ".join(cols[:6]))
    textobject.moveCursor(0, 12)
    for i, row in df.head(20).iterrows():
        row_vals = [str(row[c])[:30].replace("\n"," ") for c in cols[:6]]
        textobject.textLine(" | ".join(row_vals))
        textobject.moveCursor(0, 6)
    c.drawText(textobject)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

def auto_choose_chart(df: pd.DataFrame):
    """Return a Plotly figure chosen by heuristics"""
    # If first column is datetime-like, use line
    for c in df.columns:
        try:
            parsed = pd.to_datetime(df[c], errors='coerce')
            if parsed.notna().sum() > len(df) * 0.5:
                # treat as time series
                y_cols = df.select_dtypes(include='number').columns.tolist()
                if not y_cols:
                    y_cols = df.columns[1:2] if len(df.columns) > 1 else []
                if y_cols:
                    fig = px.line(df, x=c, y=y_cols, title="Time series")
                    return fig
        except Exception:
            pass
    # Categorical first col small unique -> bar
    first = df.columns[0]
    if df[first].nunique() <= 30:
        # pick numeric column to aggregate
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            fig = px.bar(df, x=first, y=numeric_cols[0], title=f"Bar: {numeric_cols[0]} by {first}")
            return fig
    # fallback scatter of two numeric columns
    nums = df.select_dtypes(include='number').columns.tolist()
    if len(nums) >= 2:
        fig = px.scatter(df, x=nums[0], y=nums[1], title=f"Scatter: {nums[0]} vs {nums[1]}")
        return fig
    # else simple table-like fig (use head)
    fig = px.bar(df.head(10), x=df.columns[0], y=df.columns[1]) if len(df.columns) > 1 else None
    return fig

def history_to_markdown(history):
    md = []
    for q, a, ts in history:
        md.append(f"### Q — {q}\n\n")
        md.append(f"{a}\n\n")
    return "\n".join(md)

# ---------------- Session state init ----------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of (q, a, ts)
if "active_question" not in st.session_state:
    st.session_state.active_question = None
if "active_answer" not in st.session_state:
    st.session_state.active_answer = None
if "query" not in st.session_state:
    st.session_state.query = ""
if "processing" not in st.session_state:
    st.session_state.processing = False
if "show_more_map" not in st.session_state:
    st.session_state.show_more_map = {}
if "last_question_key" not in st.session_state:
    st.session_state.last_question_key = None

# ---------------- Sidebar: dataset + history + analysis controls ----------------
VECTOR_STORE_DIR = "vector_store"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
available_datasets = [n for n in os.listdir(VECTOR_STORE_DIR) if os.path.isdir(os.path.join(VECTOR_STORE_DIR, n))]

with st.sidebar:
    st.markdown("## 📂 Dataset & History")
    if not available_datasets:
        st.warning("No datasets found. Run `build_vector_stores.py` to create vector stores.")
        dataset = None
    else:
        dataset = st.selectbox("Choose dataset", sorted(available_datasets), index=0)

    st.markdown("---")
    st.markdown("### 🕘 Conversation History")
    if st.session_state.history:
        # show most recent first
        for i in range(len(st.session_state.history)-1, -1, -1):
            q, a, ts = st.session_state.history[i]
            cols = st.columns([0.75, 0.25])
            with cols[0]:
                if st.button(f"{q[:40]}...", key=f"hist_load_{i}"):
                    st.session_state.active_question = q
                    st.session_state.active_answer = a
                    st.session_state.query = q
            with cols[1]:
                if st.button("🗑", key=f"hist_del_{i}"):
                    st.session_state.history.pop(i)
                    st.rerun()
    else:
        st.info("No history yet.")

    st.markdown("---")
    st.markdown("### 📈 Data Analysis")
    st.markdown("Quick insights & visualizations for the selected dataset.")
    if dataset:
        # try to find a CSV in dataset folder for quick analysis (non-destructive)
        ds_path = os.path.join(VECTOR_STORE_DIR, dataset)
        # search for common CSV file names in the dataset folder
        sample_df = None
        for fname in os.listdir(ds_path):
            if fname.lower().endswith(".csv"):
                try:
                    sample_df = pd.read_csv(os.path.join(ds_path, fname), nrows=1000)
                    break
                except Exception:
                    sample_df = None
        if sample_df is not None:
            st.markdown(f"**Sample rows:** {sample_df.shape[0]} rows × {sample_df.shape[1]} cols")
            if st.button("Show dataset preview"):
                st.dataframe(sample_df.head(10))
            if st.button("Show quick chart"):
                fig = auto_choose_chart(sample_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Could not auto-generate a chart for this dataset.")
        else:
            st.info("No CSV preview available in the dataset folder.")
    st.markdown("---")
    # download whole conversation as Markdown
    if st.session_state.history:
        md = history_to_markdown(st.session_state.history)
        st.download_button("📥 Download conversation (MD)", data=md, file_name="conversation.md", mime="text/markdown")

# ---------------- Main layout ----------------
st.markdown('<div class="chat-card">', unsafe_allow_html=True)

# header
st.markdown('<div class="title-row"><h1>AI Trend Twin Chatbot</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Use the chat to query your selected dataset. Responses appear instantly and include analysis if table data is returned.</div>', unsafe_allow_html=True)

# Show warning if RAG is unavailable
if not RAG_AVAILABLE:
    st.warning(f"⚠️ RAG System Unavailable: {RAG_ERROR[:200]}... The UI is working but backend needs fixing.")

# chat + right info column layout
left_col, right_col = st.columns([3, 1])

with left_col:
    # Chat area
    st.markdown('<div class="chat-area" id="chat-area">', unsafe_allow_html=True)

    # Show active loaded q/a (if set via history load)
    if st.session_state.active_question and st.session_state.active_answer:
        q = st.session_state.active_question
        a = st.session_state.active_answer
        ts = next((t for (qq, aa, t) in st.session_state.history if qq == q and aa == a), "")
        st.markdown(f'''
            <div class="msg-row">
                <div style="flex:1"></div>
                <div class="bubble bubble-user">{escape_html(q)}</div>
                <img class="avatar" src="https://img.icons8.com/fluency/48/000000/user-male-circle.png" />
            </div>
        ''', unsafe_allow_html=True)
        # bot bubble
        st.markdown(f'''
            <div class="msg-row">
                <img class="avatar" src="https://img.icons8.com/fluency/48/000000/artificial-intelligence.png" />
                <div class="bubble bubble-bot">{escape_html(a)}</div>
                <div style="flex:1"></div>
            </div>
        ''', unsafe_allow_html=True)

    # Render full chat history
    for idx, (q, a, ts) in enumerate(st.session_state.history):
        # user
        st.markdown(f'''
            <div class="msg-row" id="msg-{idx}">
                <div style="flex:1"></div>
                <div class="bubble bubble-user">{escape_html(q)}</div>
                <img class="avatar" src="https://img.icons8.com/fluency/48/000000/user-male-circle.png" />
            </div>
        ''', unsafe_allow_html=True)

        # prepare bot content with collapse if long
        uid = f"{uuid.uuid4().hex[:8]}_{idx}"
        is_long = len(a) > 800
        show_more = st.session_state.show_more_map.get(uid, False)
        if is_long and not show_more:
            preview = a[:700] + "..."
            inner = f'<div class="short">{escape_html(preview)}<div class="fadeout"></div></div>'
        else:
            inner = escape_html(a)

        st.markdown(f'''
            <div class="msg-row">
                <img class="avatar" src="https://img.icons8.com/fluency/48/000000/artificial-intelligence.png" />
                <div style="display:flex; flex-direction:column; gap:6px; width:100%;">
                    <div class="bubble bubble-bot" id="bot-{uid}">{inner}</div>
                    <div class="meta">Response · {ts}</div>
                </div>
                <div style="flex:1"></div>
            </div>
        ''', unsafe_allow_html=True)

        # Show more / show less controls (unique keys)
        if is_long:
            if not show_more:
                if st.button("Show more", key=f"show_{uid}"):
                    st.session_state.show_more_map[uid] = True
                    st.rerun()
            else:
                if st.button("Show less", key=f"hide_{uid}"):
                    st.session_state.show_more_map[uid] = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # close chat-area

    # Auto-scroll to bottom script (simple)
    st.markdown("""
    <script>
    (function() {
      const el = document.getElementById('chat-area');
      if (el) { el.scrollTop = el.scrollHeight; }
    })();
    </script>
    """, unsafe_allow_html=True)

    # Input area (sticky)
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    with st.form(key="main_input_form", clear_on_submit=False):
        user_input = st.text_input("Ask a trend question...", value=st.session_state.query, key="main_input")
        cols = st.columns([0.12, 0.12, 0.3, 0.46])
        with cols[0]:
            submit = st.form_submit_button("Send")
        with cols[1]:
            ask_again = st.form_submit_button("Ask Again")  # reruns last question
        with cols[2]:
            if st.button("Copy last", key="copy_last_btn"):
                if st.session_state.active_answer:
                    try:
                        pyperclip.copy(st.session_state.active_answer)
                        st.toast("Copied!")
                    except Exception:
                        st.warning("Clipboard unavailable in this environment.")
        with cols[3]:
            pass  # placeholder for layout

    # Quick suggestion chips
    st.markdown('<div class="chips">', unsafe_allow_html=True)
    suggestions = [
        "Show top trends",
        "Give me a one-line summary",
        "List 3 actionable insights",
        "Show top 5 keywords"
    ]
    for s in suggestions:
        if st.button(s, key=f"chip_{s}"):
            st.session_state.query = s
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Process "Ask Again" - re-run last question
    if ask_again:
        if st.session_state.active_question:
            st.session_state.query = st.session_state.active_question
            st.rerun()

    # Process Send submit
    if submit and user_input and dataset:
        # Prevent double-processing
        if not st.session_state.processing:
            st.session_state.processing = True
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Append a placeholder (user question with empty answer)
            st.session_state.history.append((user_input, "", ts))
            # Show typing UI immediately via placeholder
            typing_ph = st.empty()
            typing_ph.markdown(f'''
                <div class="msg-row">
                    <img class="avatar" src="https://img.icons8.com/fluency/48/000000/artificial-intelligence.png" />
                    <div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
                </div>
            ''', unsafe_allow_html=True)

            # -- ORIGINAL BACKEND CALLS (kept intact) --
            try:
                retriever = load_vector_store(dataset)
                answer = query_dataset(user_input, retriever)
            except Exception as e:
                answer = f"Error: {e}"
            # -- end original calls --

            # remove typing placeholder
            typing_ph.empty()

            # update last placeholder entry with actual answer
            last_idx = None
            for i in range(len(st.session_state.history)-1, -1, -1):
                if st.session_state.history[i][0] == user_input and st.session_state.history[i][1] == "":
                    last_idx = i
                    break
            if last_idx is not None:
                st.session_state.history[last_idx] = (user_input, answer, ts)
            else:
                st.session_state.history.append((user_input, answer, ts))

            st.session_state.active_question = user_input
            st.session_state.active_answer = answer
            st.session_state.query = ""
            st.session_state.processing = False

            # rerun to show updated UI (clear input)
            st.rerun()
    elif submit and user_input and not dataset:
        st.warning("Please select a dataset from the sidebar first.")

    st.markdown('</div>', unsafe_allow_html=True)  # close input-area

with right_col:
    st.markdown("### Info & Visuals")
    st.markdown("**Last question:**")
    if st.session_state.active_question:
        st.write(st.session_state.active_question)
    else:
        st.write("—")

    st.markdown("**Last answer preview:**")
    if st.session_state.active_answer:
        # if table-like -> render with download options and auto-chart
        df = try_parse_table(st.session_state.active_answer)
        if df is not None:
            st.markdown("#### Table detected in last answer")
            st.dataframe(df.head(8))
            # download CSV
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download table (CSV)", data=csv_bytes, file_name="answer_table.csv", mime="text/csv")
            # PDF if available
            pdf_bytes = gen_pdf_from_df(df)
            if pdf_bytes:
                st.download_button("Download table (PDF)", data=pdf_bytes, file_name="answer_table.pdf", mime="application/pdf")
            # auto chart
            fig = auto_choose_chart(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            # show text preview
            st.write(st.session_state.active_answer[:400] + ("..." if len(st.session_state.active_answer) > 400 else ""))
    else:
        st.write("—")

    st.markdown("---")
    # Actions for last message
    if st.session_state.active_answer:
        if st.button("📋 Copy latest", key="copy_latest_side"):
            try:
                pyperclip.copy(st.session_state.active_answer)
                st.toast("Copied!")
            except Exception:
                st.warning("Clipboard not available.")

        if st.button("👍 Like latest", key="like_latest"):
            st.toast("Thanks for the feedback!")

        if st.button("👎 Dislike latest", key="dislike_latest"):
            st.toast("We’ll try to improve it.")

    st.markdown("---")
    st.markdown("Tips")
    st.markdown("- Use the suggestion chips for quick prompts\n- Choose dataset from sidebar for relevant answers\n- Download tables directly as CSV or PDF (if supported)")

st.markdown('</div>', unsafe_allow_html=True)  # close chat-card
