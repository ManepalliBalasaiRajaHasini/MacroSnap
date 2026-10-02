import base64
import re
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

from prompts import SYSTEM_PROMPT


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MacroSnap",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# GEMINI
# =========================================================

MODEL_NAME = "gemini-3.5-flash-lite"


@st.cache_resource
def get_client():

    api_key = st.secrets["GEMINI_API_KEY"]

    return genai.Client(
        api_key=api_key
    )


client = get_client()


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# =========================================================
# BACKGROUND IMAGE
# =========================================================

background_path = Path("assets/macrosnap-bg.png")


def get_background():

    if not background_path.exists():
        return ""

    image_bytes = background_path.read_bytes()

    encoded_image = base64.b64encode(
        image_bytes
    ).decode()

    return f"data:image/png;base64,{encoded_image}"


background_image = get_background()


# =========================================================
# PREMIUM GLASSMORPHISM CSS
# =========================================================

st.html(
f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);


/* =====================================================
   GLOBAL
   ===================================================== */

* {{
    box-sizing: border-box;
}}

html,
body {{
    margin: 0;
    padding: 0;
}}

.stApp {{

    min-height: 100vh;

    background-image:
        linear-gradient(
            rgba(0, 18, 15, 0.63),
            rgba(0, 13, 11, 0.82)
        ),
        url("{background_image}");

    background-size: cover;

    background-position: center;

    background-attachment: fixed;

    font-family: 'Inter', sans-serif;
}}


/* =====================================================
   BACKGROUND LIGHTING
   ===================================================== */

.stApp::before {{

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    background:

        radial-gradient(
            circle at 15% 18%,
            rgba(52, 211, 153, 0.16),
            transparent 27%
        ),

        radial-gradient(
            circle at 85% 18%,
            rgba(45, 212, 191, 0.14),
            transparent 27%
        ),

        radial-gradient(
            circle at 50% 85%,
            rgba(59, 130, 246, 0.08),
            transparent 32%
        );

    z-index: 0;
}}


/* =====================================================
   MAIN CONTAINER
   ===================================================== */

.block-container {{

    max-width: 1120px !important;

    padding-top: 22px !important;

    padding-bottom: 35px !important;

    position: relative;

    z-index: 2;
}}


/* =====================================================
   STREAMLIT HEADER
   ===================================================== */

header[data-testid="stHeader"] {{
    background: transparent !important;
}}

[data-testid="stToolbar"] {{
    visibility: hidden;
}}


/* =====================================================
   TEXT
   ===================================================== */

.stMarkdown,
.stMarkdown p,
.stMarkdown span,
.stMarkdown li,
.stText,
.stCaption {{
    color: #eefaf6 !important;
}}

h1,
h2,
h3,
h4,
h5,
h6 {{
    color: #ffffff !important;
}}


/* =====================================================
   HERO
   ===================================================== */

.hero {{

    padding: 28px 34px 30px;

    border-radius: 28px;

    background:
        linear-gradient(
            135deg,
            rgba(4, 53, 43, 0.74),
            rgba(1, 25, 21, 0.53)
        );

    border:
        1px solid rgba(137, 255, 224, 0.18);

    box-shadow:

        0 25px 70px
        rgba(0,0,0,0.42),

        0 0 45px
        rgba(35,220,165,0.07),

        inset 0 1px 0
        rgba(255,255,255,0.13);

    backdrop-filter: blur(18px);

    -webkit-backdrop-filter: blur(18px);

    position: relative;

    overflow: hidden;
}}


.hero::before {{

    content: "";

    position: absolute;

    top: 0;

    left: 8%;

    right: 8%;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.42),
            transparent
        );

    opacity: 0.8;
}}


.hero::after {{

    content: "";

    position: absolute;

    width: 320px;

    height: 320px;

    right: -120px;

    top: -160px;

    border-radius: 50%;

    background:
        rgba(52,211,153,0.14);

    filter: blur(65px);

    pointer-events: none;
}}


