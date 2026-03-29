import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import os
import tempfile

# =========================
# OPTIONAL REPORTLAB SAFETY
# =========================
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter
    REPORTLAB_OK = True
except:
    REPORTLAB_OK = False


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Energy Systems Research Simulator",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Energy Systems Policy Simulator (Final Research Build)")
st.caption("Hybrid simulation + real-world dataset energy transition model")


# =========================
# CONTEXT
# =========================
st.markdown("""
### 🌍 Model Framework
- IPCC AR6 mitigation pathways
- IEA Net Zero Emissions scenarios
- UN SDG 7 / 9 / 13 energy goals
- Global LCOE benchmarking
""")


# =========================
# SIDEBAR
# =========================
scenario = st.sidebar.selectbox(
    "Scenario",
    ["Custom", "Net Zero", "Nuclear Heavy", "Renewable Heavy", "Hydrogen Future"]
)

data_mode = st.sidebar.selectbox(
    "Data Mode",
    ["Simulated Model", "Real-World Dataset Mode"]
)

scenarios = {
    "Net Zero": (40, 30, 20, 10),
    "Nuclear Heavy": (70, 10, 10, 10),
    "Renewable Heavy": (20, 50, 25, 5),
    "Hydrogen Future": (25, 20, 15, 40),
    "Custom": None
}

if scenario == "Custom":
    nuclear = st.sidebar.slider("Nuclear", 0, 100, 40)
    solar = st.sidebar.slider("Solar", 0, 100, 25)
    wind = st.sidebar.slider("Wind", 0, 100, 20)
    hydrogen = st.sidebar.slider("Hydrogen", 0, 100, 15)
else:
    nuclear, solar, wind, hydrogen = scenarios[scenario]

if nuclear + solar + wind + hydrogen != 100:
    st.warning("Energy mix must equal 100%")
    st.stop()


# =========================
# REAL WORLD DATA
# =========================
real_world_data = {
    "Nuclear": {"emissions": 12, "cost": 155, "reliability": 92},
    "Solar": {"emissions": 45, "cost": 45, "reliability": 45},
    "Wind": {"emissions": 15, "cost": 50, "reliability": 55},
    "Hydrogen": {"emissions": 60, "cost": 110, "reliability": 65}
}


# =========================
# MODEL
# =========================
class EnergyModel:
    def emissions(self, n, s, w, h):
        return (n*5 + s*12 + w*10 + h*45) / 100

    def cost(self, n, s, w, h):
        return (n*140 + s*45 + w*50 + h*120) / 100

    def reliability(self, n, s, w, h):
        return (n*95 + s*40 + w*55 + h*70) / 100


model = EnergyModel()


# =========================
# METRICS
# =========================
if data_mode == "Real-World Dataset Mode":
    em_base = (
        nuclear * real_world_data["Nuclear"]["emissions"] +
        solar * real_world_data["Solar"]["emissions"] +
        wind * real_world_data["Wind"]["emissions"] +
        hydrogen * real_world_data["Hydrogen"]["emissions"]
    ) / 100

    cost_base = (
        nuclear * real_world_data["Nuclear"]["cost"] +
        solar * real_world_data["Solar"]["cost"] +
        wind * real_world_data["Wind"]["cost"] +
        hydrogen * real_world_data["Hydrogen"]["cost"]
    ) / 100

    rel_base = (
        nuclear * real_world_data["Nuclear"]["reliability"] +
        solar * real_world_data["Solar"]["reliability"] +
        wind * real_world_data["Wind"]["reliability"] +
        hydrogen * real_world_data["Hydrogen"]["reliability"]
    ) / 100
else:
    em_base = model.emissions(nuclear, solar, wind, hydrogen)
    cost_base = model.cost(nuclear, solar, wind, hydrogen)
    rel_base = model.reliability(nuclear, solar, wind, hydrogen)


risk_base = cost_base * 0.4 + (100 - rel_base) * 0.6


# =========================
# FORECAST
# =========================
years = np.arange(2030, 2051)

em_t = [em_base * (1 + i * 0.01) for i in range(len(years))]
cost_t = [cost_base * (1 + i * 0.005) for i in range(len(years))]
rel_t = [rel_base * (1 - i * 0.002) for i in range(len(years))]

co2_t = [em_base * (100 * (1.02 ** i)) for i in range(len(years))]


# =========================
# MONTE CARLO
# =========================
results = []

