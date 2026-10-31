import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BioMat CodeLab | Scaffold Mission", page_icon="🔬", layout="wide")

st.markdown("""
<style>
.main-header {padding:1.1rem 1.25rem;border-radius:16px;background:linear-gradient(120deg,#123b50,#257c7b);color:white;margin-bottom:1rem}
.main-header h1 {margin:0;font-size:2.1rem}
.main-header p {margin:.35rem 0 0 0;opacity:.95}
.mission-card {padding:1rem;border:1px solid rgba(128,128,128,.35);border-radius:12px;margin-bottom:.75rem}
</style>
""", unsafe_allow_html=True)

# Synthetic values are for learning only, not real-world biomaterial selection.
DEFAULT_MATERIALS = pd.DataFrame([
    {"Material":"Scaffold A","Material family":"Hydrogel","Porosity (%)":72,"Elastic modulus (MPa)":22,"Degradation (weeks)":8,"Cell viability (%)":91,"Pore size (µm)":180,"Cost (relative units)":2.0},
    {"Material":"Scaffold B","Material family":"Polymer","Porosity (%)":58,"Elastic modulus (MPa)":35,"Degradation (weeks)":12,"Cell viability (%)":87,"Pore size (µm)":120,"Cost (relative units)":1.5},
    {"Material":"Scaffold C","Material family":"Composite","Porosity (%)":80,"Elastic modulus (MPa)":14,"Degradation (weeks)":6,"Cell viability (%)":95,"Pore size (µm)":250,"Cost (relative units)":3.0},
    {"Material":"Scaffold D","Material family":"Hydrogel","Porosity (%)":66,"Elastic modulus (MPa)":48,"Degradation (weeks)":16,"Cell viability (%)":84,"Pore size (µm)":160,"Cost (relative units)":2.2},
    {"Material":"Scaffold E","Material family":"Ceramic-polymer","Porosity (%)":75,"Elastic modulus (MPa)":42,"Degradation (weeks)":10,"Cell viability (%)":89,"Pore size (µm)":210,"Cost (relative units)":3.4},
    {"Material":"Scaffold F","Material family":"Polymer","Porosity (%)":69,"Elastic modulus (MPa)":28,"Degradation (weeks)":9,"Cell viability (%)":93,"Pore size (µm)":195,"Cost (relative units)":1.8},
    {"Material":"Scaffold G","Material family":"Composite","Porosity (%)":62,"Elastic modulus (MPa)":18,"Degradation (weeks)":14,"Cell viability (%)":96,"Pore size (µm)":145,"Cost (relative units)":2.7},
    {"Material":"Scaffold H","Material family":"Hydrogel","Porosity (%)":84,"Elastic modulus (MPa)":8,"Degradation (weeks)":5,"Cell viability (%)":90,"Pore size (µm)":280,"Cost (relative units)":1.9},
])
REQUIRED = ["Material","Material family","Porosity (%)","Elastic modulus (MPa)","Degradation (weeks)","Cell viability (%)","Pore size (µm)","Cost (relative units)"]

def init_state():
    defaults = {"xp":0, "completed":set(), "mission_complete":False, "selected_material":None, "criteria":None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def award(task, points):
    if task not in st.session_state.completed:
        st.session_state.completed.add(task)
        st.session_state.xp += points

def validate_data(df):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}", None
    clean = df.copy()
    numeric = [c for c in REQUIRED if c not in ("Material","Material family")]
    for col in numeric:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    if clean[numeric].isna().any().any():
        return False, "Numeric columns contain blank or non-numeric values.", None
    if not clean["Porosity (%)"].between(0,100).all():
        return False, "Porosity must be between 0 and 100.", None
    if not clean["Cell viability (%)"].between(0,100).all():
        return False, "Cell viability must be between 0 and 100.", None
    if (clean[["Elastic modulus (MPa)","Degradation (weeks)","Pore size (µm)","Cost (relative units)"]] < 0).any().any():
        return False, "Modulus, degradation, pore size, and cost cannot be negative.", None
    if clean["Material"].astype(str).str.strip().eq("").any():
        return False, "Every row needs a material name.", None
    return True, "Dataset valid.", clean

def filter_candidates(df, p, e, d, v, pore):
    mask = (
        df["Porosity (%)"].between(p[0], p[1])
        & df["Elastic modulus (MPa)"].between(e[0], e[1])
        & df["Degradation (weeks)"].between(d[0], d[1])
        & (df["Cell viability (%)"] >= v)
        & df["Pore size (µm)"].between(pore[0], pore[1])
    )
    return df.loc[mask].copy()

init_state()
with st.sidebar:
    st.title("🔬 BioMat CodeLab")
    st.caption("Final Mission · Tissue Engineering")
    st.metric("XP earned", st.session_state.xp)
    st.progress(min(st.session_state.xp / 400, 1.0))
    st.write(f"**Tasks completed:** {len(st.session_state.completed)}")
    page = st.radio("Navigate", ["Mission briefing","Explore dataset","Build your filter","Visualize candidates","Python playground","Submit final design"])
    st.divider()
    uploaded = st.file_uploader("Optional: upload a CSV", type=["csv"])
    if st.button("Reset mission progress", use_container_width=True):
        for k in ["xp","completed","mission_complete","selected_material","criteria"]:
            st.session_state.pop(k, None)
        st.rerun()