/* =====================================================
   BRAND
   ===================================================== */

.brand-row {{

    display: flex;

    align-items: center;

    gap: 10px;

    position: relative;

    z-index: 2;
}}


.brand-icon {{

    width: 42px;

    height: 42px;

    border-radius: 12px;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 21px;

    background:
        linear-gradient(
            135deg,
            #32e89a,
            #12b886
        );

    box-shadow:
        0 8px 25px
        rgba(16,185,129,0.35),

        0 0 18px
        rgba(52,211,153,0.15);
}}


.brand-name {{

    font-size: 18px;

    font-weight: 800;

    color: white !important;
}}


.brand-name span {{

    color: #35e89a !important;
}}


.brand-line {{

    color: #71968a !important;

    font-size: 18px;

    margin: 0 3px;
}}


.brand-subtitle {{

    color: #b6ccc4 !important;

    font-size: 12px;

    font-weight: 600;
}}


/* =====================================================
   HERO TITLE
   ===================================================== */

.hero-title {{

    position: relative;

    z-index: 2;

    margin-top: 22px;

    font-size: 43px;

    line-height: 1.04;

    font-weight: 800;

    letter-spacing: -1.8px;

    color: white !important;
}}


.hero-title span {{

    background:
        linear-gradient(
            90deg,
            #35e89a,
            #42e59a,
            #63d8ee
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;
}}


.hero-description {{

    position: relative;

    z-index: 2;

    max-width: 650px;

    margin-top: 12px;

    color: #bdd1ca !important;

    font-size: 13px;

    line-height: 1.65;
}}


/* =====================================================
   BADGES
   ===================================================== */

.badges {{

    display: flex;

    flex-wrap: wrap;

    gap: 8px;

    margin-top: 17px;

    position: relative;

    z-index: 2;
}}


.badge {{

    padding: 7px 12px;

    border-radius: 999px;

    background:
        rgba(1, 40, 33, 0.70);

    border:
        1px solid rgba(130,255,220,0.14);

    color: #e7f8f2 !important;

    font-size: 10px;

    font-weight: 700;

    backdrop-filter: blur(12px);

    box-shadow:
        0 0 15px
        rgba(35,220,165,0.04),

        inset 0 1px 0
        rgba(255,255,255,0.08);
}}


/* =====================================================
   SECTION TITLES
   ===================================================== */

.section-title {{

    color: white !important;

    font-size: 19px;

    font-weight: 800;

    margin-top: 20px;

    margin-bottom: 4px;
}}


.section-description {{

    color: #9eb6ad !important;

    font-size: 11px;

    margin-bottom: 12px;
}}


/* =====================================================
   GLASS CARD
   ===================================================== */

.glass-card {{

    padding: 18px 20px;

    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            rgba(20, 75, 63, 0.58),
            rgba(3, 31, 27, 0.48)
        );

    border:
        1px solid rgba(130, 255, 220, 0.20);

    box-shadow:

        0 12px 35px
        rgba(0, 0, 0, 0.30),

        0 0 25px
        rgba(35, 220, 165, 0.07),

        inset 0 1px 0
        rgba(255, 255, 255, 0.15);

    backdrop-filter: blur(20px);

    -webkit-backdrop-filter: blur(20px);

    margin-bottom: 10px;

    position: relative;

    overflow: hidden;
}}


.glass-card::before {{

    content: "";

    position: absolute;

    top: 0;

    left: 8%;

    right: 8%;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.42),
            transparent
        );

    opacity: 0.75;
}}


.card-heading {{

    color: white !important;

    font-size: 14px;

    font-weight: 750;

    margin-bottom: 5px;
}}


.card-text {{

    color: #a9c1b8 !important;

    font-size: 11px;

    line-height: 1.55;
}}


/* =====================================================
   FILE UPLOADER
   ===================================================== */

[data-testid="stFileUploader"] {{
    margin-top: 8px;
}}


