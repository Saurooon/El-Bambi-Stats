import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(layout="wide", page_title="Business Weekly Dashboard")

st.title("Weekly Performance Dashboard")

# 1. File Upload
uploaded_file = st.file_uploader("Upload your data (CSV format: date, revenue, labor_cost, food_cost)", type="csv")

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # 2. Date Selection
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.date_input(
        "Select Weekly Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Ensure range is selected
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['date'].get(dt) >= start_date) & (df['date'].get(dt) <= end_date) # Simplified logic
        # Standard filtering:
        filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
        
        # 3. Calculations
        total_revenue = filtered_df['revenue'].sum()
        total_labor_cost = filtered_df['labor_cost'].sum()
        total_food_cost = filtered_df['food_cost'].sum()
        
        # Avoid division by zero
        labor_pct = (total_labor_cost / total_revenue * 100) if total_revenue > 0 else 0
        food_pct = (total_food_cost / total_revenue * 100) if total_revenue > 0 else 0
        profit = total_revenue - total_labor_cost - total_food_cost

        # 4. Gauge Chart Helper Function
        def create_gauge(value, title, ranges, suffix=""):
            # Determine color based on ranges provided
            # ranges format: [(min, max, color), ...]
            color = "gray"
            for r_min, r_max, r_color in ranges:
                if r_min <= value <= r_max:
                    color = r_color
                    break
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                number={'suffix': suffix, 'valueformat': '.2f' if suffix == "" else '.2f'},
                title={'text': title, 'font': {'size': 24}},
                gauge={
                    'axis': {'range': [0, max(value * 1.2, 7500 if suffix == "" else 60)]},
                    'bar': {'color': color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                }
            ))
            fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=20))
            return fig

        # 5. Define Color Thresholds
        # Revenue Logic
        rev_ranges = [(0, 4899, "red"), (4900, 5199, "yellow"), (5200, 999999, "green")]
        
        # Labor Logic (Corrected typo: Red is > 36.5%)
        labor_ranges = [(0, 35, "green"), (35.01, 36.5, "yellow"), (36.51, 100, "red")]
        
        # Food Logic
        food_ranges = [(0, 30.4, "green"), (30.41, 30.5, "yellow"), (30.51, 100, "red")]
        
        # Profit Logic
        profit_ranges = [( -9999, 2499, "red"), (2500, 2749, "yellow"), (2750, 99999, "green")]

        # 6. Display Layout
        row1_col1, row1_col2, row1_col3 = st.columns(3)
        
        with row1_col1:
            st.plotly_chart(create_gauge(total_revenue, "Revenue", rev_ranges, "$"), use_container_width=True)
            
        with row1_col2:
            st.plotly_chart(create_gauge(food_pct, "Food %", food_ranges, "%"), use_container_width=True)
            
        with row1_col3:
            st.plotly_chart(create_gauge(labor_pct, "Labor %", labor_ranges, "%"), use_container_width=True)

        st.divider()
        
        # Profit Row (centered)
        _, profit_col, _ = st.columns([1, 2, 1])
        with profit_col:
            st.plotly_chart(create_gauge(profit, "Profit", profit_ranges, "$"), use_container_width=True)

else:
    st.info("Please upload a CSV file to begin.")
