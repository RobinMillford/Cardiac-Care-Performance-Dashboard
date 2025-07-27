import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="Cardiac Care Performance Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Define Unique Color Palette (Cyan Theme) ---
PRIMARY_COLOR = '#00CED1'  # Dark Turquoise - for main data, "as expected"
ACCENT_POSITIVE = '#48D1CC' # Medium Turquoise - for positive outcomes (decrease in mortality, lower than expected)
ACCENT_NEGATIVE = '#EF5350' # Reddish Orange/Coral - for negative outcomes (increase in mortality, higher than expected)
NEUTRAL_DARK = '#333333'   # Dark grey for text
NEUTRAL_LIGHT = '#F5F5F5'  # Light grey for backgrounds/dividers
SECONDARY_ACCENT = '#20B2AA' # Light Sea Green - for additional lines/categories

# Custom color map for Comparison Results Category
COMP_COLORS = {
    'Rate higher than Statewide Rate': ACCENT_NEGATIVE,
    'Rate lower than Statewide Rate': ACCENT_POSITIVE,
    'Rate not different than Statewide Rate': PRIMARY_COLOR
}

# Custom color map for Procedures
PROCEDURE_COLORS = {
    'All PCI': PRIMARY_COLOR,
    'Non-Emergency PCI': ACCENT_POSITIVE,
    'Valve or Valve/CABG': SECONDARY_ACCENT,
}