[data-testid="stFileUploaderDropzone"] {{

    min-height: 120px !important;

    background:
        linear-gradient(
            135deg,
            rgba(5, 52, 43, 0.65),
            rgba(1, 29, 25, 0.52)
        ) !important;

    border:
        1px dashed
        rgba(52,211,153,0.55) !important;

    border-radius: 18px !important;

    backdrop-filter: blur(16px);

    box-shadow:

        0 10px 30px
        rgba(0,0,0,0.22),

        inset 0 1px 0
        rgba(255,255,255,0.10);

    padding: 14px !important;
}}


[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {{
    color: #d5e9e2 !important;
}}


[data-testid="stFileUploaderDropzone"] button {{

    background:
        rgba(255,255,255,0.08) !important;

    color: #dff8ef !important;

    border:
        1px solid rgba(255,255,255,0.16) !important;

    border-radius: 10px !important;
}}


/* =====================================================
   IMAGE
   ===================================================== */

[data-testid="stImage"] img {{

    border-radius: 17px !important;

    border:
        1px solid rgba(255,255,255,0.13);

    box-shadow:

        0 15px 40px
        rgba(0,0,0,0.35),

        0 0 25px
        rgba(35,220,165,0.06);
}}


/* =====================================================
   BUTTON
   ===================================================== */

.stButton > button {{

    width: 100%;

    min-height: 43px;

    border: none !important;

    border-radius: 14px !important;

    background:
        linear-gradient(
            90deg,
            #36e69b,
            #1ed6a0
        ) !important;

    color: #02251b !important;

    font-size: 12px !important;

    font-weight: 800 !important;

    box-shadow:

        0 10px 28px
        rgba(16,185,129,0.24),

        0 0 18px
        rgba(52,211,153,0.10);

    transition: all 0.2s ease;
}}


.stButton > button:hover {{

    transform: translateY(-2px);

    box-shadow:

        0 15px 35px
        rgba(16,185,129,0.38),

        0 0 25px
        rgba(52,211,153,0.14);
}}


/* =====================================================
   CHAT MESSAGE
   ===================================================== */

[data-testid="stChatMessage"] {{

    background:
        rgba(2, 35, 30, 0.58) !important;

    border:
        1px solid rgba(130,255,220,0.12) !important;

    border-radius: 16px !important;

    padding: 9px 12px !important;

    margin-bottom: 7px !important;

    backdrop-filter: blur(15px);

    box-shadow:
        0 8px 25px
        rgba(0,0,0,0.18),

        inset 0 1px 0
        rgba(255,255,255,0.08);
}}


[data-testid="stChatMessage"] .stMarkdown,
[data-testid="stChatMessage"] .stMarkdown p,
[data-testid="stChatMessage"] .stMarkdown span {{
    color: #edf9f5 !important;

    font-size: 12px !important;
}}


/* =====================================================
   CHAT INPUT
   ===================================================== */

.stChatInput > div {{

    background:
        rgba(1, 31, 27, 0.82) !important;

    border:
        1px solid
        rgba(52,211,153,0.30) !important;

    border-radius: 17px !important;

    box-shadow:

        0 10px 30px
        rgba(0,0,0,0.30),

        0 0 20px
        rgba(35,220,165,0.05) !important;
}}


.stChatInput textarea {{

    color: white !important;

    background: transparent !important;

    caret-color: #35e89a !important;

    font-size: 12px !important;
}}


.stChatInput textarea::placeholder {{
    color: #78958b !important;
}}


/* =====================================================
   ANALYSIS WRAPPER
   ===================================================== */

.analysis-wrapper {{

    padding: 17px;

    border-radius: 21px;

    background:
        linear-gradient(
            135deg,
            rgba(5,43,35,0.70),
            rgba(1,26,22,0.52)
        );

    border:
        1px solid rgba(130,255,220,0.17);

    box-shadow:

        0 20px 50px
        rgba(0,0,0,0.28),

        0 0 25px
        rgba(35,220,165,0.05),

        inset 0 1px 0
        rgba(255,255,255,0.12);

    backdrop-filter: blur(18px);

    margin-top: 10px;
}}


/* =====================================================
   DETECTED MEAL
   ===================================================== */

.detected-meal {{

    display: flex;

    align-items: center;

    gap: 13px;

    padding: 12px;

    border-radius: 15px;

    background:
        rgba(255,255,255,0.045);

    border:
        1px solid rgba(255,255,255,0.08);
}}


.meal-icon {{

    width: 43px;

    height: 43px;

    border-radius: 13px;

    display: flex;

    align-items: center;

    justify-content: center;

    background:
        linear-gradient(
            135deg,
            #39e6a0,
            #0d9488
        );

    font-size: 20px;

    box-shadow:
        0 8px 22px
        rgba(16,185,129,0.20);
}}


.meal-label {{

    color: #6fe5ae !important;

    font-size: 9px;

    text-transform: uppercase;

    letter-spacing: 1px;

    font-weight: 800;
}}


.meal-name {{

    color: white !important;

    font-size: 13px;

    font-weight: 700;

    margin-top: 3px;
}}


/* =====================================================
   METRIC CARDS
   ===================================================== */

.metric-card {{

    min-height: 105px;

    padding: 14px;

    border-radius: 17px;

    background:
        linear-gradient(
            145deg,
            rgba(20, 75, 63, 0.62),
            rgba(3, 30, 27, 0.48)
        );

    border:
        1px solid rgba(120, 255, 220, 0.18);

    box-shadow:

        0 12px 30px
        rgba(0,0,0,0.28),

        0 0 20px
        rgba(35,220,165,0.06),

        inset 0 1px 0
        rgba(255,255,255,0.12);

    backdrop-filter: blur(16px);

    position: relative;

    overflow: hidden;
}}


.metric-card::before {{

    content: "";

    position: absolute;

    top: 0;

    left: 12%;

    right: 12%;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.35),
            transparent
        );
}}


