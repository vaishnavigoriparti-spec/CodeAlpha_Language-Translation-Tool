import streamlit as st
import pandas as pd
import time
import html
import re
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

# ==========================================
# 1. PAGE SETUP & INITIAL CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AuroraTranslate - Premium Multi-Language Translator",
    page_icon="🌅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DYNAMIC LANGUAGE LIST ACQUISITION
# ==========================================
@st.cache_data
def load_supported_languages():
    """Retrieve supported translation languages dynamically from Google Translator with local fallback."""
    try:
        translator = GoogleTranslator()
        languages_dict = translator.get_supported_languages(as_dict=True)
        # Capitalize language names for better UI display
        formatted_langs = {name.title(): code for name, code in languages_dict.items()}
        return formatted_langs
    except Exception:
        # Fallback to key global languages if network error
        return {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Chinese (Simplified)": "zh-CN",
            "Chinese (Traditional)": "zh-TW",
            "Japanese": "ja",
            "Korean": "ko",
            "Hindi": "hi",
            "Arabic": "ar",
            "Russian": "ru",
            "Turkish": "tr",
            "Vietnamese": "vi",
            "Dutch": "nl",
            "Greek": "el",
            "Polish": "pl",
            "Swedish": "sv"
        }

supported_languages = load_supported_languages()

# Map of non-Latin languages to their Google Input Tools transliteration code (ITC)
NON_LATIN_ITCS = {
    "Hindi": "hi-t-i0-und",
    "Japanese": "ja-t-i0-und",
    "Chinese (Simplified)": "zh-t-i0-und",
    "Chinese (Traditional)": "zh-hant-t-i0-und",
    "Russian": "ru-t-i0-und",
    "Arabic": "ar-t-i0-und",
    "Greek": "el-t-i0-und",
    "Hebrew": "he-t-i0-und",
    "Korean": "ko-t-i0-und",
    "Tamil": "ta-t-i0-und",
    "Telugu": "te-t-i0-und",
    "Kannada": "kn-t-i0-und",
    "Malayalam": "ml-t-i0-und",
    "Bengali": "bn-t-i0-und",
    "Gujarati": "gu-t-i0-und",
    "Marathi": "mr-t-i0-und",
    "Punjabi": "pa-t-i0-und"
}

# ==========================================
# 3. STATE INITIALIZATION (SESSION STATE)
# ==========================================
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

if "src_lang_selection" not in st.session_state:
    st.session_state.src_lang_selection = "Auto Detect"

if "tgt_lang_selection" not in st.session_state:
    st.session_state.tgt_lang_selection = "Spanish"

if "source_text_input" not in st.session_state:
    st.session_state.source_text_input = ""

if "translated_text_output" not in st.session_state:
    st.session_state.translated_text_output = ""

if "transliteration_preview" not in st.session_state:
    st.session_state.transliteration_preview = ""

if "translated_romanization" not in st.session_state:
    st.session_state.translated_romanization = ""

# Handle language swap operation
def swap_languages_action():
    current_source = st.session_state.src_lang_selection
    current_target = st.session_state.tgt_lang_selection
    
    # Can only swap if the source language is not a special option
    if current_source not in ["Auto Detect"]:
        st.session_state.src_lang_selection = current_target
        st.session_state.tgt_lang_selection = current_source
        
        # Swap texts if target text exists
        temp_text = st.session_state.source_text_input
        st.session_state.source_text_input = st.session_state.translated_text_output
        st.session_state.translated_text_output = temp_text