for _ in range(300):
    n = nuclear + np.random.normal(0, 3)
    s = solar + np.random.normal(0, 3)
    w = wind + np.random.normal(0, 3)
    h = hydrogen + np.random.normal(0, 3)

    total = n + s + w + h
    if total <= 0:
        continue

    n, s, w, h = [max(0, x) / total * 100 for x in [n, s, w, h]]

    e = model.emissions(n, s, w, h)
    c = model.cost(n, s, w, h)
    r = model.reliability(n, s, w, h)

    risk = c * 0.4 + (100 - r) * 0.6
    results.append([e, c, r, risk])


results = np.array(results)

mean = np.mean(results, axis=0) if len(results) > 0 else np.zeros(4)
std = np.std(results, axis=0) if len(results) > 0 else np.zeros(4)


# =========================
# REPORT GRAPH (UNCHANGED + UNITS ADDED IN DISPLAY)
# =========================
def make_report_graph():
    fig, ax = plt.subplots()
    ax.bar(
        ["Emissions (gCO2/kWh)", "Cost ($/MWh)", "Reliability (%)", "Risk Index"],
        mean
    )
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp.name)
    plt.close()
    return tmp.name


# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Forecast", "Uncertainty", "Report"])


# =========================
# OVERVIEW (EXPANDED - NO REMOVALS)
# =========================
with tab1:
    st.subheader("System Overview")

    st.metric("Emissions (gCO2/kWh)", f"{em_base:.2f}")
    st.metric("Cost ($/MWh)", f"{cost_base:.2f}")
    st.metric("Reliability (%)", f"{rel_base:.2f}")
    st.metric("Risk Index", f"{risk_base:.2f}")

    # ADDED GRAPH (kept overview graph requirement)
    st.markdown("### 📊 Overview System Snapshot")
    fig, ax = plt.subplots()
    ax.bar(
        ["Emissions", "Cost", "Reliability", "Risk"],
        [em_base, cost_base, rel_base, risk_base]
    )
    ax.set_ylabel("Value (mixed units / normalized index)")
    st.pyplot(fig)


with tab2:
    st.markdown("### 📈 Forecast Over Time (Units Included)")
    st.line_chart({
        "Emissions (gCO2/kWh)": em_t,
        "Cost ($/MWh)": cost_t,
        "Reliability (%)": rel_t
    })


with tab3:
    st.write("Mean (Emissions, Cost, Reliability, Risk):", mean)
    st.write("Std Dev:", std)


# =========================
# REPORT
# =========================
with tab4:
    st.subheader("Policy Report Generator")

    analysis = """
    This system shows trade-offs between cost, emissions, and reliability.
    Nuclear reduces emissions but increases cost rigidity.
    Renewables reduce emissions but increase variability.
    Hydrogen increases flexibility but adds cost volatility.
    """

    text = f"""
Scenario: {scenario}
Mode: {data_mode}

Emissions: {em_base:.2f} gCO2/kWh
Cost: {cost_base:.2f} $/MWh
Reliability: {rel_base:.2f} %

Monte Carlo:
Mean Risk: {mean[3]:.2f}

Analysis:
{analysis}

Framework:
IPCC AR6, IEA Net Zero, UN SDGs
"""

    st.write(text)

    def create_pdf():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        content = []
        content.append(Paragraph("Energy Systems Report", styles["Title"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph(text, styles["Normal"]))
        content.append(Spacer(1, 12))

        img = make_report_graph()
        content.append(RLImage(img, width=400, height=250))

        doc.build(content)
        buffer.seek(0)
        return buffer


    if REPORTLAB_OK and st.button("Generate PDF"):
        pdf = create_pdf()
        st.download_button("Download", pdf, file_name="energy_report.pdf")
    elif not REPORTLAB_OK:
        st.warning("Install reportlab: pip3 install reportlab")


# =========================
# REFERENCES (UNCHANGED)
# =========================
st.markdown("""
---

## 📚 Academic & Institutional References

- International Energy Agency (IEA), *Net Zero by 2050 Roadmap* (2023–2025 updates)
- IPCC Sixth Assessment Report (AR6), Working Group III – Mitigation of Climate Change
- United Nations, Sustainable Development Goals Framework (SDG 7, 9, 13)
- Lazard, *Levelized Cost of Energy Analysis (Version 17–18)*
- World Nuclear Association, nuclear lifecycle emissions datasets
- IEA Hydrogen Projects Database (Global Hydrogen Review)

⚠️ This tool is a **research-grade educational simulation model**, not a physical grid optimizer.

---

Made by Ooreoluwanimi E. Moronkeji
""")