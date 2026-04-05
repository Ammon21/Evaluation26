import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import os

if not os.path.exists("encoded_teacher_evaluations.csv"):
    st.error("CSV file missing!")
    st.stop()

if os.path.exists("assets/logo.png"):
    st.sidebar.image("assets/logo.png", width=120)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Teachers Dashboard", page_icon="📊", layout="wide")

# --- LOAD DATA ---
dfx = pd.read_csv("encoded_teacher_evaluations.csv")

# Drop Response number if exists
if 'Response number' in dfx.columns:
    dfx = dfx.drop(columns=['Response number'])

# Fix teacher names
replacements = {
    'Aeser': 'Aser Mesfine', 'Acer': 'Aser Mesfine', 'Alelgn Damtew': 'Alelegne Damtew',
    'Ayenew Tdese': 'Ayenew Tadesse', 'Bililegne': 'Bililegne Assefa', 'Endalk Asfaw': 'Endalkachew Assefa',
    'Etagegnehu': 'Etagegnehu Degsew', 'Eyob': 'Eyob Teshome', 'Frew': 'Firew Teklu',
    'Getnet': 'Getnet Alelign', 'Mohammedaman': 'Mohammadaman', 'Mr.Samuel': 'Samuel',
    'Sintayehu Wondat': 'Sintayehu W', 'Sintayehu': 'Sintayehu W', 'Tefri': 'Teferi Getahun',
    'Teshager': 'Teshager Belehu'
}
dfx['Teacher Name'] = dfx['Teacher Name'].replace(replacements)

# --- Convert all rating columns to numeric ---
non_rating_cols = ['Grade', 'Section', 'Teacher Name']
rating_columns = [col for col in dfx.columns if col not in non_rating_cols]
dfx[rating_columns] = dfx[rating_columns].apply(pd.to_numeric, errors='coerce')

# --- SIDEBAR ---
st.sidebar.image("assets/logo.png", width=120)
st.sidebar.title("Dashboard Pages")
page = st.sidebar.radio("Select Page:", ["Front Page", "Teacher Ranking", "Strengths & Weaknesses"])

# --- FRONT PAGE ---
def front_page():
    st.markdown("""
        <style>
            .title {font-size: 36px; font-weight: 800; color: #0D47A1; text-align: center; margin-bottom: 20px;}
            .circle {border: 6px solid #3498db; border-radius: 50%; width: 180px; height: 180px;
                     display: flex; justify-content: center; align-items: center;
                     color: #0D47A1; font-size: 36px; font-weight: 700; margin: 0 auto 20px auto;}
            .subheader {font-size: 22px; font-weight: 700; color: #1565C0; margin-top: 20px; text-align: center;}
            .footer {text-align:center; color: gray; margin-top: 30px; font-size:14px;}
            .highlight-card {background: linear-gradient(135deg, #85c1e9, #3498db); color: white; border-radius: 12px;
                              padding: 20px; margin:10px; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title">Teachers Evaluation Dashboard</div>', unsafe_allow_html=True)

    # Teacher selection
    teacher_list = dfx['Teacher Name'].unique()
    selected_teacher = st.selectbox("Select Teacher", teacher_list)

    # Average score for selected teacher
    teacher_data = dfx[dfx['Teacher Name'] == selected_teacher]
    avg_score = teacher_data[rating_columns].mean().mean()

    st.markdown(f'<div class="circle">{avg_score:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subheader">Selected Teacher: {selected_teacher}</div>', unsafe_allow_html=True)

    # Top 6 teachers overall
    teacher_avgs = dfx.groupby('Teacher Name')[rating_columns].mean().mean(axis=1).sort_values(ascending=False)
    top6 = teacher_avgs.head(6)
    cols = st.columns(3)
    for i, (teacher, score) in enumerate(top6.items()):
        with cols[i % 3]:
            st.markdown(f'<div class="highlight-card"><h3>{teacher}</h3><p>Avg Score: {score:.2f}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="footer">Designed by Ammon | Data Analyst | 2026</div>', unsafe_allow_html=True)


# --- TEACHER RANKING PAGE ---
def teacher_ranking_page():
    st.markdown("""
        <style>
            .subheader {font-size: 22px; font-weight: 700; color: #1565C0; margin:10px 0;}
            .highlight-card {background: linear-gradient(135deg, #85c1e9, #3498db); color: white; border-radius: 12px;
                              padding: 10px; margin:5px; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);}
        </style>
    """, unsafe_allow_html=True)

    st.title("🏅 Teacher Ranking")

    # Compute overall average per teacher
    dfx['Overall_Avg'] = dfx[rating_columns].mean(axis=1)

    # Best teachers per grade
    grade_teacher_avg = dfx.groupby(['Grade','Teacher Name'])['Overall_Avg'].mean().reset_index()
    best_per_grade = grade_teacher_avg.loc[grade_teacher_avg.groupby('Grade')['Overall_Avg'].idxmax()]

    st.markdown("<div class='subheader'>Top Teachers per Grade (Overall Average)</div>", unsafe_allow_html=True)
    grades = best_per_grade['Grade'].unique()
    for grade in grades:
        grade_data = best_per_grade[best_per_grade['Grade'] == grade]
        st.markdown(f"### Grade {grade}")
        cols = st.columns(len(grade_data))
        for i, row in grade_data.iterrows():
            with cols[i % len(cols)]:
                st.markdown(f"""
                    <div class="highlight-card">
                        <h4>{row['Teacher Name']}</h4>
                        <p>Avg Score: {row['Overall_Avg']:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)

    # Overall ranking
    st.markdown("<div class='subheader'>All Teachers Ranking (Overall Average)</div>", unsafe_allow_html=True)
    teacher_final_avg = dfx.groupby('Teacher Name')['Overall_Avg'].mean().reset_index()
    teacher_final_avg = teacher_final_avg.sort_values('Overall_Avg', ascending=False)
    st.dataframe(teacher_final_avg.style.background_gradient(subset=['Overall_Avg'], cmap='Blues'))


# --- STRENGTHS & WEAKNESSES PAGE ---
def strengths_weaknesses_page():
    st.title("💡 Strengths & Weaknesses")
    
    teacher_list = dfx['Teacher Name'].unique()
    selected_teacher = st.selectbox("Select Teacher", teacher_list, key="strength_teacher")
    
    teacher_data = dfx[dfx['Teacher Name'] == selected_teacher]
    avg_scores = teacher_data[rating_columns].mean()
    
    # Strength: top 5
    strengths = avg_scores.sort_values(ascending=False).head(5)
    weaknesses = avg_scores.sort_values(ascending=True).head(5)
    
    st.markdown("### 🌟 Top Strengths")
    st.table(strengths.reset_index().rename(columns={'index':'Question', 0:'Avg Score'}))
    
    st.markdown("### ⚠️ Top Weaknesses")
    st.table(weaknesses.reset_index().rename(columns={'index':'Question', 0:'Avg Score'}))
    
    # Radar chart
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=avg_scores.tolist(),
        theta=rating_columns,
        fill='toself',
        line=dict(color='rgba(93, 164, 214, 0.9)', width=3),
        fillcolor='rgba(93, 164, 214, 0.5)',
        name=selected_teacher
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,5])),
        showlegend=False,
        margin=dict(t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)


# --- PAGE NAVIGATION ---
if page == "Front Page":
    front_page()
elif page == "Teacher Ranking":
    teacher_ranking_page()
elif page == "Strengths & Weaknesses":
    strengths_weaknesses_page()