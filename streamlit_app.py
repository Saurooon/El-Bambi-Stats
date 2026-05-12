import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Weekly Performance Dashboard")
st.title("Weekly Performance Dashboard")

# --- DATA LOADING ---
# Replace this URL with your actual "Raw" GitHub URL
GITHUB_CSV_URL = "https://raw.githubusercontent.com/Saurooon/El-Bambi-Stats/refs/heads/main/weekly_costs.csv"

@st.cache_data(ttl=600) # This refreshes the data every 10 minutes
def load_data(url):
    try:
        df = pd.read_csv(url)
        df['week_start'] = pd.to_datetime(df['week_start'])
        return df
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return None

df = load_data(GITHUB_CSV_URL)

if df is not None:
    # --- DATE SELECTION ---
    selected_week = st.selectbox(
        "Select Week Commencing",
        options=sorted(df['week_start'].dt.date.unique(), reverse=True)
    )

    filtered_df = df[df['week_start'].dt.date == selected_week]
    
    if not filtered_df.empty:
        # 3. Calculations
        total_revenue = filtered_df['revenue'].sum()
        total_labor_cost = filtered_df['labor_cost'].sum()
        total_food_cost = filtered_df['food_cost'].sum()
        
        labor_pct = (total_labor_cost / total_revenue * 100) if total_revenue > 0 else 0
        food_pct = (total_food_cost / total_revenue * 100) if total_revenue > 0 else 0
        profit = total_revenue - total_labor_cost - total_food_cost

        # 4. Gauge Chart Helper Function with Target Lines
def create_gauge(value, title, ranges, target_value, suffix=""):
    # Current value color logic (keeps your existing thresholds)
    color = "gray"
    for r_min, r_max, r_color in ranges:
        if r_min <= value <= r_max:
            color = r_color
            break
    
    # Determine appropriate axis range
    if "%" in suffix:
        axis_range = [0, 100]
    else:
        # Dynamic axis for dollars based on target or value
        axis_range = [0, max(value * 1.3, target_value * 1.3, 6000)]

    # New custom formatting for percentages to avoid 2-place leading zero decimals
    value_format = '.1f' if suffix == "%" else ',.2f'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': suffix, 'valueformat': value_format},
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': axis_range},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e0e0e0",
            # --- THIS BLOCK ADDS THE TARGET LINE ---
            'threshold': {
                'line': {'color': "#2b2b2b", 'width': 5},  # Custom color and width for target line
                'thickness': 0.85, # Makes the line cross the colored bar
                'value': target_value
            }
            # --------------------------------------
        }
    ))
    fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=20))
    return fig

        # 5. Thresholds
        rev_ranges = [(0, 4799.99, "red"), (4800, 5199.99, "yellow"), (5200, 100000, "green")]
        labor_ranges = [(0, 35, "green"), (35.01, 36.5, "yellow"), (36.51, 100, "red")]
        food_ranges = [(0, 30.4, "green"), (30.41, 30.5, "yellow"), (30.51, 100, "red")]
        profit_ranges = [(-10000, 2499.99, "red"), (2500, 2749.99, "yellow"), (2750, 100000, "green")]

       # 6. Display Layout (Updated with target values)
        col1, col2, col3 = st.columns(3)
        with col1: 
            # Revenue Call updated with 5200 target
            st.plotly_chart(create_gauge(total_revenue, "Revenue", rev_ranges, 5200, "$"), use_container_width=True)
        with col2: 
            # Food Call updated with 30.4 target
            st.plotly_chart(create_gauge(food_pct, "Food Cost %", food_ranges, 30.4, "%"), use_container_width=True)
        with col3: 
            # Labor Call updated with 35 target
            st.plotly_chart(create_gauge(labor_pct, "Labor Cost %", labor_ranges, 35, "%"), use_container_width=True)

        st.divider()
        _, profit_col, _ = st.columns([1, 2, 1])
        with profit_col: 
            # Profit Call updated with 2750 target
            st.plotly_chart(create_gauge(profit, "Total Profit", profit_ranges, 2750, "$"), use_container_width=True)