.metric-icon {{
    font-size: 19px;
    margin-bottom: 5px;
}}


.metric-label {{

    color: #9eb6ad !important;

    font-size: 9px;

    text-transform: uppercase;

    letter-spacing: 0.7px;

    font-weight: 800;
}}


.metric-value {{

    color: white !important;

    font-size: 22px;

    font-weight: 800;

    margin-top: 3px;
}}


.metric-unit {{

    color: #8fa9a0 !important;

    font-size: 9px;

    font-weight: 600;
}}


/* =====================================================
   SUMMARY
   ===================================================== */

.summary-card {{

    margin-top: 10px;

    padding: 13px 15px;

    border-radius: 16px;

    background:
        linear-gradient(
            90deg,
            rgba(20,184,166,0.12),
            rgba(52,211,153,0.05)
        );

    border:
        1px solid rgba(52,211,153,0.15);

    box-shadow:
        0 10px 25px
        rgba(0,0,0,0.15),

        inset 0 1px 0
        rgba(255,255,255,0.08);
}}


.summary-label {{

    color: #71e6b0 !important;

    font-size: 9px;

    text-transform: uppercase;

    letter-spacing: 1px;

    font-weight: 800;

    margin-bottom: 5px;
}}


.summary-text {{

    color: #bdd1c9 !important;

    font-size: 11px;

    line-height: 1.55;
}}


/* =====================================================
   FEATURES
   ===================================================== */

.feature-card {{

    min-height: 105px;

    padding: 15px 10px;

    border-radius: 17px;

    background:
        linear-gradient(
            145deg,
            rgba(10, 51, 43, 0.68),
            rgba(2, 28, 25, 0.58)
        );

    border:
        1px solid rgba(130,255,220,0.13);

    text-align: center;

    backdrop-filter: blur(15px);

    box-shadow:

        0 12px 30px
        rgba(0,0,0,0.20),

        0 0 18px
        rgba(35,220,165,0.04),

        inset 0 1px 0
        rgba(255,255,255,0.10);

    position: relative;

    overflow: hidden;
}}


