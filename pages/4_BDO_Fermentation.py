import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="2,3-BDO Fermentation", layout="wide")

st.title("2,3-Butanediol Fermentation — Two-Phase Model")
st.caption(
    "Aerobic → anaerobic phase switch triggered by oxygen limitation"
)

st.markdown(
    "This model has **two distinct phases**: an aerobic growth phase where cells "
    "multiply rapidly using oxygen, and an anaerobic production phase where oxygen "
    "becomes limiting and cells switch to producing 2,3-butanediol. "
    "The phase transition is automatically detected and marked on the plot."
)
st.markdown("---")

# ── Sidebar parameters ────────────────────────────────────────────────────────

st.sidebar.header("Model parameters")

st.sidebar.subheader("Growth kinetics")
pmax = st.sidebar.slider(
    "μmax — max specific growth rate (hr⁻¹)",
    min_value=0.10, max_value=1.50, value=0.52, step=0.01,
    help="Aerobic phase only — exponential growth rate"
)
YATPmax = st.sidebar.slider(
    "YATPmax — max biomass yield on ATP (g/mol)",
    min_value=5.0, max_value=20.0, value=11.0, step=0.5
)
kd = st.sidebar.slider(
    "kd — product inhibition constant",
    min_value=0.001, max_value=0.050, value=0.0077, step=0.001,
    help="Higher kd = 2,3-BDO inhibits growth more strongly in anaerobic phase"
)

st.sidebar.subheader("Oxygen transfer")
kLaCstar = st.sidebar.slider(
    "kLa·C* — O₂ transfer limit (g/L/hr)",
    min_value=0.005, max_value=0.100, value=0.027, step=0.001,
    help="Maximum oxygen supply rate. When O₂ demand exceeds this, the phase switches."
)

st.sidebar.subheader("Maintenance coefficients")
me1 = st.sidebar.slider(
    "me1 — aerobic maintenance (gS/gX·hr)",
    min_value=0.010, max_value=0.150, value=0.047, step=0.001
)
me2 = st.sidebar.slider(
    "me2 — anaerobic maintenance (gS/gX·hr)",
    min_value=0.001, max_value=0.050, value=0.017, step=0.001
)

st.sidebar.subheader("Initial conditions")
X0_bdo    = st.sidebar.slider("X₀ — initial biomass (g/L)", 0.001, 1.0, 0.01, 0.001)
S0_bdo    = st.sidebar.slider("S₀ — initial xylose (g/L)", 20.0, 200.0, 100.0, 5.0)
t_end_bdo = st.sidebar.slider("Simulation time (hr)", 20, 100, 60, 5)

MWxyl = 150.13
MWbd  = 90.12

# ── ODE with phase detection ──────────────────────────────────────────────────

def bdo_odes(t, y, pmax, YATPmax, kd, kLaCstar, me1, me2, phase_state):
    X, S, P = y
    X = max(X, 0); S = max(S, 0); P = max(P, 0)

    if not phase_state["limited"]:
        # Phase 1: Aerobic exponential growth
        dXdt = pmax * X
        Qsa  = (1.0 / 120.0) * dXdt
        QATP = (1.0 / YATPmax) * dXdt + me1 * X
        Qsr  = (3.0 / 70.0) * QATP
        Qsf  = 0.0
        if 5.0 * Qsr >= 0.999 * kLaCstar:
            phase_state["limited"]  = True
            phase_state["Xl"]       = X
            phase_state["t_switch"] = t
    else:
        # Phase 2: Anaerobic BDO production
        Xl = phase_state["Xl"]
        if S <= 0.001:
            return [0.0, 0.0, 0.0]
        dXdt = max((pmax - kd * P) * Xl, 0.0)
        Qsa  = (1.0 / 120.0) * dXdt
        Qsf  = max((18.0 / 25.0) * (
            (1.0 / YATPmax) * dXdt + me2 * X - (14.0 / 3.0) * kLaCstar
        ), 0.0)
        Qsr  = max((1.0 / 10.0) * (2.0 * kLaCstar - (5.0 / 6.0) * Qsf), 0.0)

    dSdt = -(Qsa + Qsr + Qsf) * MWxyl
    dPdt =  (5.0 / 6.0) * Qsf * MWbd
    return [dXdt, dSdt, dPdt]

phase_state = {"limited": False, "Xl": 0.0, "t_switch": None}

sol = solve_ivp(
    lambda t, y: bdo_odes(t, y, pmax, YATPmax, kd, kLaCstar, me1, me2, phase_state),
    t_span=(0, t_end_bdo),
    y0=[X0_bdo, S0_bdo, 0.0],
    method="RK45",
    t_eval=np.linspace(0, t_end_bdo, 1200),
    max_step=0.05
)

t = sol.t
X = np.maximum(sol.y[0], 0)
S = np.maximum(sol.y[1], 0)
P = np.maximum(sol.y[2], 0)

