import streamlit as st
import pickle
import numpy as np
import pandas as pd

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BURN: Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. LOAD YOUR MODEL ---
@st.cache_resource
def load_model():
    """Loads the saved XGBoost model from model.pkl"""
    try:
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.error("FATAL ERROR: 'model.pkl' not found. Run your notebook to create it.")
        return None
    except Exception as e:
        st.error(f"An error occurred loading the model: {e}")
        return None

model = load_model()

# --- 3. CUSTOM CSS (THE "PRO STUDIO" DESIGN) ---
css = """
<style>
    /* Base */
    .stApp {
        background-color: #0A0A0A; /* Almost Black */
        color: #FAFAFA;
    }
    
    [data-testid="stSidebar"] { display: none; }

    /* Titles */
    h1 { color: #FAFAFA; font-weight: 700; }
    h2, h3 {
        color: #007AFF;  /* Pro Blue Accent */
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Main "Hero" Metric */
    div[data-testid="stMetric"]:first-child [data-testid="stMetricValue"] {
        font-size: 7.5rem;
        color: #007AFF; /* Pro Blue */
        font-weight: 900;
        line-height: 1;
    }
    div[data-testid="stMetric"]:first-child [data-testid="stMetricLabel"] {
        font-size: 1.5rem;
        color: #FAFAFA;
        text-transform: uppercase;
    }

    /* Secondary Metrics */
    div[data-testid="stMetric"]:not(:first-child) [data-testid="stMetricValue"] {
        font-size: 4rem;
        color: #FAFAFA;
        font-weight: 700;
    }
    div[data-testid="stMetric"]:not(:first-child) [data-testid="stMetricLabel"] {
        font-size: 1.25rem;
        color: #FAFAFA;
        text-transform: uppercase;
    }

    /* Primary Button */
    [data-testid="stButton"] > button {
        background-color: #007AFF;
        color: #FFFFFF;
        font-size: 1.1rem;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        width: 100%;
    }
    [data-testid="stButton"] > button:hover {
        background-color: #FFFFFF;
        color: #007AFF;
    }

    /* Coach's Feedback Box */
    [data-testid="stInfo"] {
        background-color: rgba(0, 122, 255, 0.1);
        border: 1px solid #007AFF;
        border-radius: 8px;
        font-size: 1.1rem;
        color: #FAFAFA;
    }
    
    [data-testid="stTooltipIcon"] { color: #007AFF; }

    .st-emotion-cache-183lzff {
        background-color: #1A1A1A;
        border-radius: 8px;
        padding: 1.5rem;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- 4. SESSION STATE (To hold the results) ---
if "results" not in st.session_state:
    st.session_state.results = None

# --- 5. COACH'S FEEDBACK FUNCTION ---
def get_coaching_message(calories):
    """Gives refined, professional feedback."""
    calories = int(calories)
    if calories < 100:
        return f"Warm-up complete: {calories} kcal. A solid start to the session."
    elif calories < 300:
        return f"Solid work: {calories} kcal. You're building a strong foundation. That's a productive session."
    elif calories < 500:
        return f"Performance Zone: {calories} kcal. 🔥 You're pushing your limits and making significant progress."
    else:
        return f"Peak Output: {calories} kcal. 🚀 An elite-level session. Focus on recovery."

# --- 6. THE INTERFACE (Single-Column Layout) ---

# 1. The Header Image
try:
    st.image('header_image.jpg', use_container_width=True)
except FileNotFoundError:
    st.warning("`header_image.jpg` not found. Add it to your folder to see the header!")

st.title("BURN: STUDIO ⚡")

# 2. SECTION 1: LOG YOUR SESSION (Full Width)
with st.container():
    st.header("Log Your Session")
    
    with st.container(border=True):
        
        # --- THIS IS THE NEW 3-COLUMN LAYOUT ---
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1:
            st.subheader("Bio")
            Gender_input = st.selectbox("Gender", ('male', 'female'), index=0)
            Age = st.number_input("Age (Years)", min_value=10, max_value=100, value=30, step=1)

        with col2:
            st.subheader("Metrics")
            Height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
            Weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
        
        with col3:
            st.subheader("Performance")
            Duration = st.slider("Workout Duration (min)", 1, 180, 45)
            Heart_Rate = st.slider("Avg Heart Rate (bpm)", 60, 220, 140, 
                help="Your Average Heart Rate (BPM) is the *single most important* predictor of calorie burn. Find this on your watch, fitness tracker, or cardio machine."
            )
            Body_Temp = st.slider("Body Temp (°C)", 35.0, 45.0, 40.0, 0.1,
                help="Your core body temperature during exercise."
            )
    
    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    # 3. The "Analyze" Button (Full Width)
    if st.button("Analyze Performance", use_container_width=True):
        if model:
            Gender = 0 if Gender_input == 'male' else 1
            input_data = [[Gender, Age, Height, Weight, Duration, Heart_Rate, Body_Temp]]
            input_df = pd.DataFrame(input_data, columns=[
                'Gender', 'Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp'
            ])
            
            try:
                prediction = model.predict(input_df)
                calories_burned = prediction[0]
                message = get_coaching_message(calories_burned)
                
                st.session_state.results = {
                    "calories": calories_burned,
                    "duration": Duration,
                    "heart_rate": Heart_Rate,
                    "message": message
                }
                st.balloons()
            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")
        else:
            st.error("Model not loaded. Please restart the app.")

# --- 4. SECTION 2: YOUR PERFORMANCE (Full Width) ---
st.divider()
st.header("Your Performance")

# This is the clear, high-impact results layout
with st.container(border=True):
    if st.session_state.results:
        r = st.session_state.results
        
        # HERO METRIC (Full Width)
        st.metric(label="Total Calories Burned", value=f"{r['calories']:.0f} kcal")
        
        st.divider()
        
        # SUPPORTING METRICS (50/50 Split)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Workout Duration", value=f"{r['duration']} min")
        with col2:
            st.metric(label="Avg Heart Rate", value=f"{r['heart_rate']} bpm")
        
        st.divider()
        
        # COACH'S VERDICT
        st.subheader("Coach's Verdict")
        st.info(f"🎙️ \"{r['message']}\"")
        
    else:
        # Default prompt
        st.info("Your performance analysis will appear here once you log your session. 🚀")