.feature-card::before {{

    content: "";

    position: absolute;

    top: 0;

    left: 15%;

    right: 15%;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.30),
            transparent
        );
}}


.feature-icon {{

    font-size: 22px;

    margin-bottom: 5px;
}}


.feature-title {{

    color: white !important;

    font-size: 12px;

    font-weight: 750;
}}


.feature-text {{

    color: #829b91 !important;

    font-size: 9px;

    line-height: 1.4;

    margin-top: 4px;
}}


/* =====================================================
   DIVIDER
   ===================================================== */

.divider {{

    height: 1px;

    margin: 24px 0 18px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(130,255,220,0.18),
            transparent
        );
}}


/* =====================================================
   CENTER CLEAR BUTTON
   ===================================================== */

.clear-button-wrapper {{

    display: flex;

    justify-content: center;

    width: 100%;
}}


/* =====================================================
   FOOTER
   ===================================================== */

.footer {{

    text-align: center;

    padding-top: 22px;

    color: #718a81 !important;

    font-size: 9px;

    line-height: 1.6;
}}


/* =====================================================
   MOBILE
   ===================================================== */

@media (max-width: 768px) {{

    .block-container {{
        padding-left: 12px !important;
        padding-right: 12px !important;
    }}

    .hero {{
        padding: 23px;
    }}

    .hero-title {{
        font-size: 34px;
    }}

}}

</style>
"""
)


# =========================================================
# HERO
# =========================================================

st.html(
"""
<div class="hero">

    <div class="brand-row">

        <div class="brand-icon">
            🥗
        </div>

        <div class="brand-name">
            Macro<span>Snap</span>
        </div>

        <div class="brand-line">
            |
        </div>

        <div class="brand-subtitle">
            AI Nutrition Buddy
        </div>

    </div>


    <div class="hero-title">

        Snap your meal.<br>

        <span>Know what you eat.</span>

    </div>


    <div class="hero-description">

        Turn a simple meal photo into an instant nutrition estimate.
        MacroSnap uses AI vision to identify your food and estimate
        calories, protein, carbohydrates and fat.

    </div>


    <div class="badges">

        <div class="badge">
            📸 AI Vision
        </div>

        <div class="badge">
            🔥 Calories
        </div>

        <div class="badge">
            💪 Protein
        </div>

        <div class="badge">
            🌿 Macros
        </div>

        <div class="badge">
            💬 AI Chat
        </div>

    </div>

</div>
"""
)


# =========================================================
# MAIN TWO COLUMNS
# =========================================================

left_col, right_col = st.columns(
    [1, 1],
    gap="medium"
)


# =========================================================
# MEAL ANALYZER
# =========================================================

with left_col:

    st.html(
    """
    <div class="section-title">
        📸 Meal Analyzer
    </div>

    <div class="section-description">
        Upload a photo of your food and let MacroSnap analyze it.
    </div>

    <div class="glass-card">

        <div class="card-heading">
            Upload your meal
        </div>

        <div class="card-text">
            Add a clear photo of your meal.
            MacroSnap will identify the food and estimate its nutrition.
        </div>

    </div>
    """
    )


    uploaded_file = st.file_uploader(
        "Upload meal image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        label_visibility="collapsed"
    )


    if uploaded_file:

        st.image(
            uploaded_file,
            use_container_width=True
        )


        if st.button(
            "✨  Analyze My Meal",
            key="analyze_meal"
        ):

            with st.spinner(
                "🤖 MacroSnap is analyzing your meal..."
            ):

                try:

                    image_bytes = uploaded_file.getvalue()


                    analysis_prompt = """
Analyze this meal image and return the result exactly in this format:

MEAL: [food items]

CALORIES: [number] kcal

PROTEIN: [number] g

CARBS: [number] g

FAT: [number] g

SUMMARY: [short 1-2 sentence nutrition summary]

