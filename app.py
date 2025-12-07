# Install the library when the script starts
import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package('openai')

import openai 
# ... rest of your Streamlit code follows ...
import streamlit as st
import openai
import json
import os
from dotenv import load_dotenv
load_dotenv()
st.markdown("""
<style>
div.stButton > button[kind="secondary"] {
    background-color: #d3d3d3 !important;
    color: black;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)
client = openai.OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.x.ai/v1"
)
MODEL = "grok-4-1-fast-reasoning"
MEMORY_FILE = "memory.json"
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)
def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)
def save_memory(new_cuts):
    memory = load_memory()
    memory.extend(new_cuts)
    memory = memory[-20:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)
system_prompt = """You are Step Five. Apply Elon's exact 5-step algorithm thoughtfully and logically:
1. Question every requirement (explain why it might not be needed)
2. Delete only parts or processes that are truly unnecessary (justify each deletion)
3. Simplify what remains while keeping the process effective
4. Accelerate cycle time without sacrificing quality
5. Automate where it makes sense
Previous accepted cuts (apply these first, but only if they still make sense):
{prev_cuts}
First identify the main software/tool mentioned (e.g., Google Sheets). If multiple, list the primary one first. If none, say "No specific software detected".
Be logical and balanced. Never remove a step just to reduce count or for aesthetics. Preserve anything needed for safety, compliance, accuracy, or auditability. Question aggressively but delete conservatively with clear justification. Prioritize effectiveness and correctness over brevity. A good SOP is short but never incomplete.
Ensure the optimized SOP includes detailed tool-based information for beginners and AI agents with no prior knowledge. Do not assume familiarity with tools; explain specific steps on how to use them explicitly. Keep all essential tool details to help mimic human work accurately. Avoid vagueness at all costs; make every step understandable on first read for novices and experts alike.
Return ONLY markdown with these sections:
### New SOP
[optimized SOP only]
### Reasoning
Bullet list explaining every change with justification.
### Software tips & automations
- 3-5 uncommon but high-impact shortcuts/features (built-in or free add-ons only)
- 1-2 realistic automation ideas (built-in tools, free add-ons, or simple scripts)
### Estimated time saved
X% (conservative realistic estimate for an experienced user)
### Summary
One sentence.
### References
List any external sources or references used in this optimization (e.g., URLs, books, articles). If none, say "None"."""
st.markdown("<h1 style='text-align: center; margin-bottom: 5px; text-decoration: underline;'>STEP 5</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; margin-top: 0px;'>Apply Elon's Algorithm to any Standard Operating Procedure</p>", unsafe_allow_html=True)
sop = st.text_area("", height=300, placeholder="Paste any SOP here (Example: Set up new hires with access and training...)")
if st.button("Apply The Algorithm", type="primary"):
    if not sop.strip():
        st.error("Paste something first")
    else:
        with st.spinner("Algorizzing..."):
            prev = load_memory()
            prev_text = "\n".join(prev[-10:]) if prev else "None"
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt.format(prev_cuts=prev_text)},
                    {"role": "user", "content": sop}
                ],
                temperature=0.2,
                max_tokens=2048
            )
            result = response.choices[0].message.content
            # Parse sections
            sections = {
                "New SOP": [],
                "Reasoning": [],
                "Software tips & automations": [],
                "Estimated time saved": [],
                "Summary": [],
                "References": []
            }
            current = None
            for line in result.split("\n"):
                if line.startswith("### "):
                    current = line[4:].strip()
                elif current in sections:
                    sections[current].append(line)
            # Centered New SOP header
            st.markdown("<h1 style='text-align: center; margin-top: 40px; margin-bottom: 0px;'><strong>📝 New SOP</strong></h1>", unsafe_allow_html=True)
            st.markdown("<hr style='border-top: 3px solid white; width: 60%; margin: auto; margin-bottom: 30px;'>", unsafe_allow_html=True)
            new_sop_text = "\n".join(sections["New SOP"])
            if new_sop_text.strip():
                st.markdown(new_sop_text)
            else:
                st.markdown("No optimized SOP returned")
            # Expander for details
            with st.expander("Show Reasoning, Software Tips, Estimated Time Saved, and Summary"):
                if sections["Reasoning"]:
                    st.markdown("### Reasoning")
                    st.markdown("\n".join(sections["Reasoning"]))
                if sections["Software tips & automations"]:
                    st.markdown("### Software tips & automations")
                    st.markdown("\n".join(sections["Software tips & automations"]))
                if sections["Estimated time saved"]:
                    st.markdown("### Estimated time saved")
                    st.markdown("\n".join(sections["Estimated time saved"]))
                if sections["Summary"]:
                    st.markdown("### Summary")
                    st.markdown("\n".join(sections["Summary"]))
                if sections["References"]:
                    st.markdown("### References")
                    st.markdown("\n".join(sections["References"]))
        # Accept button
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            if st.button("✅ Accept this version & refine similar SOPs in the future", key="accept_button", type="secondary"):
                cuts = [line.strip() for line in result.split("\n") if any(word in line.lower() for word in ["deleted", "removed", "unnecessary"])]
                save_memory(cuts)
                st.success("Memory updated")