materials = DEFAULT_MATERIALS.copy()
if uploaded is not None:
    try:
        raw = pd.read_csv(uploaded)
        ok, message, cleaned = validate_data(raw)
        if ok:
            materials = cleaned
            st.sidebar.success("Uploaded CSV loaded.")
        else:
            st.sidebar.error(message)
    except Exception as exc:
        st.sidebar.error(f"Could not read CSV: {exc}")

st.markdown("""
<div class="main-header">
<h1>🧫 Design a Tissue-Engineering Scaffold</h1>
<p>Use Python to inspect data, filter candidate biomaterials, visualize trade-offs, and defend a data-informed choice.</p>
</div>
""", unsafe_allow_html=True)
st.warning("Educational prototype only: all built-in data and thresholds are synthetic examples, not validated criteria for clinical or real-world material selection.")

if page == "Mission briefing":
    st.subheader("Your role: junior biomaterials researcher")
    st.write("A tissue-engineering scaffold can provide a temporary structure for cells while tissue develops. A candidate may need suitable porosity, mechanical properties, degradation behaviour, and cell compatibility. The right values depend on the intended tissue and application.")
    for heading, desc in [
        ("1 · Inspect","Explore the fictional material-property dataset."),
        ("2 · Define constraints","Set acceptable ranges for the target application."),
        ("3 · Filter","Use Python conditions to identify candidates meeting all requirements."),
        ("4 · Compare","Visualize candidates and discuss trade-offs."),
        ("5 · Defend","Choose a candidate and explain limitations.")
    ]:
        st.markdown(f'<div class="mission-card"><b>{heading}</b><br>{desc}</div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.metric("Python", "Conditions & masks")
    b.metric("Data", "Pandas")
    c.metric("Visualization", "Plotly")
    if st.button("Complete briefing (+25 XP)", type="primary"):
        award("briefing",25)
        st.success("Briefing complete. XP is awarded only once per session.")

elif page == "Explore dataset":
    st.subheader("Step 1 — Explore the dataset")
    st.dataframe(materials, use_container_width=True, hide_index=True)
    definitions = {
        "Porosity (%)":"Percentage of scaffold volume represented by pores.",
        "Elastic modulus (MPa)":"A measure of stiffness; target values depend on the tissue.",
        "Degradation (weeks)":"Illustrative time scale for material degradation.",
        "Cell viability (%)":"Synthetic cell-viability indicator used in this exercise.",
        "Pore size (µm)":"Illustrative characteristic pore size.",
        "Cost (relative units)":"Made-up relative index, not a market price."
    }
    st.markdown("### Variable guide")
    for term, definition in definitions.items():
        with st.expander(term):
            st.write(definition)
    st.caption(f"{len(materials)} candidates · Synthetic teaching dataset")
    if st.button("Dataset explored (+25 XP)", type="primary"):
        award("explore",25)
        st.success("Exploration complete.")

elif page == "Build your filter":
    st.subheader("Step 2 — Define your scaffold requirements")
    st.write("A candidate passes only if it satisfies **every** selected criterion.")
    left,right = st.columns(2)
    with left:
        st.markdown("#### Materials Science")
        p = st.slider("Acceptable porosity (%)",0,100,(60,80))
        e = st.slider("Elastic modulus (MPa)",0.0,100.0,(10.0,50.0),step=1.0)
        pore = st.slider("Pore size (µm)",0,500,(100,300),step=10)
    with right:
        st.markdown("#### Biotechnology")
        d = st.slider("Degradation time (weeks)",0,52,(6,16))
        v = st.slider("Minimum cell viability (%)",0,100,85)
    st.session_state.criteria = {"p":p,"e":e,"pore":pore,"d":d,"v":v}
    passing = filter_candidates(materials,p,e,d,v,pore)
    x,y = st.columns(2)
    x.metric("Passing candidates",len(passing))
    y.metric("Candidates assessed",len(materials))
    if passing.empty:
        st.info("No candidate meets every current constraint. Relax a criterion and compare again.")
    else:
        st.success(f"{len(passing)} candidate(s) pass the filter.")
        st.dataframe(passing,use_container_width=True,hide_index=True)
    with st.expander("Python concept: Boolean masks"):
        st.code("""mask = (
    df["Porosity (%)"].between(porosity_min, porosity_max)
    & df["Elastic modulus (MPa)"].between(modulus_min, modulus_max)
    & (df["Cell viability (%)"] >= minimum_viability)
)
candidates = df.loc[mask]""",language="python")
        st.write("Comparisons produce True/False values. `&` combines conditions, and `df.loc[mask]` keeps rows where the combined mask is True.")
    if st.button("Filter built (+50 XP)",type="primary"):
        award("filter",50)
        st.success("Filter challenge complete.")

elif page == "Visualize candidates":
    st.subheader("Step 3 — Compare candidates visually")
    cr = st.session_state.criteria or {"p":(60,80),"e":(10.0,50.0),"pore":(100,300),"d":(6,16),"v":85}
    passing = filter_candidates(materials,cr["p"],cr["e"],cr["d"],cr["v"],cr["pore"])
    if passing.empty:
        st.info("No candidates pass the current filter. Visit Build your filter to adjust criteria.")
    else:
        fig = px.scatter(passing,x="Elastic modulus (MPa)",y="Cell viability (%)",size="Porosity (%)",color="Material family",hover_name="Material",hover_data=["Porosity (%)","Degradation (weeks)","Pore size (µm)","Cost (relative units)"],title="Stiffness vs cell viability")
        st.plotly_chart(fig,use_container_width=True)
        fig2 = px.bar(passing,x="Material",y=["Porosity (%)","Cell viability (%)"],barmode="group",title="Porosity and cell viability")
        st.plotly_chart(fig2,use_container_width=True)
    st.markdown("### Think like a scientist")
    st.write("- Does the highest viability candidate also have suitable stiffness?")
    st.write("- Do these values guarantee performance in a living system?")
    st.write("- What additional tests would be required?")
    if st.button("Visualization reviewed (+50 XP)",type="primary"):
        award("visualize",50)
        st.success("Visualization challenge complete.")

elif page == "Python playground":
    st.subheader("Step 4 — Practice Python logic")
    st.write("Review the starter code. This learning app intentionally does not execute arbitrary user-entered Python.")
    st.code("""# materials is a pandas DataFrame
porosity_min, porosity_max = 60, 80
modulus_min, modulus_max = 10, 50
minimum_viability = 85

mask = (
    materials["Porosity (%)"].between(porosity_min, porosity_max)
    & materials["Elastic modulus (MPa)"].between(modulus_min, modulus_max)
    & (materials["Cell viability (%)"] >= minimum_viability)
)
candidates = materials.loc[mask]
print(candidates[["Material", "Porosity (%)",
                  "Elastic modulus (MPa)", "Cell viability (%)"]])""",language="python")
    answer = st.radio("What does `materials.loc[mask]` do?",[
        "Keeps rows where the mask is True",
        "Sorts materials alphabetically",
        "Changes missing values to zero",
        "Plots the DataFrame automatically"
    ],index=None)
    if st.button("Check answer"):
        if answer == "Keeps rows where the mask is True":
            award("quiz",25)
            st.success("Correct! `loc` selects rows using the Boolean mask. +25 XP.")
        elif answer is None:
            st.warning("Choose an answer first.")
        else:
            st.error("Not quite. Think about how a Boolean mask selects rows.")
    with st.expander("Hint"):
        st.write("A mask contains True/False values. Pandas uses it to select matching rows.")

elif page == "Submit final design":
    st.subheader("Final mission — Defend your scaffold choice")
    st.write("Choose a candidate that passes the current teaching criteria and justify your decision.")
    cr = st.session_state.criteria or {"p":(60,80),"e":(10.0,50.0),"pore":(100,300),"d":(6,16),"v":85}
    passing = filter_candidates(materials,cr["p"],cr["e"],cr["d"],cr["v"],cr["pore"])
    if passing.empty:
        st.warning("No candidates currently pass. Adjust the filter first.")
    else:
        selected = st.selectbox("Candidate",passing["Material"].tolist())
        row = passing.loc[passing["Material"] == selected].iloc[0]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Porosity",f'{row["Porosity (%)"]:.0f}%')
        c2.metric("Modulus",f'{row["Elastic modulus (MPa)"]:.1f} MPa')
        c3.metric("Degradation",f'{row["Degradation (weeks)"]:.0f} weeks')
        c4.metric("Cell viability",f'{row["Cell viability (%)"]:.0f}%')
        justification = st.text_area("Defend your choice (at least two sentences)",placeholder="I selected this scaffold because... One limitation is...",height=130)
        limitations = st.multiselect("Select at least two limitations to consider",[
            "The dataset is synthetic and small",
            "The criteria may not match a specific tissue",
            "Cell viability alone does not prove biocompatibility",
            "Mechanical performance may change during degradation",
            "Sterility, immune response, and in-vivo performance need separate evaluation"
        ])
        if st.button("Submit final design",type="primary"):
            if len(justification.strip()) < 40:
                st.error("Please write at least two meaningful sentences (40 characters or more).")
            elif len(limitations) < 2:
                st.error("Select at least two limitations.")
            else:
                st.session_state.selected_material = selected
                st.session_state.mission_complete = True
                award("final",250)
                st.success("Mission complete! +250 XP.")
                st.balloons()
        if st.session_state.mission_complete:
            st.markdown("### 🏆 Mission complete!")
            st.write(f"Selected teaching-example candidate: **{st.session_state.selected_material}**")
            st.info("This is a learning result, not a validated recommendation for a real tissue-engineering application.")

st.divider()
st.caption(f"BioMat CodeLab · Synthetic educational dataset · Current XP: {st.session_state.xp}")