# --- Data Loading and Preprocessing ---
@st.cache_data
def load_and_preprocess_data(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: '{file_path}' not found. Please upload the file or ensure the path is correct.")
        st.stop()

    df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('/', '_').str.replace('-', '_')

    numeric_cols = [
        'Facility_ID', 'Number_of_Cases', 'Number_of_Deaths',
        'Observed_Mortality_Rate', 'Expected_Mortality_Rate', 'Risk_Adjusted_Mortality_Rate',
        'Lower_Limit_of_Confidence_Interval', 'Upper_Limit_of_Confidence_Interval'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    def parse_year_range(year_str):
        if pd.isna(year_str):
            return None, None
        year_str = str(year_str).strip()
        if '-' in year_str:
            parts = year_str.split('-')
            try:
                start = int(parts[0])
                end = int(parts[1])
                return start, end
            except ValueError:
                return None, None
        else:
            try:
                single_year = int(year_str)
                return single_year, single_year
            except ValueError:
                return None, None

    df[['Start_Year', 'End_Year']] = df['Year_of_Hospital_Discharge'].apply(lambda x: pd.Series(parse_year_range(x)))
    df['Mid_Year'] = ((df['Start_Year'] + df['End_Year']) / 2).astype('Int64')

    df['Comparison_Results_Category'] = df['Comparison_Results'].astype('category')
    df['Is_Higher_Than_Expected_Mortality'] = (df['Comparison_Results'] == 'Rate higher than Statewide Rate')
    df['Is_Lower_Than_Expected_Mortality'] = (df['Comparison_Results'] == 'Rate lower than Statewide Rate')
    df['Is_As_Expected_Mortality'] = (df['Comparison_Results'] == 'Rate not different than Statewide Rate')

    df['Observed_vs_Expected_Difference'] = df['Observed_Mortality_Rate'] - df['Expected_Mortality_Rate']
    df['Observed_vs_RiskAdjusted_Difference'] = df['Observed_Mortality_Rate'] - df['Risk_Adjusted_Mortality_Rate']
    df['CI_Width'] = df['Upper_Limit_of_Confidence_Interval'] - df['Lower_Limit_of_Confidence_Interval']

    return df

# Load data
df = load_and_preprocess_data('cardiac_data_cleaned_engineered.csv')

# --- Dashboard Title and Description ---
st.title("❤️ Cardiac Care Performance Dashboard")
st.markdown(
    """
    This interactive dashboard analyzes cardiac surgery and percutaneous coronary intervention (PCI) performance
    across hospitals and regions since 2008. Explore trends, compare outcomes, and identify key insights into quality of care.
    """
)

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters")

# Year Filter
with st.sidebar.expander("Filter by Year", expanded=True):
    all_years = sorted(df['Start_Year'].unique())
    selected_years = st.slider(
        "Select Year Range",
        min_value=min(all_years),
        max_value=max(all_years),
        value=(min(all_years), max(all_years)),
        key="year_slider"
    )
df_filtered_by_year = df[(df['Start_Year'] >= selected_years[0]) & (df['Start_Year'] <= selected_years[1])]


# Region Filter
with st.sidebar.expander("Filter by Region", expanded=True):
    current_regions_options = ['Overall'] + sorted(df_filtered_by_year['Region'].unique().tolist())
    selected_region = st.selectbox(
        "Select a Region",
        options=current_regions_options,
        key="region_select"
    )
if selected_region == 'Overall':
    df_filtered_by_region = df_filtered_by_year
else:
    df_filtered_by_region = df_filtered_by_year[df_filtered_by_year['Region'] == selected_region]


# Procedure Filter
with st.sidebar.expander("Filter by Procedure", expanded=True):
    current_procedures_options = ['Overall'] + sorted(df_filtered_by_region['Procedure'].unique().tolist())
    selected_procedure = st.selectbox(
        "Select a Procedure",
        options=current_procedures_options,
        key="procedure_select"
    )
if selected_procedure == 'Overall':
    df_filtered_by_procedure = df_filtered_by_region
else:
    df_filtered_by_procedure = df_filtered_by_region[df_filtered_by_region['Procedure'] == selected_procedure]


# Hospital Filter (Optional, for detailed drill-down)
with st.sidebar.expander("Filter by Hospital", expanded=False):
    current_hospitals_options = ['Overall'] + sorted(df_filtered_by_procedure['Hospital_Name'].unique().tolist())
    selected_hospital = st.selectbox(
        "Select a Hospital",
        options=current_hospitals_options,
        key="hospital_select"
    )
if selected_hospital == 'Overall':
    df_filtered = df_filtered_by_procedure
else:
    df_filtered = df_filtered_by_procedure[df_filtered_by_procedure['Hospital_Name'] == selected_hospital]


if df_filtered.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
    st.stop()

# --- Key Performance Indicators (KPIs) ---
st.header("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

# Custom CSS for KPI boxes
st.markdown(f"""
<style>
div[data-testid="metric-container"] {{
    background-color: {NEUTRAL_LIGHT}; /* Light background for boxes */
    border: 1px solid {PRIMARY_COLOR}; /* Border with primary color */
    padding: 10% 10% 10% 10%;
    border-radius: 10px;
    color: {NEUTRAL_DARK};
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.05);
}}
div[data-testid="metric-container"] > label {{
    font-size: 1.1em;
    color: {PRIMARY_COLOR}; /* Primary color for labels */
    font-weight: bold;
}}
div[data-testid="metric-container"] > div.stMetricValue {{
    font-size: 2.2em;
    font-weight: bold;
}}
</style>
""", unsafe_allow_html=True)


# KPI 1: Total Procedures Performed
total_procedures = int(df_filtered['Number_of_Cases'].sum())
col1.markdown(f"<div data-testid='metric-container'><label>Total Procedures Performed</label><div class='stMetricValue'>{total_procedures:,}</div></div>", unsafe_allow_html=True)

# KPI 2: Average Observed Mortality Rate
avg_observed_mortality = df_filtered['Observed_Mortality_Rate'].mean()
col2.markdown(f"<div data-testid='metric-container'><label>Avg. Observed Mortality Rate</label><div class='stMetricValue'>{avg_observed_mortality:.2f}%</div></div>", unsafe_allow_html=True)

# KPI 3: Average Observed vs. Expected Difference
avg_diff = df_filtered['Observed_vs_Expected_Difference'].mean()
diff_color = ACCENT_POSITIVE if avg_diff < 0 else (ACCENT_NEGATIVE if avg_diff > 0 else PRIMARY_COLOR)
col3.markdown(f"<div data-testid='metric-container'><label>Avg. Obs. vs Exp. Difference</label><div class='stMetricValue' style='color:{diff_color};'>{avg_diff:.2f}%</div></div>", unsafe_allow_html=True)

# KPI 4: YoY Change in Observed Mortality Rate
yoy_mortality_change = 0.0
latest_year_data = df_filtered.groupby('Start_Year')['Observed_Mortality_Rate'].mean().sort_index()
if len(latest_year_data) >= 2:
    current_year_mortality = latest_year_data.iloc[-1]
    previous_year_mortality = latest_year_data.iloc[-2]
    if previous_year_mortality != 0:
        yoy_mortality_change = ((current_year_mortality - previous_year_mortality) / previous_year_mortality) * 100
    else:
        yoy_mortality_change = 0.0

arrow = ""
yoy_color = NEUTRAL_DARK
if yoy_mortality_change > 0:
    arrow = "▲"
    yoy_color = ACCENT_NEGATIVE
elif yoy_mortality_change < 0:
    arrow = "▼"
    yoy_color = ACCENT_POSITIVE

col4.markdown(f"<div data-testid='metric-container'><label>YoY Avg. Mortality Change</label><div class='stMetricValue' style='color:{yoy_color};'>{yoy_mortality_change:.2f}% {arrow}</div></div>", unsafe_allow_html=True)

st.markdown("---")

# --- Visualization Sections ---

# --- Analysis Area 1: Overall Trends Over Time ---
st.header("Overall Trends Over Time")

col_trend1, col_trend2 = st.columns(2)

with col_trend1:
    st.subheader("Procedure Volume Trend")
    df_volume_trend = df_filtered.groupby(['Start_Year', 'Procedure'])['Number_of_Cases'].sum().reset_index()
    fig_volume_trend = px.line(
        df_volume_trend,
        x='Start_Year',
        y='Number_of_Cases',
        color='Procedure',
        title='Total Procedures Performed by Year and Type',
        labels={'Number_of_Cases': 'Total Cases', 'Start_Year': 'Year'},
        template="plotly_white",
        color_discrete_map=PROCEDURE_COLORS
    )
    fig_volume_trend.update_layout(hovermode="x unified")
    st.plotly_chart(fig_volume_trend, use_container_width=True)

with col_trend2:
    st.subheader("Mortality Rate Trends")
    df_mortality_trend = df_filtered.groupby('Start_Year').agg(
        Observed_Mortality_Rate=('Observed_Mortality_Rate', 'mean'),
        Expected_Mortality_Rate=('Expected_Mortality_Rate', 'mean'),
        Risk_Adjusted_Mortality_Rate=('Risk_Adjusted_Mortality_Rate', 'mean')
    ).reset_index()

    fig_mortality_trend = go.Figure()
    fig_mortality_trend.add_trace(go.Scatter(
        x=df_mortality_trend['Start_Year'], y=df_mortality_trend['Observed_Mortality_Rate'],
        mode='lines+markers', name='Observed Mortality', line=dict(color=PRIMARY_COLOR)
    ))
    fig_mortality_trend.add_trace(go.Scatter(
        x=df_mortality_trend['Start_Year'], y=df_mortality_trend['Expected_Mortality_Rate'],
        mode='lines+markers', name='Expected Mortality', line=dict(color=NEUTRAL_DARK, dash='dash')
    ))
    fig_mortality_trend.add_trace(go.Scatter(
        x=df_mortality_trend['Start_Year'], y=df_mortality_trend['Risk_Adjusted_Mortality_Rate'],
        mode='lines+markers', name='Risk-Adjusted Mortality', line=dict(color=SECONDARY_ACCENT, dash='dot')
    ))

    fig_mortality_trend.update_layout(
        title='Average Mortality Rates Over Time',
        xaxis_title='Year',
        yaxis_title='Mortality Rate (%)',
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_mortality_trend, use_container_width=True)

st.subheader("Observed vs. Expected Mortality Difference Trend")
df_diff_trend = df_filtered.groupby('Start_Year')['Observed_vs_Expected_Difference'].mean().reset_index()
fig_diff_trend = px.line(
    df_diff_trend,
    x='Start_Year',
    y='Observed_vs_Expected_Difference',
    title='Average Observed vs. Expected Mortality Difference Over Time',
    labels={'Observed_vs_Expected_Difference': 'Difference (%)', 'Start_Year': 'Year'},
    template="plotly_white",
    color_discrete_sequence=[PRIMARY_COLOR]
)
fig_diff_trend.add_hline(y=0, line_dash="dot", line_color=NEUTRAL_DARK, annotation_text="Zero Difference")
fig_diff_trend.update_layout(hovermode="x unified")
st.plotly_chart(fig_diff_trend, use_container_width=True)

st.markdown("---")

# --- Analysis Area 2: Procedure-Specific Analysis ---
st.header("Procedure-Specific Analysis")

col_proc1, col_proc2 = st.columns(2)

with col_proc1:
    st.subheader("Procedure Volume Breakdown")
    df_proc_volume = df_filtered.groupby('Procedure')['Number_of_Cases'].sum().reset_index()
    fig_proc_volume = px.bar(
        df_proc_volume,
        x='Procedure',
        y='Number_of_Cases',
        title='Total Cases by Procedure Type',
        labels={'Number_of_Cases': 'Total Cases'},
        template="plotly_white",
        color='Procedure',
        color_discrete_map=PROCEDURE_COLORS
    )
    fig_proc_volume.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig_proc_volume, use_container_width=True)

with col_proc2:
    st.subheader("Procedure Mortality Comparison")
    df_proc_mortality = df_filtered.groupby('Procedure').agg(
        Observed_Mortality_Rate=('Observed_Mortality_Rate', 'mean'),
        Expected_Mortality_Rate=('Expected_Mortality_Rate', 'mean')
    ).reset_index()

    fig_proc_mortality = go.Figure(data=[
        go.Bar(name='Observed', x=df_proc_mortality['Procedure'], y=df_proc_mortality['Observed_Mortality_Rate'], marker_color=PRIMARY_COLOR),
        go.Bar(name='Expected', x=df_proc_mortality['Procedure'], y=df_proc_mortality['Expected_Mortality_Rate'], marker_color=NEUTRAL_DARK)
    ])
    fig_proc_mortality.update_layout(
        barmode='group',
        title='Average Mortality Rates by Procedure Type',
        xaxis_title='Procedure',
        yaxis_title='Mortality Rate (%)',
        template="plotly_white"
    )
    st.plotly_chart(fig_proc_mortality, use_container_width=True)

st.markdown("---")

# --- Analysis Area 3: Regional Performance Comparison ---
st.header("Regional Performance Comparison")

col_region1, col_region2 = st.columns(2)

with col_region1:
    st.subheader("Regional Mortality Performance")
    df_region_diff = df_filtered.groupby('Region')['Observed_vs_Expected_Difference'].mean().reset_index()
    fig_region_diff = px.bar(
        df_region_diff,
        x='Observed_vs_Expected_Difference',
        y='Region',
        orientation='h',
        color='Observed_vs_Expected_Difference',
        color_continuous_scale=[ACCENT_POSITIVE, PRIMARY_COLOR, ACCENT_NEGATIVE], # Custom diverging scale
        title='Average Observed vs. Expected Mortality Difference by Region',
        labels={'Observed_vs_Expected_Difference': 'Difference (%)'},
        template="plotly_white"
    )
    fig_region_diff.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_region_diff.add_vline(x=0, line_dash="dot", line_color=NEUTRAL_DARK)
    st.plotly_chart(fig_region_diff, use_container_width=True)

with col_region2:
    st.subheader("Regional Comparison Results Breakdown")
    df_region_comp = df_filtered.groupby(['Region', 'Comparison_Results_Category']).size().reset_index(name='Count')
    df_region_comp['Percentage'] = df_region_comp.groupby('Region')['Count'].transform(lambda x: x / x.sum())

    fig_region_comp = px.bar(
        df_region_comp,
        x='Region',
        y='Percentage',
        color='Comparison_Results_Category',
        title='Proportion of Hospitals by Comparison Result and Region',
        labels={'Percentage': 'Percentage of Hospitals'},
        category_orders={"Comparison_Results_Category": ['Rate higher than Statewide Rate', 'Rate not different than Statewide Rate', 'Rate lower than Statewide Rate']},
        color_discrete_map=COMP_COLORS,
        template="plotly_white"
    )
    fig_region_comp.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig_region_comp, use_container_width=True)

st.markdown("---")

# --- Analysis Area 4: Hospital-Level Performance & Outliers ---
st.header("Hospital-Level Performance & Outliers")

col_hospital1, col_hospital2 = st.columns(2)

with col_hospital1:
    st.subheader("Hospital Mortality & Volume Scatter Plot")
    fig_hospital_scatter = px.scatter(
        df_filtered,
        x='Number_of_Cases',
        y='Observed_Mortality_Rate',
        color='Comparison_Results_Category',
        hover_name='Hospital_Name',
        title='Observed Mortality Rate vs. Number of Cases by Hospital',
        labels={'Number_of_Cases': 'Total Cases', 'Observed_Mortality_Rate': 'Observed Mortality Rate (%)'},
        color_discrete_map=COMP_COLORS,
        log_x=True,
        template="plotly_white"
    )
    st.plotly_chart(fig_hospital_scatter, use_container_width=True)

with col_hospital2:
    st.subheader("Top/Bottom Hospitals by Mortality Difference")
    df_hospital_diff = df_filtered.groupby('Hospital_Name')['Observed_vs_Expected_Difference'].mean().reset_index()
    top_n = 10
    bottom_n = 10
    df_top_bottom = pd.concat([
        df_hospital_diff.nsmallest(top_n, 'Observed_vs_Expected_Difference'),
        df_hospital_diff.nlargest(bottom_n, 'Observed_vs_Expected_Difference')
    ]).sort_values(by='Observed_vs_Expected_Difference', ascending=False)

    fig_top_bottom = px.bar(
        df_top_bottom,
        x='Observed_vs_Expected_Difference',
        y='Hospital_Name',
        orientation='h',
        color='Observed_vs_Expected_Difference',
        color_continuous_scale=[ACCENT_POSITIVE, PRIMARY_COLOR, ACCENT_NEGATIVE], # Custom diverging scale
        title=f'Top {top_n} Best & Worst Hospitals by Avg. Mortality Difference',
        labels={'Observed_vs_Expected_Difference': 'Difference (%)'},
        template="plotly_white"
    )
    fig_top_bottom.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_top_bottom.add_vline(x=0, line_dash="dot", line_color=NEUTRAL_DARK)
    st.plotly_chart(fig_top_bottom, use_container_width=True)

st.markdown("---")

# --- Analysis Area 5: Confidence Intervals (Error Bars) ---
st.header("Confidence Intervals & Data Reliability")

st.subheader("Mortality Rate with Confidence Intervals by Procedure")
df_ci_proc = df_filtered.groupby('Procedure').agg(
    Observed_Mortality_Rate=('Observed_Mortality_Rate', 'mean'),
    Lower_Limit_of_Confidence_Interval=('Lower_Limit_of_Confidence_Interval', 'mean'),
    Upper_Limit_of_Confidence_Interval=('Upper_Limit_of_Confidence_Interval', 'mean')
).reset_index()

df_ci_proc['error_lower'] = df_ci_proc['Observed_Mortality_Rate'] - df_ci_proc['Lower_Limit_of_Confidence_Interval']
df_ci_proc['error_upper'] = df_ci_proc['Upper_Limit_of_Confidence_Interval'] - df_ci_proc['Observed_Mortality_Rate']

fig_ci = go.Figure(data=[
    go.Bar(
        x=df_ci_proc['Procedure'],
        y=df_ci_proc['Observed_Mortality_Rate'],
        name='Observed Mortality',
        marker_color=PRIMARY_COLOR,
        error_y=dict(
            type='data',
            symmetric=False,
            array=df_ci_proc['error_upper'],
            arrayminus=df_ci_proc['error_lower'],
            visible=True,
            color=NEUTRAL_DARK
        )
    )
])
fig_ci.update_layout(
    title='Average Observed Mortality Rate with 95% Confidence Intervals by Procedure',
    xaxis_title='Procedure',
    yaxis_title='Mortality Rate (%)',
    template="plotly_white"
)
st.plotly_chart(fig_ci, use_container_width=True)

st.subheader("Confidence Interval Width vs. Number of Cases (Hospital-Level)")
df_ci_width_hospital = df_filtered.groupby('Hospital_Name').agg(
    Avg_CI_Width=('CI_Width', 'mean'),
    Total_Cases=('Number_of_Cases', 'sum')
).reset_index()

fig_ci_width = px.scatter(
    df_ci_width_hospital,
    x='Total_Cases',
    y='Avg_CI_Width',
    hover_name='Hospital_Name',
    title='Average Confidence Interval Width vs. Total Cases by Hospital',
    labels={'Total_Cases': 'Total Cases', 'Avg_CI_Width': 'Average Confidence Interval Width (%)'},
    log_x=True,
    template="plotly_white",
    color_discrete_sequence=[PRIMARY_COLOR]
)
st.plotly_chart(fig_ci_width, use_container_width=True)

st.markdown("---")
st.info("Data source: Cardiac Surgery and Percutaneous Coronary Interventions by Hospital: Beginning 2008")