# ==========================================
# 4. CUSTOM CYBER SUNSET THEME STYLING
# ==========================================
def inject_cyber_sunset_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Cyber Sunset Glowing Header */
    .translation-header {
        background: linear-gradient(135deg, rgba(255, 78, 80, 0.1) 0%, rgba(249, 212, 35, 0.1) 50%, rgba(144, 36, 242, 0.1) 100%);
        border: 1px solid rgba(255, 78, 80, 0.25);
        border-radius: 20px;
        padding: 35px 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(255, 78, 80, 0.08);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .translation-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -50%;
        width: 200%;
        height: 100%;
        background: radial-gradient(circle, rgba(255, 78, 80, 0.06) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .app-title {
        font-size: 3.1rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #ff4e50 0%, #f9d425 50%, #9024f2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0px 2px 10px rgba(255, 78, 80, 0.25));
        letter-spacing: -0.5px;
    }
    
    .app-subtitle {
        font-size: 1.15rem;
        font-weight: 400;
        color: #94a3b8;
        margin-top: 10px;
        margin-bottom: 0;
    }
    
    /* Sidebar Profile Layout */
    .sidebar-avatar-section {
        text-align: center;
        padding: 25px 0 20px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 25px;
    }
    
    .pulsing-sunset-avatar {
        font-size: 4.2rem;
        margin-bottom: 12px;
        display: inline-block;
        animation: floatSunset 4s ease-in-out infinite;
    }
    
    @keyframes floatSunset {
        0% { transform: translateY(0px) scale(1); filter: drop-shadow(0 0 0px rgba(255, 78, 80, 0)); }
        50% { transform: translateY(-8px) scale(1.02); filter: drop-shadow(0 4px 15px rgba(255, 78, 80, 0.35)); }
        100% { transform: translateY(0px) scale(1); filter: drop-shadow(0 0 0px rgba(255, 78, 80, 0)); }
    }
    
    /* Card design for outputs and history logs */
    .cyber-card {
        background: rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(255, 78, 80, 0.15);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .cyber-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 78, 80, 0.35);
        box-shadow: 0 8px 32px rgba(255, 78, 80, 0.12);
    }
    
    /* Elegant Read-Only Translated Display Box */
    .translated-display-box {
        background: rgba(30, 41, 59, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
        min-height: 180px;
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.6;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Custom Styling for Streamlit Text Area Native Component */
    [data-testid="stTextArea"] textarea {
        background-color: rgba(30, 41, 59, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        transition: border-color 0.2s ease-in-out !important;
    }
    
    [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(255, 78, 80, 0.4) !important;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2), 0 0 10px rgba(255, 78, 80, 0.15) !important;
    }
    
    /* Character Count display styling */
    .char-count-text {
        font-size: 0.82rem;
        color: #64748b;
        text-align: right;
        margin-top: 5px;
    }
    
    /* Swap Button custom style alignment */
    .swap-btn-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        margin-top: 10px;
    }
    
    /* Native stream button alignment fixes */
    div.stButton > button {
        border-radius: 10px !important;
        transition: all 0.2s ease-in-out !important;
    }
    </style>
    """, unsafe_allow_html=True)

inject_cyber_sunset_theme()

# ==========================================
# 5. DYNAMIC MULTILINGUAL CLIENT TTS & CLIPBOARD COPY UTILITIES
# ==========================================
def generate_translation_utilities_html(text_to_process, target_lang_code, unique_key):
    """Embed Web Speech API and Clipboard Copy functionalities using custom glowing buttons."""
    escaped_text = html.escape(text_to_process.replace("'", "\\'").replace("\n", " "))
    copy_button_id = f"copy_trigger_{unique_key}"
    speech_button_id = f"speech_trigger_{unique_key}"
    
    html_elements = f"""
    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 15px;">
        <button id="{copy_button_id}" class="glow-utility-btn" onclick="navigator.clipboard.writeText('{escaped_text}'); var btn = document.getElementById('{copy_button_id}'); btn.innerHTML = '📋 Copied!'; setTimeout(function() {{ btn.innerHTML = '📋 Copy'; }}, 2000);">📋 Copy</button>
        <button id="{speech_button_id}" class="glow-utility-btn" onclick="window.speechSynthesis.cancel(); var utterance = new SpeechSynthesisUtterance('{escaped_text}'); utterance.lang = '{target_lang_code}'; window.speechSynthesis.speak(utterance); var sBtn = document.getElementById('{speech_button_id}'); sBtn.innerHTML = '🔊 Speaking...'; utterance.onend = function() {{ sBtn.innerHTML = '🔊 Speak'; }};">🔊 Speak</button>
    </div>
    <style>
        .glow-utility-btn {{
            background: linear-gradient(135deg, rgba(255, 78, 80, 0.05), rgba(144, 36, 242, 0.05));
            color: #ff4e50;
            border: 1px solid rgba(255, 78, 80, 0.35);
            border-radius: 10px;
            padding: 6px 16px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            font-weight: 500;
            outline: none;
        }}
        .glow-utility-btn:hover {{
            background: linear-gradient(135deg, #ff4e50, #9024f2);
            color: #0f172a !important;
            border-color: transparent;
            box-shadow: 0 0 15px rgba(255, 78, 80, 0.45);
            transform: translateY(-1px);
        }}
        .glow-utility-btn:active {{
            transform: translateY(0px);
        }}
    </style>
    """
    return html_elements

# ==========================================
# 6. TRANSLATION & TRANSLITERATION PROCESSING ENGINE
# ==========================================
def is_latin_script(text):
    """Check if the text is composed exclusively of standard Latin (English) characters."""
    cleaned = re.sub(r'[\s\d\.,!\?\-\'"]', '', text)
    if not cleaned:
        return True
    return all(ord(char) < 128 for char in cleaned)

def transliterate_to_native(text, language_name):
    """Phonetically transliterate Latin script into the target native script using Google Input Tools."""
    if not text.strip():
        return ""
    
    itc_code = NON_LATIN_ITCS.get(language_name)
    if not itc_code:
        return text # No transliteration layout for this language
        
    try:
        url = "https://inputtools.google.com/request"
        params = {
            "text": text,
            "itc": itc_code,
            "num": 1
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data[0] == "SUCCESS":
                words_data = data[1]
                transliterated_words = [word_info[1][0] for word_info in words_data]
                return " ".join(transliterated_words)
    except Exception:
        pass
    return text

def translate_and_romanize(text, source_code, target_code):
    """Query Google Translate to retrieve both the translation and the target pronunciation/romanization."""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_code,
            "tl": target_code,
            "dt": ["t", "rm"],
            "q": text
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            translated_text = ""
            romanized_text = ""
            
            if data and data[0]:
                translation_parts = []
                for part in data[0]:
                    if part[0] is not None:
                        translation_parts.append(part[0])
                    elif len(part) >= 3 and part[2] is not None:
                        # Extract Romanized pronunciation
                        romanized_text = part[2]
                translated_text = "".join(translation_parts)
            return translated_text, romanized_text
    except Exception:
        pass
        
    # Standard fallback
    try:
        translator = GoogleTranslator(source=source_code, target=target_code)
        return translator.translate(text), ""
    except Exception as exc:
        return f"⚠️ Translation engine connection anomaly: {str(exc)}", ""

def execute_translation_pipeline(text, src_label, tgt_label):
    """Normalize language labels, run auto-transliteration if typing in Latin, and translate."""
    if not text.strip():
        return ""
    
    st.session_state.transliteration_preview = ""
    st.session_state.translated_romanization = ""
    text_to_translate = text
    source_code = "auto" if src_label == "Auto Detect" else supported_languages.get(src_label, "auto")
    
    # Smart Phonetic Input Transliteration:
    # If the user selected a non-Latin script language (like Hindi, Japanese, Russian) but typed in Latin letters:
    if src_label in NON_LATIN_ITCS and is_latin_script(text):
        transliterated = transliterate_to_native(text, src_label)
        if transliterated.strip().lower() != text.strip().lower():
            st.session_state.transliteration_preview = transliterated
            text_to_translate = transliterated
            source_code = supported_languages.get(src_label, "auto")
            
    target_code = supported_languages.get(tgt_label, "en")
    
    # Process translation and query pronunciation
    translated_result, romanization = translate_and_romanize(text_to_translate, source_code, target_code)
    st.session_state.translated_romanization = romanization
    return translated_result

# ==========================================
# 7. GRAPHICAL USER INTERFACE
# ==========================================

# Sidebar Dashboard Panel
with st.sidebar:
    st.markdown("""
    <div class="sidebar-avatar-section">
        <div class="pulsing-sunset-avatar">🌅</div>
        <h2 style='margin: 0; font-size: 1.5rem; font-weight: 700; color: #f8fafc;'>AuraTranslate</h2>
        <p style='margin: 4px 0 0 0; color: #ff4e50; font-size: 0.72rem; letter-spacing: 1.2px; font-weight: 600; text-transform: uppercase;'>Semantic Translation Tool</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 1: System Specs
    st.markdown("### 📊 Engine Status")
    st.markdown(f"""
    <div class="cyber-card">
        <strong>Engine:</strong> Google Translator API<br/>
        <strong>Supported Languages:</strong> {len(supported_languages)} Languages<br/>
        <strong>Transliteration:</strong> Multi-Script Autodetect 💫<br/>
        <strong>Status:</strong> Active & Online ✅
    </div>
    """, unsafe_allow_html=True)
    
    # Section 2: Recent Translation History
    st.markdown("### 📜 Translation Logs")
    if len(st.session_state.translation_history) > 0:
        for index, item in enumerate(reversed(st.session_state.translation_history[-5:])):
            st.markdown(f"""
            <div class="cyber-card" style="padding: 12px; margin-bottom: 12px; font-size: 0.85rem; border-color: rgba(255, 78, 80, 0.1);">
                <span style="color: #ff4e50; font-weight: 600;">{item['src_lang']} ➔ {item['tgt_lang']}</span><br/>
                <span style="color: #94a3b8; font-style: italic;">"{item['src_text'][:40]}..."</span><br/>
                <span style="color: #e2e8f0;">➡ "{item['tgt_text'][:40]}..."</span>
            </div>
            """, unsafe_allow_html=True)
            
        sidebar_col1, sidebar_col2 = st.columns(2)
        with sidebar_col1:
            if st.button("🗑️ Clear Logs", use_container_width=True):
                st.session_state.translation_history = []
                st.session_state.transliteration_preview = ""
                st.session_state.translated_romanization = ""
                st.rerun()
        with sidebar_col2:
            # Export logs
            export_text = "\n".join([
                f"[{log['time']}] {log['src_lang']} -> {log['tgt_lang']}\nInput: {log['src_text']}\nOutput: {log['tgt_text']}\n---"
                for log in st.session_state.translation_history
            ])
            st.download_button(
                label="📥 Export Logs",
                data=export_text,
                file_name="translation_history.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.markdown("_No translations processed yet in this session._")

# Main Screen Header Banner
st.markdown("""
<div class="translation-header">
    <span style="color: #ff4e50; font-weight: 600; font-size: 0.82rem; letter-spacing: 2px; text-transform: uppercase;">Instant Multi-Language System</span>
    <h1 class="app-title" style="margin-top: 5px;">AuroraTranslate Companion</h1>
    <p class="app-subtitle">Type standard text, or write foreign scripts using English keys. It translates and shows pronunciation!</p>
</div>
""", unsafe_allow_html=True)

# Grid Layout for Language Selectors and Swap button
lang_col1, lang_swap_col, lang_col2 = st.columns([9, 2, 9])

# Sort languages alphabetically for dropdown display
language_names_sorted = sorted(list(supported_languages.keys()))

with lang_col1:
    source_options = ["Auto Detect"] + language_names_sorted
    try:
        src_index = source_options.index(st.session_state.src_lang_selection)
    except ValueError:
        src_index = 0
        
    source_lang_box = st.selectbox(
        "Source Language 🌐",
        options=source_options,
        index=src_index,
        key="src_lang_selectbox_key"
    )
    st.session_state.src_lang_selection = source_lang_box

with lang_swap_col:
    st.markdown("<div class='swap-btn-container'>", unsafe_allow_html=True)
    if st.button("🔄 Swap", use_container_width=True, on_click=swap_languages_action, help="Swap source and target languages"):
        pass
    st.markdown("</div>", unsafe_allow_html=True)

with lang_col2:
    try:
        tgt_index = language_names_sorted.index(st.session_state.tgt_lang_selection)
    except ValueError:
        tgt_index = 0
        
    target_lang_box = st.selectbox(
        "Target Language 🎯",
        options=language_names_sorted,
        index=tgt_index,
        key="tgt_lang_selectbox_key"
    )
    st.session_state.tgt_lang_selection = target_lang_box

# Main Translation Panels
text_col1, text_col2 = st.columns(2)

with text_col1:
    st.markdown("### 📝 Input Text")
    input_value = st.text_area(
        "Enter text to translate here...",
        value=st.session_state.source_text_input,
        placeholder="Type here. (Tip: Try choosing 'Japanese' and typing 'arigatou' or 'Hindi' and typing 'dhanyawaad')...",
        height=200,
        label_visibility="collapsed",
        key="src_text_area_widget"
    )
    st.session_state.source_text_input = input_value
    
    char_count = len(input_value)
    st.markdown(f"<div class='char-count-text'>{char_count} / 5000 characters</div>", unsafe_allow_html=True)
    
    # Transliteration script preview
    if st.session_state.transliteration_preview:
        st.markdown(f"""
        <div class="cyber-card" style="padding: 14px; margin-top: 15px; border-color: rgba(255, 78, 80, 0.35); background: rgba(255, 78, 80, 0.05);">
            <strong style="color: #ff4e50; font-size: 0.82rem;">✨ Script Transliterated (Auto-Converted):</strong><br/>
            <span style="font-size: 1.1rem; color: #f8fafc; font-weight: 500;">{st.session_state.transliteration_preview}</span>
        </div>
        """, unsafe_allow_html=True)

with text_col2:
    st.markdown("### 🏆 Translated Text")
    output_container = st.empty()
    
    # Render read-only premium translation box
    translated_output_content = st.session_state.translated_text_output
    if translated_output_content:
        output_container.markdown(
            f'<div class="translated-display-box">{html.escape(translated_output_content)}</div>', 
            unsafe_allow_html=True
        )
        # Romanization/Pronunciation preview
        if st.session_state.translated_romanization:
            st.markdown(f"""
            <div style="margin-top: 10px; font-size: 0.95rem; color: #f9d425; font-style: italic; display: flex; align-items: center; gap: 6px;">
                🗣️ Pronunciation / Romaji: <strong style="color: #f8fafc;">{st.session_state.translated_romanization}</strong>
            </div>
            """, unsafe_allow_html=True)
    else:
        output_container.markdown(
            '<div class="translated-display-box" style="color:#64748b; font-style:italic;">Your translation will appear here...</div>', 
            unsafe_allow_html=True
        )
        
    # Render Utility Buttons (Copy/Speak) underneath target card if translation exists
    utility_placeholder = st.empty()
    if translated_output_content and not translated_output_content.startswith("⚠️"):
        # Resolve target language ISO code for speech synthesizer
        tgt_iso_code = supported_languages.get(st.session_state.tgt_lang_selection, "en")
        utility_placeholder.markdown(
            generate_translation_utilities_html(translated_output_content, tgt_iso_code, "output"), 
            unsafe_allow_html=True
        )

# Translate Action Buttons Layout
control_col1, control_col2, control_col3 = st.columns([3, 1, 1])

with control_col1:
    if st.button("🚀 Translate Text", type="primary", use_container_width=True):
        if not input_value.strip():
            st.warning("Please enter some text to translate first!")
        elif len(input_value) > 5000:
            st.error("Character limit exceeded! Please keep your text under 5000 characters.")
        else:
            with st.spinner("🌅 Connecting to translation matrix..."):
                translation_result = execute_translation_pipeline(
                    input_value, 
                    st.session_state.src_lang_selection, 
                    st.session_state.tgt_lang_selection
                )
                time.sleep(0.15) # Simulated network debounce latency
                
            st.session_state.translated_text_output = translation_result
            
            # Save transaction to logs history if successful
            if translation_result and not translation_result.startswith("⚠️"):
                st.session_state.translation_history.append({
                    "src_lang": st.session_state.src_lang_selection,
                    "tgt_lang": st.session_state.tgt_lang_selection,
                    "src_text": input_value,
                    "tgt_text": translation_result,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
            st.rerun()

with control_col2:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state.source_text_input = ""
        st.session_state.translated_text_output = ""
        st.session_state.transliteration_preview = ""
        st.session_state.translated_romanization = ""
        st.rerun()

# Quick Prompt Cards for Fast User testing
st.markdown("<br/><hr style='border-color:rgba(255,78,80,0.15);'/>", unsafe_allow_html=True)
st.markdown("### 💡 Quick Transliteration Demos (Click to Try)")
prompt_col1, prompt_col2, prompt_col3 = st.columns(3)

sample_sentences = [
    {"label": "🇯🇵 Type Japanese in English (arigatou)", "src": "Japanese", "tgt": "English", "text": "arigatou gozaimasu"},
    {"label": "🇮🇳 Type Hindi in English (dhanyawaad)", "src": "Hindi", "tgt": "English", "text": "dhanyawaad, aap kaise ho?"},
    {"label": "🇷🇺 Type Russian in English (spasibo)", "src": "Russian", "tgt": "English", "text": "spasibo bolshoye"}
]

with prompt_col1:
    if st.button(sample_sentences[0]["label"], use_container_width=True):
        st.session_state.source_text_input = sample_sentences[0]["text"]
        st.session_state.src_lang_selection = sample_sentences[0]["src"]
        st.session_state.tgt_lang_selection = sample_sentences[0]["tgt"]
        st.session_state.transliteration_preview = ""
        st.rerun()
with prompt_col2:
    if st.button(sample_sentences[1]["label"], use_container_width=True):
        st.session_state.source_text_input = sample_sentences[1]["text"]
        st.session_state.src_lang_selection = sample_sentences[1]["src"]
        st.session_state.tgt_lang_selection = sample_sentences[1]["tgt"]
        st.session_state.transliteration_preview = ""
        st.rerun()
with prompt_col3:
    if st.button(sample_sentences[2]["label"], use_container_width=True):
        st.session_state.source_text_input = sample_sentences[2]["text"]
        st.session_state.src_lang_selection = sample_sentences[2]["src"]
        st.session_state.tgt_lang_selection = sample_sentences[2]["tgt"]
        st.session_state.transliteration_preview = ""
        st.rerun()
