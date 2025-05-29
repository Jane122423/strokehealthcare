import streamlit as st
import pandas as pd
import plotly.express as px

# --- Set page config FIRST ---
st.set_page_config(page_title="Stroke Data Dashboard", layout="wide")

# --- Load & clean dataset ---
@st.cache_data
def load_data():
    df = pd.read_csv("STROKE_HEALTHCARE_CLEANED_DATA.csv")
    df.columns = [
        'ID', 'Gender', 'Age', 'Hypertension', 'Heart Disease', 'Ever Married',
        'Work Type', 'Residence Type', 'Avg Glucose Level', 'BMI', 'Smoking Status',
        'Stroke'
    ]
    # Map categorical variables for better readability
    gender_map = {0: 'Female', 1: 'Male'}
    work_type_map = {0: 'Never Worked', 1: 'Private', 2: 'Self-employed', 3: 'Govt Job', 4: 'Children'}
    residence_type_map = {0: 'Rural', 1: 'Urban'}
    smoking_status_map = {0: 'Unknown', 1: 'Formerly Smoked', 2: 'Never Smoked', 3: 'Smokes'}

    df['Gender'] = df['Gender'].map(gender_map)
    df['Work Type'] = df['Work Type'].map(work_type_map)
    df['Residence Type'] = df['Residence Type'].map(residence_type_map)
    df['Smoking Status'] = df['Smoking Status'].map(smoking_status_map)
    return df

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filters")
age_range = st.sidebar.slider(
    "Select Age Range:",
    min_value=int(df['Age'].min()),
    max_value=int(df['Age'].max()),
    value=(int(df['Age'].min()), int(df['Age'].max()))
)

selected_genders = st.sidebar.multiselect(
    "Select Gender:",
    options=df['Gender'].dropna().unique(),
    default=df['Gender'].dropna().unique()
)

selected_smoking = st.sidebar.multiselect(
    "Select Smoking Status:",
    options=df['Smoking Status'].dropna().unique(),
    default=df['Smoking Status'].dropna().unique()
)

# --- Filter dataframe ---
filtered_df = df[
    (df['Age'] >= age_range[0]) &
    (df['Age'] <= age_range[1]) &
    (df['Gender'].isin(selected_genders)) &
    (df['Smoking Status'].isin(selected_smoking))
]

# --- Main title ---
st.title("Stroke Data Dashboard")

# --- KPI cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Patients", f"{df.shape[0]:,}")
col2.metric("Average Glucose Level", f"{df['Avg Glucose Level'].mean():.2f}")
col3.metric("Average BMI", f"{df['BMI'].mean():.2f}")
col4.metric("Stroke Cases", f"{df['Stroke'].sum():,}")

st.markdown("---")

# --- Charts ---
st.subheader("Gender Distribution")
gender_counts = filtered_df['Gender'].value_counts()
fig_gender = px.pie(
    values=gender_counts.values,
    names=gender_counts.index,
    title="Gender Distribution",
    hole=0.4
)
st.plotly_chart(fig_gender, use_container_width=True)

st.subheader("Stroke Cases by Age")
stroke_by_age = filtered_df.groupby(['Age', 'Stroke']).size().unstack(fill_value=0)
fig_stroke_age = px.bar(
    stroke_by_age,
    x=stroke_by_age.index,
    y=[0, 1],
    barmode='group',
    labels={'x': 'Age', 'value': 'Count'},
    title="Stroke Cases by Age"
)
st.plotly_chart(fig_stroke_age, use_container_width=True)

st.subheader("Hypertension vs Heart Disease")
counts = {
    'Hypertension': filtered_df['Hypertension'].sum(),
    'Heart Disease': filtered_df['Heart Disease'].sum(),
    'Neither': len(filtered_df) - filtered_df['Hypertension'].sum() - filtered_df['Heart Disease'].sum()
}
fig_hypertension_heart = px.pie(
    values=list(counts.values()),
    names=list(counts.keys()),
    title="Hypertension vs Heart Disease",
    hole=0.4
)
st.plotly_chart(fig_hypertension_heart, use_container_width=True)

st.subheader("Average Glucose Level by Age")
avg_glucose_by_age = filtered_df.groupby('Age')['Avg Glucose Level'].mean().reset_index()
fig_glucose_age = px.line(
    avg_glucose_by_age,
    x='Age',
    y='Avg Glucose Level',
    title="Average Glucose Level by Age"
)
st.plotly_chart(fig_glucose_age, use_container_width=True)

st.subheader("BMI Distribution by Gender")
fig_bmi_gender = px.box(
    filtered_df,
    x='Gender',
    y='BMI',
    color='Gender',
    title="BMI Distribution by Gender"
)
st.plotly_chart(fig_bmi_gender, use_container_width=True)

# --- Insights Section ---
st.markdown("---")
st.header("Insights")

st.markdown("""
- The average glucose level across all patients is approximately {:.2f}.
- The average BMI across all patients is approximately {:.2f}.
- The most common smoking status among patients is **{}**.
- The percentage of patients with hypertension is approximately {:.2f}%.
- The percentage of patients with heart disease is approximately {:.2f}%.
- The stroke rate among patients is approximately {:.2f}%.
""".format(
    df['Avg Glucose Level'].mean(),
    df['BMI'].mean(),
    df['Smoking Status'].mode()[0],
    100 * df['Hypertension'].mean(),
    100 * df['Heart Disease'].mean(),
    100 * df['Stroke'].mean()
))

st.markdown("""
**Recommendations:**

- Encourage regular health check-ups for patients above a certain age.
- Focus on preventive measures for patients with hypertension or heart disease.
- Promote awareness campaigns about the risks of smoking.
""")