Important:
- These are estimates.
- If portion size is unclear, mention that values may vary.
- Do not give medical advice.
"""


                    response = client.models.generate_content(
                        model=MODEL_NAME,

                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type=uploaded_file.type
                            ),
                            analysis_prompt
                        ]
                    )


                    result = response.text


                    st.session_state.analysis_result = result


                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "content":
                                "📸 I uploaded a meal photo for analysis."
                        }
                    )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": result
                        }
                    )


                    st.rerun()


                except Exception as e:

                    st.error(
                        "Unable to analyze the image right now."
                    )

                    st.caption(
                        str(e)
                    )


# =========================================================
# AI CHAT
# =========================================================

with right_col:

    st.html(
    """
    <div class="section-title">
        🤖 AI Nutrition Chat
    </div>

    <div class="section-description">
        Ask MacroSnap anything about your meal or nutrition.
    </div>

    <div class="glass-card">

        <div class="card-heading">
            Chat with MacroSnap
        </div>

        <div class="card-text">
            Try asking:
            "Is this a balanced meal?"
            or
            "How can I increase my protein?"
        </div>

    </div>
    """
    )


    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    user_input = st.chat_input(
        "Ask MacroSnap about food or nutrition..."
    )


    if user_input:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )


        with st.chat_message("user"):

            st.markdown(
                user_input
            )


        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    conversation = ""

                    for message in st.session_state.messages:

                        conversation += (
                            message["role"].upper()
                            + ": "
                            + message["content"]
                            + "\n\n"
                        )


                    prompt = f"""
{SYSTEM_PROMPT}

Conversation so far:

{conversation}

Reply naturally as MacroSnap.

Keep the answer:
- friendly
- simple
- useful
- concise

Only discuss food, nutrition and fitness.
"""


                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt
                    )


                    answer = response.text


                    st.markdown(
                        answer
                    )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )


                except Exception as e:

                    st.error(
                        "MacroSnap could not respond right now."
                    )

                    st.caption(
                        str(e)
                    )


# =========================================================
# NUTRITION ANALYSIS
# =========================================================

if st.session_state.analysis_result:

    result = st.session_state.analysis_result


    # -----------------------------------------------------
    # EXTRACT VALUES
    # -----------------------------------------------------

    meal_match = re.search(
        r"MEAL:\s*(.*)",
        result,
        re.IGNORECASE
    )

    calories_match = re.search(
        r"CALORIES:\s*([\d,]+)",
        result,
        re.IGNORECASE
    )

    protein_match = re.search(
        r"PROTEIN:\s*([\d.]+)",
        result,
        re.IGNORECASE
    )

    carbs_match = re.search(
        r"CARBS:\s*([\d.]+)",
        result,
        re.IGNORECASE
    )

    fat_match = re.search(
        r"FAT:\s*([\d.]+)",
        result,
        re.IGNORECASE
    )

    summary_match = re.search(
        r"SUMMARY:\s*(.*)",
        result,
        re.IGNORECASE
    )


    meal = (
        meal_match.group(1).strip()
        if meal_match
        else "Meal detected"
    )


    calories = (
        calories_match.group(1)
        if calories_match
        else "--"
    )


    protein = (
        protein_match.group(1)
        if protein_match
        else "--"
    )


    carbs = (
        carbs_match.group(1)
        if carbs_match
        else "--"
    )


    fat = (
        fat_match.group(1)
        if fat_match
        else "--"
    )


    summary = (
        summary_match.group(1).strip()
        if summary_match
        else
        "Nutrition values are estimated and may vary based on portion size."
    )


    # =====================================================
    # TITLE
    # =====================================================

    st.html(
    """
    <div class="divider"></div>

    <div class="section-title">
        📊 Nutrition Analysis
    </div>

    <div class="section-description">
        AI-generated nutrition estimates based on your meal photo.
    </div>
    """
    )


    # =====================================================
    # DETECTED MEAL
    # =====================================================

    st.html(
    f"""
    <div class="analysis-wrapper">

        <div class="detected-meal">

            <div class="meal-icon">
                🍽️
            </div>

            <div>

                <div class="meal-label">
                    Detected Meal
                </div>

                <div class="meal-name">
                    {meal}
                </div>

            </div>

        </div>

    </div>
    """
    )


    # =====================================================
    # METRIC CARDS
    # =====================================================

    m1, m2, m3, m4 = st.columns(
        4,
        gap="small"
    )


    with m1:

        st.html(
        f"""
        <div class="metric-card">

            <div class="metric-icon">
                🔥
            </div>

            <div class="metric-label">
                Calories
            </div>

            <div class="metric-value">
                {calories}
                <span class="metric-unit">
                    kcal
                </span>
            </div>

        </div>
        """
        )


    with m2:

        st.html(
        f"""
        <div class="metric-card">

            <div class="metric-icon">
                💪
            </div>

            <div class="metric-label">
                Protein
            </div>

            <div class="metric-value">
                {protein}
                <span class="metric-unit">
                    g
                </span>
            </div>

        </div>
        """
        )


    with m3:

        st.html(
        f"""
        <div class="metric-card">

            <div class="metric-icon">
                🍚
            </div>

            <div class="metric-label">
                Carbs
            </div>

            <div class="metric-value">
                {carbs}
                <span class="metric-unit">
                    g
                </span>
            </div>

        </div>
        """
        )


    with m4:

        st.html(
        f"""
        <div class="metric-card">

            <div class="metric-icon">
                🥑
            </div>

            <div class="metric-label">
                Fat
            </div>

            <div class="metric-value">
                {fat}
                <span class="metric-unit">
                    g
                </span>
            </div>

        </div>
        """
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    st.html(
    f"""
    <div class="summary-card">

        <div class="summary-label">
            📋 Nutrition Summary
        </div>

        <div class="summary-text">
            {summary}
        </div>

    </div>
    """
    )


# =========================================================
# FEATURES
# =========================================================

st.html(
"""
<div class="divider"></div>

