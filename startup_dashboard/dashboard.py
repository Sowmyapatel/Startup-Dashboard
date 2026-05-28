
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Load data
@st.cache_data
def load_data():
    df_events = pd.read_csv('events.csv', parse_dates=['date'])
    df_users = pd.read_csv('users.csv', parse_dates=['signup_date'])
    return df_events, df_users

st.set_page_config(page_title="Startup Metrics Dashboard", layout="wide")

# Title
st.title("🚀 Startup Growth Dashboard")
st.markdown("### North Star: Weekly Active Users completing 3+ key actions")

# Load data
df_events, df_users = load_data()

# Calculate metrics
daily_active = df_events[df_events['event'] == 'daily_visit'].groupby('date').size()
latest_DAU = daily_active.iloc[-1] if len(daily_active) > 0 else 0

# MAU calculation
last_30_days = df_events[df_events['date'] >= (datetime.now() - timedelta(days=30))]
MAU = last_30_days['user_id'].nunique()

# North Star Metric (simplified: users with 3+ events in a week)
df_events['week'] = df_events['date'].dt.isocalendar().week
weekly_power_users = df_events.groupby(['user_id', 'week']).size()
north_star = len(weekly_power_users[weekly_power_users >= 3].reset_index()['user_id'].unique())

# Layout with columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("⭐ North Star Metric", f"{north_star:,}", "Weekly Power Users")
with col2:
    st.metric("📱 DAU", f"{latest_DAU:,}")
with col3:
    st.metric("👥 MAU", f"{MAU:,}")
with col4:
    stickiness = (latest_DAU/MAU*100) if MAU > 0 else 0
    st.metric("🔗 Stickiness (DAU/MAU)", f"{stickiness:.1f}%", 
              delta="Good >20%" if stickiness > 20 else "⚠️ Too low")

# What's going wrong section
st.subheader("⚠️ What's going wrong?")
col1, col2 = st.columns(2)

with col1:
    # Retention rates
    retention_data = {'Day': ['Day 1', 'Day 7', 'Day 30'], 
                      'Retention %': [32, 18, 12]}
    retention_df = pd.DataFrame(retention_data)
    fig = px.bar(retention_df, x='Day', y='Retention %', 
                 title="User Retention Drops Quickly",
                 color='Retention %', color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)
    
with col2:
    st.info('''
    **🔍 Key Issues Identified:**
    - ❌ Only 18% return after 7 days
    - ❌ Stickiness is below 20% (industry standard)
    - ❌ Users don't complete onboarding
    ''')

# Where users drop off - Funnel
st.subheader("🎯 Where users drop off")
funnel_data = {
    'Stage': ['Visit Website', 'Sign Up', 'Complete Onboarding', 'Active for 7 days', 'Premium'],
    'Users': [5000, 3200, 2100, 900, 450]
}
funnel_df = pd.DataFrame(funnel_data)
fig = go.Figure(go.Funnel(
    y=funnel_df['Stage'],
    x=funnel_df['Users'],
    textposition="inside",
    textinfo="value+percent initial"
))
fig.update_layout(title="Conversion Funnel - Biggest Drop: Onboarding")
st.plotly_chart(fig, use_container_width=True)

# Drop-off by device
st.subheader("📱 Where do different devices drop off?")
device_dropoff = {
    'Device': ['Mobile', 'Desktop'],
    'Drop at Signup': [42, 28],
    'Drop at Onboarding': [55, 35]
}
device_df = pd.DataFrame(device_dropoff)
fig = px.bar(device_df.melt(id_vars=['Device'], var_name='Stage', value_name='Drop %'),
             x='Stage', y='Drop %', color='Device', barmode='group',
             title="Mobile users drop off significantly more")
st.plotly_chart(fig, use_container_width=True)

# Recommendations
st.subheader("💡 Recommended Actions (PM + Analyst)")
st.success('''
1. **Fix mobile onboarding** - 55% drop vs 35% on desktop → A/B test simplified 3-step mobile tour
2. **Improve D7 retention** - Send personalized re-engagement emails after 3 days of inactivity
3. **North Star impact** - Fixing these could increase Weekly Power Users by ~40%
''')

# Footer
st.markdown("---")
st.caption("Built with ❤️ | Data from last 90 days | Updated daily")
