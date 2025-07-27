# 🫀 Cardiac Care Performance Dashboard

## Overview

This project presents a comprehensive data analysis and interactive dashboard focused on **Cardiac Surgery and Percutaneous Coronary Interventions (PCI) performance by hospital, spanning from 2008 onwards.** Leveraging real-world healthcare data, this dashboard aims to provide actionable insights into trends, regional disparities, hospital-level outcomes, and the overall quality of cardiac care.

The goal is to empower healthcare administrators, policymakers, and medical researchers with a clear, data-driven understanding of performance, enabling informed decisions to optimize patient outcomes and resource allocation.

## Live Dashboards

Experience the interactive dashboards:

- **Streamlit Cloud App:** https://cardiac-care-performance-dashboard.streamlit.app
- **Tableau Public Dashboard:** https://public.tableau.com/app/profile/yamin3547/viz/Cardiac_Care_Peformance_and_Outcomes_Analysis/Dashboard1

## Project Goal & Impact

The primary objective of this project is to transform raw, complex healthcare data into clear, digestible insights. By analyzing performance metrics like mortality rates and procedure volumes, we aim to:

- **Identify Trends:** Understand how cardiac care delivery and outcomes have evolved over time.
- **Benchmark Performance:** Compare hospitals and regions against state-wide averages and expected outcomes.
- **Spot Outliers:** Pinpoint high-performing institutions (potential best practices) and areas needing intervention.
- **Inform Decisions:** Provide data-backed insights for improving quality of care, optimizing resource distribution, and guiding patient choice.

## Data Source

The analysis is based on a real-world dataset detailing Cardiac Surgery and Percutaneous Coronary Interventions by Hospital, beginning in 2008. Key columns include:

- `Facility_ID`, `Hospital_Name`
- `Detailed_Region`, `Region`
- `Procedure` (e.g., All PCI, Non-Emergency PCI, Valve or Valve/CABG)
- `Year_of_Hospital_Discharge` (including year ranges like '2013-2015')
- `Number_of_Cases`, `Number_of_Deaths`
- `Observed_Mortality_Rate`, `Expected_Mortality_Rate`, `Risk_Adjusted_Mortality_Rate`
- `Lower_Limit_of_Confidence_Interval`, `Upper_Limit_of_Confidence_Interval`
- `Comparison_Results`

**Data Source:** https://health.data.ny.gov/Health/Cardiac-Surgery-and-Percutaneous-Coronary-Interven/jtip-2ccj/about_data

## Technical Overview

- **Data Analysis & Preprocessing:** Python (Pandas, NumPy)
- **Interactive Dashboard (Streamlit):** Python (Streamlit, Plotly Express, Plotly Graph Objects)
- **Interactive Dashboard (Tableau):** Tableau Desktop / Tableau Public
- **Styling:** Custom CSS, Google Fonts ("Inter")
- **Deployment:** Streamlit Cloud

## Data Preparation & Feature Engineering

The raw data underwent a robust cleaning and feature engineering process to prepare it for analysis:

- **Column Renaming:** Standardized column names for easier access (e.g., `Number_of_Cases`).
- **Data Type Conversion:** Ensured all numerical fields were correctly typed, handling missing values gracefully.
- **Year Range Handling:** The `Year_of_Hospital_Discharge` column, which contained both single years (e.g., '2016') and year ranges (e.g., '2013-2015'), was processed to extract `Start_Year`, `End_Year`, and `Mid_Year`. For time-series analysis, the `Start_Year` was primarily used to represent the data point.
- **Performance Flags:** Created boolean flags (`Is_Higher_Than_Expected_Mortality`, `Is_Lower_Than_Expected_Mortality`, `Is_As_Expected_Mortality`) from `Comparison_Results` for easy filtering and visual highlighting.
- **Difference Metrics:** Calculated `Observed_vs_Expected_Difference` and `Observed_vs_RiskAdjusted_Difference` to quantify performance deviation from expected benchmarks.
- **Confidence Interval Width:** Derived `CI_Width` to assess the reliability and precision of mortality rate estimates.

## Key Analysis & Insights (The Story)

Through the interactive dashboards, several critical insights into cardiac care performance were uncovered:

1.  **Evolving Procedure Landscape:**

    - **Insight:** The dashboard clearly shows trends in procedure volumes over time. For instance, we can observe if PCI procedures have steadily increased while traditional cardiac surgeries (like Valve/CABG) have remained stable or decreased, reflecting shifts in medical practice.
    - **Visualization:** "Procedure Volume Trend" line chart.

