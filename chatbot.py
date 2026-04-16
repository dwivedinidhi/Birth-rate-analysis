"""
Chatbot module for Birth Rate Prediction System
Provides conversational interface for predictions and data insights
"""

import re
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import os

class BirthPredictionChatbot:
    def __init__(self, model_path=None, data_path="births.csv"):
        """Initialize the chatbot with model and data"""
        self.model = None
        self.data = None
        
        # Load model if available
        if model_path and os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
        
        # Load data
        try:
            self.data = pd.read_csv(data_path)
            self.data['day'] = self.data['day'].fillna(1).astype(int)
            self.data['decade'] = 10 * (self.data['year'] // 10)
        except Exception as e:
            print(f"Warning: Could not load data: {e}")
    
    def get_response(self, user_input):
        """Process user input and return appropriate response"""
        user_input = user_input.lower().strip()
        
        # Greeting patterns
        if any(word in user_input for word in ['hello', 'hi', 'hey', ' greetings']):
            return self._greeting_response()
        
        # Help patterns
        if any(word in user_input for word in ['help', 'commands', 'what can you do']):
            return self._help_response()
        
        # Prediction patterns
        prediction_patterns = [
            r'predict\s+births?\s+(?:for\s+)?(.+)',
            r'how\s+many\s+births?\s+(?:are\s+)?(?:predicted\s+)?(?:for\s+)?(.+)',
            r'what\s+(?:is\s+)?the\s+predicted\s+births?\s+(?:for\s+)?(.+)',
            r'forecast\s+births?\s+(?:for\s+)?(.+)'
        ]
        
        for pattern in prediction_patterns:
            match = re.search(pattern, user_input)
            if match:
                date_str = match.group(1).strip()
                return self._handle_prediction_request(date_str)
        
        # Average births query
        if any(phrase in user_input for phrase in ['average births', 'mean births', 'avg births']):
            return self._average_births_response()
        
        # Total births query
        if any(phrase in user_input for phrase in ['total births', 'sum of births']):
            return self._total_births_response()
        
        # Decade comparison
        if any(phrase in user_input for phrase in ['decade', '10 year', 'ten year']):
            return self._decade_analysis_response()
        
        # Gender comparison
        if any(phrase in user_input for phrase in ['male', 'female', 'gender', 'boy', 'girl']):
            return self._gender_analysis_response()
        
        # Year with most births
        if any(phrase in user_input for phrase in ['most births', 'highest births', 'peak births', 'max births']):
            return self._peak_year_response()
        
        # Year with least births
        if any(phrase in user_input for phrase in ['least births', 'lowest births', 'minimum births', 'min births']):
            return self._lowest_year_response()
        
        # Trend analysis
        if any(phrase in user_input for phrase in ['trend', 'increasing', 'decreasing', 'pattern']):
            return self._trend_analysis_response()
        
        # About the model
        if any(phrase in user_input for phrase in ['about', 'how does it work', 'what model', 'algorithm']):
            return self._model_info_response()
        
        # About the data
        if any(phrase in user_input for phrase in ['data source', 'dataset', 'where data', 'data from']):
            return self._data_info_response()
        
        # Goodbye patterns
        if any(word in user_input for word in ['bye', 'goodbye', 'exit', 'quit', 'thank you', 'thanks']):
            return self._goodbye_response()
        
        # If no pattern matches
        return self._fallback_response()
    
    def _greeting_response(self):
        """Return a friendly greeting"""
        return (
            "👋 Hello! I'm your Birth Rate Prediction Assistant. "
            "I can help you with:\n\n"
            "• **Predict births** for any date (e.g., 'Predict births for March 2025')\n"
            "• **Analyze trends** in birth data\n"
            "• **Answer questions** about the dataset\n\n"
            "Type 'help' to see all available commands!"
        )
    
    def _help_response(self):
        """Return help information"""
        return (
            "📋 **Available Commands:**\n\n"
            "**Predictions:**\n"
            "• 'Predict births for [month] [year]'\n"
            "• 'How many births for March 2025?'\n"
            "• 'Forecast births for 2026'\n\n"
            "**Data Analysis:**\n"
            "• 'What is the average births?'\n"
            "• 'Show decade analysis'\n"
            "• 'Compare male vs female births'\n"
            "• 'Which year had most births?'\n"
            "• 'What's the birth trend?'\n\n"
            "**Information:**\n"
            "• 'How does the model work?'\n"
            "• 'Tell me about the data'\n\n"
            "Type 'bye' to end the conversation."
        )
    
    def _handle_prediction_request(self, date_str):
        """Handle birth prediction requests"""
        if not self.model:
            return "❌ Sorry, the prediction model is not available. Please ensure the model file exists."
        
        # Try to parse various date formats
        date_patterns = [
            r'(\d{4})',  # Just year
            r'(\d{1,2})[/-](\d{4})',  # MM/YYYY or MM-YYYY
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\w+)\s+(\d{4})',  # Month YYYY
            r'(\w+)\s+(\d{1,2})[,-]\s+(\d{4})',  # Month DD, YYYY
        ]
        
        # Month name to number mapping
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        year = None
        month = None
        day = 1  # Default to first day of month
        
        # Try parsing with regex patterns
        for i, pattern in enumerate(date_patterns):
            match = re.search(pattern, date_str)
            if match:
                groups = match.groups()
                if i == 0:  # Just year
                    year = int(groups[0])
                    month = 1
                elif i == 1:  # MM/YYYY
                    month = int(groups[0])
                    year = int(groups[1])
                elif i == 2:  # DD/MM/YYYY
                    day = int(groups[0])
                    month = int(groups[1])
                    year = int(groups[2])
                elif i == 3:  # Month YYYY
                    month_name = groups[0].lower()
                    if month_name in month_map:
                        month = month_map[month_name]
                        year = int(groups[1])
                elif i == 4:  # Month DD, YYYY
                    month_name = groups[0].lower()
                    if month_name in month_map:
                        month = month_map[month_name]
                        day = int(groups[1])
                        year = int(groups[2])
                break
        
        # Validate parsed date
        if not year or not month:
            return "❌ I couldn't understand the date. Please use formats like:\n• 'March 2025'\n• '03/2025'\n• '15/03/2025'"
        
        if month < 1 or month > 12:
            return "❌ Invalid month. Please enter a month between 1 and 12."
        
        if year < 1900 or year > 2100:
            return "❌ Year out of range. Please enter a year between 1900 and 2100."
        
        try:
            # Make prediction
            prediction = self.model.predict([[year, month, day]])
            predicted_value = int(prediction[0])
            
            # Get historical context if available
            context = ""
            if self.data is not None:
                historical_data = self.data[(self.data['year'] == year) & (self.data['month'] == month)]
                if not historical_data.empty:
                    avg_historical = historical_data['births'].mean()
                    context = f"\n\n📊 **Historical Context:** The average births for {month}/{year} in our data was {avg_historical:.0f}."
            
            return (
                f"🔮 **Prediction for {day}-{month:02d}-{year}:**\n\n"
                f"**Predicted Births:** {predicted_value:,}\n"
                f"{context}\n\n"
                f"Note: This prediction is based on historical patterns learned by our Random Forest model."
            )
        except Exception as e:
            return f"❌ Error making prediction: {str(e)}"
    
    def _average_births_response(self):
        """Return average births information"""
        if self.data is None:
            return "❌ Data not available for analysis."
        
        avg_total = self.data['births'].mean()
        avg_male = self.data[self.data['gender'] == 'M']['births'].mean() if 'gender' in self.data.columns else None
        avg_female = self.data[self.data['gender'] == 'F']['births'].mean() if 'gender' in self.data.columns else None
        
        response = f"📊 **Average Births Analysis:**\n\n"
        response += f"• **Overall Average:** {avg_total:,.0f} births per day\n"
        
        if avg_male is not None and avg_female is not None:
            response += f"• **Male Average:** {avg_male:,.0f} births per day\n"
            response += f"• **Female Average:** {avg_female:,.0f} births per day\n"
        
        return response
    
    def _total_births_response(self):
        """Return total births information"""
        if self.data is None:
            return "❌ Data not available for analysis."
        
        total = self.data['births'].sum()
        year_range = f"{self.data['year'].min()} to {self.data['year'].max()}"
        
        return (
            f"📊 **Total Births:**\n\n"
            f"• **Total Births in Dataset:** {total:,.0f}\n"
            f"• **Time Period:** {year_range}\n"
            f"• **Data Points:** {len(self.data):,} records"
        )
    
    def _decade_analysis_response(self):
        """Return decade-wise analysis"""
        if self.data is None:
            return "❌ Data not available for analysis."
        
        decade_stats = self.data.groupby('decade')['births'].agg(['sum', 'mean', 'count'])
        decade_stats = decade_stats.sort_index()
        
        response = "📊 **Decade-wise Birth Analysis:**\n\n"
        
        for decade, row in decade_stats.iterrows():
            response += f"• **{int(decade)}s:** Total: {row['sum']:,.0f}, Average: {row['mean']:.0f}/day\n"
        
        # Find highest and lowest decades
        highest_decade = decade_stats['sum'].idxmax()
        lowest_decade = decade_stats['sum'].idxmin()
        
        response += f"\n📈 **Highest:** {int(highest_decade)}s with {decade_stats.loc[highest_decade, 'sum']:,.0f} total births\n"
        response += f"📉 **Lowest:** {int(lowest_decade)}s with {decade_stats.loc[lowest_decade, 'sum']:,.0f} total births\n"
        
        return response
    
    def _gender_analysis_response(self):
        """Return gender-wise analysis"""
        if self.data is None or 'gender' not in self.data.columns:
            return "❌ Gender data not available in the dataset."
        
        gender_stats = self.data.groupby('gender')['births'].agg(['sum', 'mean', 'count'])
        
        response = "👫 **Gender-wise Birth Analysis:**\n\n"
        
        for gender, row in gender_stats.iterrows():
            gender_label = "Male" if gender == 'M' else "Female" if gender == 'F' else gender
            response += f"• **{gender_label}:** Total: {row['sum']:,.0f}, Average: {row['mean']:.0f}/day\n"
        
        # Calculate ratio
        if 'M' in gender_stats.index and 'F' in gender_stats.index:
            male_total = gender_stats.loc['M', 'sum']
            female_total = gender_stats.loc['F', 'sum']
            ratio = male_total / female_total if female_total > 0 else 0
            response += f"\n📊 **Male to Female Ratio:** {ratio:.2f}:1\n"
            response += f"• **Male Percentage:** {(male_total/(male_total+female_total)*100):.1f}%\n"
            response += f"• **Female Percentage:** {(female_total/(male_total+female_total)*100):.1f}%\n"
        
        return response
    
    def _peak_year_response(self):
        """Return year with most births"""
        if self.data is None:
            return "❌ Data not available for analysis."
        
        year_stats = self.data.groupby('year')['births'].sum()
        peak_year = year_stats.idxmax()
        peak_value = year_stats.max()
        
        # Get top 3 years
        top_3 = year_stats.nlargest(3)
        
        response = "📈 **Years with Highest Births:**\n\n"
        for i, (year, value) in enumerate(top_3.items(), 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            response += f"{medal} **{year}:** {value:,.0f} births\n"
        
        response += f"\n🏆 **Peak Year:** {peak_year} with {peak_value:,.0f} total births"
        
        return response
    
    def _lowest_year_response(self):
        """Return year with least births"""
        if self.data is None:
            return "❌ Data not available for analysis."
        
        year_stats = self.data.groupby('year')['births'].sum()
        lowest_year = year_stats.idxmin()
        lowest_value = year_stats.min()
        
        # Get bottom 3 years
        bottom_3 = year_stats.nsmallest(3)
        
        response = "📉 **Years with Lowest Births:**\n\n"
        for i, (year, value) in enumerate(bottom_3.items(), 1):
            response += f"• **{year}:** {value:,.0f} births\n"
        
        response += f"\n🔻 **Lowest Year:** {lowest_year} with {lowest_value:,.0f} total births"
        
        return response
    
    def _trend_analysis_response(self):
        """Return trend analysis"""
        if self.data is None:
            return "❌ Data not available for analysis."
        
        year_stats = self.data.groupby('year')['births'].sum().sort_index()
        
        # Calculate trend
        years = year_stats.index.values
        values = year_stats.values
        
        if len(years) > 1:
            # Simple linear trend
            correlation = np.corrcoef(years, values)[0, 1]
            
            if correlation > 0.5:
                trend = "📈 **increasing**"
            elif correlation < -0.5:
                trend = "📉 **decreasing**"
            else:
                trend = "➡️ **relatively stable**"
            
            response = f"📊 **Birth Rate Trend Analysis:**\n\n"
            response += f"• **Overall Trend:** {trend}\n"
            response += f"• **Correlation Coefficient:** {correlation:.2f}\n"
            response += f"• **Time Period:** {years[0]} to {years[-1]}\n"
            response += f"• **Years Analyzed:** {len(years)}\n\n"
            
            # Recent trend (last 5 years)
            recent_years = year_stats.tail(5)
            recent_corr = np.corrcoef(recent_years.index.values, recent_years.values)[0, 1] if len(recent_years) > 1 else 0
            
            if recent_corr > 0.3:
                recent_trend = "📈 increasing"
            elif recent_corr < -0.3:
                recent_trend = "📉 decreasing"
            else:
                recent_trend = "➡️ stable"
            
            response += f"• **Recent Trend (Last 5 Years):** {recent_trend}\n"
            
            return response
        
        return "❌ Not enough data for trend analysis."
    
    def _model_info_response(self):
        """Return information about the ML model"""
        return (
            "🤖 **About the Prediction Model:**\n\n"
            "• **Algorithm:** Random Forest Regressor\n"
            "• **Features Used:** Year, Month, Day\n"
            "• **Target:** Number of Births\n"
            "• **Training Data:** Historical birth records from births.csv\n\n"
            "**How it Works:**\n"
            "The Random Forest model learns patterns from historical birth data, "
            "including seasonal trends, yearly variations, and day-of-month patterns. "
            "It then uses these learned patterns to make predictions for new dates.\n\n"
            "**Model Performance:**\n"
            "The model is trained on 80% of the data and tested on 20% to ensure "
            "it generalizes well to unseen data."
        )
    
    def _data_info_response(self):
        """Return information about the dataset"""
        if self.data is None:
            return "❌ Data information not available."
        
        response = "📊 **Dataset Information:**\n\n"
        response += f"• **Total Records:** {len(self.data):,}\n"
        response += f"• **Time Period:** {self.data['year'].min()} to {self.data['year'].max()}\n"
        response += f"• **Features:** Year, Month, Day, Births"
        
        if 'gender' in self.data.columns:
            response += ", Gender"
        
        response += f"\n• **Date Range:** {self.data['year'].min()}/{self.data['month'].min():02d} to {self.data['year'].max()}/{self.data['month'].max():02d}\n"
        
        # Data quality info
        missing_values = self.data.isnull().sum()
        total_missing = missing_values.sum()
        if total_missing > 0:
            response += f"\n• **Missing Values:** {total_missing} total missing values (handled during preprocessing)\n"
        else:
            response += f"\n• **Data Quality:** Complete dataset with no missing values\n"
        
        return response
    
    def _goodbye_response(self):
        """Return goodbye message"""
        return (
            "👋 Thank you for using the Birth Rate Prediction Assistant! "
            "Feel free to come back anytime for predictions and analysis. "
            "Have a great day! 🎉"
        )
    
    def _fallback_response(self):
        """Return fallback response for unrecognized input"""
        return (
            "🤔 I'm not sure I understand that question. "
            "I can help you with birth predictions, data analysis, and trend insights.\n\n"
            "Try asking:\n"
            "• 'Predict births for March 2025'\n"
            "• 'What is the average births?'\n"
            "• 'Show me decade analysis'\n\n"
            "Type 'help' for more commands."
        )
    
    def get_quick_actions(self):
        """Return list of quick action buttons"""
        return [
            "Predict births for current month",
            "Show average births",
            "Decade analysis",
            "Gender comparison",
            "Peak year analysis",
            "Trend analysis",
            "Model information"
        ]
    
    def process_quick_action(self, action):
        """Process quick action button clicks"""
        action_map = {
            "Predict births for current month": f"predict births for {datetime.now().strftime('%B %Y')}",
            "Show average births": "average births",
            "Decade analysis": "decade analysis",
            "Gender comparison": "male vs female births",
            "Peak year analysis": "most births",
            "Trend analysis": "birth trend",
            "Model information": "how does the model work"
        }
        
        if action in action_map:
            return self.get_response(action_map[action])
        return self._fallback_response()