t_switch = phase_state.get("t_switch")

# ── Derived metrics ───────────────────────────────────────────────────────────

dep_idx    = np.where(S < 0.01 * S0_bdo)[0]
t_ferm     = float(t[dep_idx[0]])     if len(dep_idx) > 0 else t_end_bdo
X_final    = float(X[dep_idx[0]])     if len(dep_idx) > 0 else float(X[-1])
P_final    = float(np.max(P))
proc_yield = P_final / S0_bdo
theo_yield = 0.5 * MWbd / MWxyl
metabolic_pct = (proc_yield / theo_yield) * 100

# ── Metric cards ──────────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
c1.metric("Final cell mass",   f"{X_final:.2f} g/L",      help="HW4: 10.86 g/L")
c2.metric("Final 2,3-BDO",     f"{P_final:.2f} g/L",      help="HW4: 39.10 g/L")
c3.metric("Fermentation time", f"{t_ferm:.2f} hr",        help="HW4: 25.85 hr")
c4.metric("Process yield",     f"{proc_yield:.3f} kg/kg", help="HW4: 0.391 kg/kg")

c5, c6, c7, c8 = st.columns(4)
c5.metric("O₂ limiting at",
          f"{t_switch:.2f} hr" if t_switch else "—",
          help="HW4: 12.80 hr")
c6.metric("Metabolic yield",     f"{metabolic_pct:.1f}%",       help="HW4: 85.8%")
c7.metric("Theoretical BDO max", f"{theo_yield * S0_bdo:.1f} g/L",
          help="0.5 × MWbd/MWxyl × S₀")
c8.metric("Xl at O₂ transition",
          f"{phase_state['Xl']:.3f} g/L" if phase_state['Xl'] else "—",
          help="Biomass locked in at the moment of phase switch")

st.markdown("---")

# ── Dual-axis plot ────────────────────────────────────────────────────────────

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(x=t, y=S, name="Xylose S (g/L)",
               line=dict(color="#E24B4A", width=2.5)),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=t, y=X, name="Biomass X (g/L)",
               line=dict(color="#378ADD", width=2.5)),
    secondary_y=True
)
fig.add_trace(
    go.Scatter(x=t, y=P, name="2,3-BDO P (g/L)",
               line=dict(color="#1D9E75", width=2.5)),
    secondary_y=True
)

if t_switch:
    fig.add_vline(
        x=t_switch,
        line_dash="dash", line_color="#BA7517", line_width=2,
        annotation_text=f"O₂ limiting at {t_switch:.1f} hr → BDO production begins",
        annotation_position="top right",
        annotation_font=dict(color="#BA7517", size=12)
    )

if t_ferm < t_end_bdo:
    fig.add_vline(
        x=t_ferm,
        line_dash="dot", line_color="gray",
        annotation_text=f"Xylose depleted at {t_ferm:.1f} hr",
        annotation_position="top left"
    )

fig.update_yaxes(
    title_text="Xylose S (g/L)", secondary_y=False,
    title_font=dict(color="#E24B4A"), tickfont=dict(color="#E24B4A")
)
fig.update_yaxes(
    title_text="Biomass X / 2,3-BDO P (g/L)", secondary_y=True,
    title_font=dict(color="#378ADD"), tickfont=dict(color="#555")
)
fig.update_xaxes(title_text="Time (hr)")
fig.update_layout(
    title="Batch 2,3-Butanediol Fermentation Simulation",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=480,
    margin=dict(l=20, r=20, t=60, b=20),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("What is the two-phase model doing?"):
    st.markdown(f"""
**Phase 1 — Aerobic (before the orange dashed line):**
Cells grow exponentially at μmax = {pmax} hr⁻¹, consuming xylose via aerobic respiration.
The phase ends when oxygen demand from the growing cell mass exceeds the maximum
transfer rate kLa·C* = {kLaCstar} g/L/hr. At that moment Xl = {phase_state['Xl']:.3f} g/L
is locked in — cells stop multiplying.

**Phase 2 — Anaerobic (after the orange line):**
Without enough oxygen, cells switch metabolism to fermentation, channelling carbon into
**2,3-butanediol**. Biomass growth slows (inhibited by BDO via kd = {kd}) but BDO
accumulates rapidly until xylose is exhausted.

**What to try:**
- **Lower kLa·C*** → phase switches earlier, less biomass builds up, less BDO produced
- **Raise μmax** → cells hit the O₂ limit faster, transition happens sooner
- **Raise kd** → BDO inhibits anaerobic growth more, slowing production late in run
- **Raise S₀** → more xylose fed, fermentation runs longer, more BDO ultimately produced

**Industrial relevance:** 2,3-BDO is a platform chemical for plastics, solvents, and
jet fuel precursors. The two-phase strategy — grow cells aerobically first, then trigger
production by oxygen starvation — is central to making the process economically viable.
The scale-up implications of this are explored in the **Scale-Up Calculator** page.
""")