2.  **Overall Mortality Improvement (and Persistent Gaps):**

    - **Insight:** While overall `Observed_Mortality_Rate` may show a general downward trend over the years, the comparison with `Expected_Mortality_Rate` and `Risk_Adjusted_Mortality_Rate` reveals the true performance. The "Observed vs. Expected Mortality Difference Trend" helps identify if, on average, hospitals are improving faster or slower than expected risk adjustments.
    - **Visualization:** "Mortality Rate Trends" and "Observed vs. Expected Mortality Difference Trend" line charts.

3.  **Regional Disparities in Care:**

    - **Insight:** Significant variations exist in cardiac care outcomes across different geographic `Region`s. Some regions consistently demonstrate average `Observed_vs_Expected_Difference` values that are better (negative difference) or worse (positive difference) than others. The "Regional Comparison Results Breakdown" further highlights the proportion of hospitals within each region falling into "Higher than Expected" mortality categories.
    - **Visualization:** "Regional Mortality Performance" bar chart (diverging colors) and "Regional Comparison Results Breakdown" stacked bar chart.

4.  **The Volume-Outcome Relationship & Hospital Outliers:**

    - **Insight:** The analysis often reveals a correlation where hospitals performing a higher `Number_of_Cases` tend to have lower `Observed_Mortality_Rate`s (the "volume-outcome" relationship). However, this isn't always absolute. The dashboard helps identify specific `Hospital_Name`s that are outliers – either performing exceptionally well (lower than expected mortality despite volume) or unexpectedly poorly.
    - **Visualization:** "Hospital Mortality & Volume Scatter Plot" (color-coded by `Comparison_Results_Category`) and "Top/Bottom Hospitals by Mortality Difference" bar chart.

5.  **Understanding Data Reliability with Confidence Intervals:**

    - **Insight:** For hospitals with a low `Number_of_Cases`, their `Observed_Mortality_Rate` often has a very wide `CI_Width`, indicating less statistical certainty in that rate. This is crucial for interpreting performance; a seemingly high mortality rate in a low-volume center might not be statistically significant.
    - **Visualization:** "Confidence Interval Width vs. Number of Cases (Hospital-Level)" scatter plot and "Mortality Rate with Confidence Intervals by Procedure" bar chart.

## Dashboard Features (Streamlit App)

The Streamlit dashboard offers an intuitive user experience with:

- **Interactive Filters:** Select `Year Range`, `Region`, `Procedure`, and `Hospital` from the sidebar to drill down into specific data segments. The "Overall" option allows viewing aggregated data.
- **Dynamic KPIs:** Four key performance indicators at the top provide an immediate snapshot of total procedures, average mortality, average deviation from expected, and Year-over-Year mortality change.
- **Consistent Cyan Theme:** A custom color palette inspired by cardiac health visuals ensures a cohesive and professional aesthetic across all charts and elements.
- **Responsive Design:** The dashboard adapts to different screen sizes, providing a seamless experience on desktop and mobile.
- **Plotly Interactivity:** All charts are built with Plotly, offering zoom, pan, hover tooltips, and data export functionalities.

## How to Run Locally

To run this Streamlit application on your local machine:

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/RobinMillford/Cardiac-Care-Performance-Dashboard.git
    cd Cardiac-Care-Performance-Dashboard
    ```

    (If not using Git, download the project files and navigate to the directory.)

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Create a `requirements.txt` file in your project's root directory with the following content:

    ```
    streamlit
    pandas
    plotly
    numpy
    ```

    Then install:

    ```bash
    pip install -r requirements.txt
    ```

    **Important Note:** If you previously generated `requirements.txt` from a Windows environment, ensure `pywin32` is **NOT** included in this file, as it will cause deployment errors on Linux systems.

4.  **Place Data File:**
    Ensure your `cardiac_data_cleaned_engineered.csv` file is in the same directory as your `dashboard.py` script.

5.  **Run the App:**

    ```bash
    streamlit run dashboard.py
    ```

    This will open the dashboard in your default web browser.

## Future Enhancements

- **Detailed Hospital Profiles:** Implement a drill-down feature to show a dedicated page or section for a selected hospital, including all its historical data and comparisons.
- **Statistical Significance Indicators:** Add more explicit visual indicators or text to charts to denote statistical significance, especially around confidence intervals and comparison results.
- **Patient Risk Stratification:** If more granular patient-level data were available (anonymized), a project could involve building a basic risk stratification model.
- **Geospatial Analysis:** Integrate a map visualization (e.g., using `st.map` or `pydeck`) to show regional performance directly on a geographical map.
- **User Feedback/Interaction:** Add a simple feedback mechanism or a way for users to request specific analyses.