<div class="section-title">
    ✨ What MacroSnap can do
</div>

<div class="section-description">
    Simple AI-powered nutrition assistance in one place.
</div>
"""
)


f1, f2, f3, f4 = st.columns(
    4,
    gap="small"
)


with f1:

    st.html(
    """
    <div class="feature-card">

        <div class="feature-icon">
            📸
        </div>

        <div class="feature-title">
            AI Vision
        </div>

        <div class="feature-text">
            Understand meals from photos.
        </div>

    </div>
    """
    )


with f2:

    st.html(
    """
    <div class="feature-card">

        <div class="feature-icon">
            🔥
        </div>

        <div class="feature-title">
            Calories
        </div>

        <div class="feature-text">
            Get estimated calorie values.
        </div>

    </div>
    """
    )


with f3:

    st.html(
    """
    <div class="feature-card">

        <div class="feature-icon">
            💪
        </div>

        <div class="feature-title">
            Macronutrients
        </div>

        <div class="feature-text">
            Protein, carbs and fat estimates.
        </div>

    </div>
    """
    )


with f4:

    st.html(
    """
    <div class="feature-card">

        <div class="feature-icon">
            💬
        </div>

        <div class="feature-title">
            AI Chat
        </div>

        <div class="feature-text">
            Ask nutrition questions naturally.
        </div>

    </div>
    """
    )


# =========================================================
# CLEAR CONVERSATION - CENTER
# =========================================================

st.html(
"""
<div class="divider"></div>
"""
)


left_space, center_button, right_space = st.columns(
    [1, 1, 1]
)


with center_button:

    if st.button(
        "🗑️  Clear Conversation",
        key="clear_conversation"
    ):

        st.session_state.messages = []

        st.session_state.analysis_result = None

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.html(
"""
<div class="footer">

    🥗 <b>MacroSnap</b>
    &nbsp; • &nbsp;
    AI Nutrition Buddy

    <br>

    Nutrition estimates are for informational purposes only
    and should not be treated as medical advice.

</div>
"""
)