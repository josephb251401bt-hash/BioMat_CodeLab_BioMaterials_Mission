# BioMat CodeLab — Bio-Materials Mission

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.

## Features
- Mission briefing and learning objectives
- Synthetic scaffold-property dataset and optional CSV upload
- CSV validation
- User-controlled filters for porosity, modulus, degradation, viability, and pore size
- Interactive Plotly charts
- Python Boolean-mask tutorial and quiz
- Final candidate selection, written justification, XP, and progress

## CSV columns required
`Material`, `Material family`, `Porosity (%)`, `Elastic modulus (MPa)`, `Degradation (weeks)`, `Cell viability (%)`, `Pore size (µm)`, `Cost (relative units)`.

## Important
All default data and thresholds are synthetic teaching examples. Do not use this app for clinical, regulatory, or real-world material selection. Arbitrary user code is not executed.
