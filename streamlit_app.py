import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(layout="wide", page_title="Weekly Performance Dashboard")

st.title("Weekly Performance Dashboard")

# 1. File Upload
uploaded_file = st.file_uploader("Upload your data (CSV format: week_start, revenue, labor_cost, food_cost)", type="csv")

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    
    # Update: Now reading 'week_start' instead of 'date'
    df['week_start'] = pd.to_datetime(df['week_start'])
    
    # 2. Date Selection (Filtering based on the start of the week)
    min_date = df['week_start'].min().date()
    max_date = df['week_start'].max().date()
    
    selected_week = st.selectbox(
        "Select Week Commencing",
        options=sorted(df['week_start'].dt.date.unique(), reverse=True)
    )

    # Filter data for the selected week
    filtered_df = df[df['week_start'].dt.date == selected_week]
    
    if not filtered_df.empty:
        # 3. Calculations (Aggregating in case there are multiple entries per week_start)
        total_revenue = filtered_df['revenue'].sum()
        total_labor_cost = filtered_df['labor_cost'].sum()
        total_food_cost = filtered_df['food_cost'].sum()
        
        labor_pct = (total_labor_cost / total_revenue * 100) if total_revenue > 0 else 0
        food_pct = (total_food_cost / total_revenue * 100) if total_revenue > 0 else 0
        profit = total_revenue - total_labor_cost - total_food_cost

        # 4. Gauge Chart Helper Function
        def create_gauge(value, title, ranges, suffix=""):
            color = "gray"
            for r_min, r_max, r_color in ranges:
                if r_min <= value <= r_max:
                    color = r_color
                    break
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                number={'suffix': suffix, 'valueformat': '.2f'},
                title={'text': title, 'font': {'size': 24}},
                gauge={
                    'axis': {'range': [None, max(value * 1.3, 100 if "%" in suffix else 6000)]},
                    'bar': {'color': color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e0e0e0",
                }
            ))
            fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=20))
            return fig

        # 5. Threshold Logic
        rev_ranges = [(0, 4899.99, "red"), (4900, 5199.99, "yellow"), (5200, 100000, "green")]
        labor_ranges = [(0, 35, "green"), (35.01, 36.5, "yellow"), (36.51, 100, "red")]
        food_ranges = [(0, 30.4, "green"), (30.41, 30.5, "yellow"), (30.51, 100, "red")]
        profit_ranges = [(-10000, 2499.99, "red"), (2500, 2749.99, "yellow"), (2750, 100000, "green")]

        # 6. Display Layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.plotly_chart(create_gauge(total_revenue, "Revenue", rev_ranges, "$"), use_container_width=True)
        with col2:
            st.plotly_chart(create_gauge(food_pct, "Food Cost %", food_ranges, "%"), use_container_width=True)
        with col3:
            st.plotly_chart(create_gauge(labor_pct, "Labor Cost %", labor_ranges, "%"), use_container_width=True)

        st.divider()
        
        _, profit_col, _ = st.columns([1, 2, 1])
        with profit_col:
            st.plotly_chart(create_gauge(profit, "Total Profit", profit_ranges, "$"), use_container_width=True)
    else:
        st.warning("No data found for the selected week.")

else:
    st.info("Please upload your CSV file containing 'week_start' column to see the dashboard.")
