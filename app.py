import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import os
import calendar
from datetime import datetime
from chatbot import BirthPredictionChatbot

# ----------------------------------------
# LOAD TRAINED MODEL SAFELY
# ----------------------------------------

model_path = os.path.join(os.path.dirname(__file__), "birth_prediction_model.pkl")

if not os.path.exists(model_path):
    st.error("❌ Model file not found! Please run train_model.py first.")
    st.stop()

model = joblib.load(model_path)

# ----------------------------------------
# INITIALIZE CHATBOT
# ----------------------------------------

chatbot = BirthPredictionChatbot(model_path=model_path, data_path="births.csv")

# ----------------------------------------
# APP TITLE
# ----------------------------------------

st.set_page_config(page_title="Birth Rate Prediction System", layout="wide")

st.title("📊 Birth Rate Analysis & Prediction System")
st.write("Final Year Major Project – Machine Learning Based Forecasting")

# ----------------------------------------
# SIDEBAR - CHATBOT INTERFACE
# ----------------------------------------

with st.sidebar:
    st.header("🤖 Chatbot Assistant")
    st.write("Ask me anything about birth predictions and data analysis!")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": chatbot._greeting_response()
        })
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        response = chatbot.get_response(prompt)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Quick Actions
    st.divider()
    st.subheader("⚡ Quick Actions")
    
    quick_actions = chatbot.get_quick_actions()
    
    for action in quick_actions:
        if st.button(action, key=f"quick_{action}"):
            # Process quick action
            response = chatbot.process_quick_action(action)
            
            # Add to chat history
            st.session_state.messages.append({
                "role": "user", 
                "content": action
            })
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response
            })
            
            # Rerun to update chat
            st.rerun()

# ----------------------------------------
# MAIN CONTENT - PREDICTION SECTION
# ----------------------------------------

tab1, tab2, tab3 = st.tabs(["🔮 Predict Births", "📈 Data Visualization", "🤖 Chatbot"])

with tab1:
    st.subheader("📅 Enter Date for Prediction")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        year = st.number_input("Year", min_value=1900, max_value=2100, value=2025)
    
    with col2:
        month = st.number_input("Month", min_value=1, max_value=12, value=1)
    
    with col3:
        # Automatically get correct number of days in the selected month
        max_day = calendar.monthrange(year, month)[1]
        day = st.number_input("Day", min_value=1, max_value=max_day, value=1)
    
    # Prediction button
    if st.button("🔮 Predict Births", type="primary"):
        try:
            prediction = model.predict([[year, month, day]])
            st.success(f"✅ Predicted Births on {day}-{month:02d}-{year}: {int(prediction[0]):,}")
            
            # Add to chat history for context
            chatbot_message = f"User requested prediction for {day}-{month:02d}-{year}: {int(prediction[0]):,} births predicted."
            st.session_state.messages.append({
                "role": "system", 
                "content": chatbot_message
            })
            
        except Exception as e:
            st.error("❌ Error in prediction")
            st.text(str(e))

with tab2:
    st.subheader("📈 Births Data Visualization")
    
    births = pd.read_csv("births.csv")
    births['day'] = births['day'].fillna(1).astype(int)
    births['decade'] = 10 * (births['year'] // 10)
    
    # Create visualization options
    viz_option = st.selectbox(
        "Select Visualization Type",
        ["Births by Decade", "Monthly Trends", "Gender Distribution"]
    )
    
    if viz_option == "Births by Decade":
        birth_decade = births.pivot_table('births', index='decade', columns='gender', aggfunc='sum')
        st.line_chart(birth_decade)
        
        # Add insights
        st.write("**Insights:**")
        decade_stats = births.groupby('decade')['births'].sum()
        peak_decade = decade_stats.idxmax()
        st.write(f"• Peak decade: {int(peak_decade)}s with {decade_stats.max():,} total births")
    
    elif viz_option == "Monthly Trends":
        monthly_avg = births.groupby('month')['births'].mean()
        st.bar_chart(monthly_avg)
        st.write("**Insights:**")
        peak_month = monthly_avg.idxmax()
        st.write(f"• Peak month: {peak_month} with average {monthly_avg.max():.0f} births")
    
    elif viz_option == "Gender Distribution":
        if 'gender' in births.columns:
            gender_stats = births.groupby('gender')['births'].sum()
            fig, ax = plt.subplots()
            ax.pie(gender_stats.values, labels=['Female', 'Male'], autopct='%1.1f%%')
            ax.set_title('Gender Distribution of Births')
            st.pyplot(fig)
        else:
            st.write("Gender data not available in this dataset.")

with tab3:
    st.subheader("🤖 Chatbot Conversation")
    st.write("This tab shows the full chatbot interface. You can also use the sidebar for quick access!")
    
    # Display full conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ----------------------------------------
# FOOTER
# ----------------------------------------

st.divider()
st.caption("Developed as a Major Project using Python, Machine Learning & Streamlit")
st.caption("🤖 Chatbot powered by rule-based NLP and integrated with ML predictions")