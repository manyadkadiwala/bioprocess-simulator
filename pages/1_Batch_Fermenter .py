import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Batch Fermenter", layout="wide")

st.title("Batch Fermenter — Monod Kinetics")
st.caption(
    "Coupled ODE simulation of biomass growth and substrate depletion · RK4 solver"
)

# ── Sidebar: parameters ──────────────────────────────────────────────────────

st.sidebar.header("Model parameters")

st.sidebar.subheader("Kinetic constants")
mu_max = st.sidebar.slider(
    "μmax — max specific growth rate (hr⁻¹)",
    min_value=0.05, max_value=0.60,
    value=0.26, step=0.01,
    help="Upper limit of growth rate when substrate is not limiting"
)
Ks = st.sidebar.slider(
    "Ks — Monod constant (g/L)",
    min_value=0.05, max_value=2.0,
    value=0.315, step=0.005,
    help="Substrate concentration where μ = μmax / 2"
)
Ysx = st.sidebar.slider(
    "Ysx — yield coefficient (g substrate / g biomass)",
    min_value=1.0, max_value=30.0,
    value=14.3, step=0.1,
    help="How much substrate is consumed per unit of biomass formed"
)

st.sidebar.subheader("Initial conditions")
X0 = st.sidebar.slider("X₀ — initial biomass (g/L)", 0.1, 10.0, 1.0, 0.1)
S0 = st.sidebar.slider("S₀ — initial substrate (g/L)", 10.0, 400.0, 200.0, 5.0)

st.sidebar.subheader("Simulation settings")
t_end = st.sidebar.slider("Stop time (hr)", 5, 72, 24, 1)

# ── Model: Monod ODEs ────────────────────────────────────────────────────────

def monod_odes(t, y, mu_max, Ks, Ysx):
    X, S = y
    X = max(X, 0)
    S = max(S, 0)
    mu = mu_max * S / (Ks + S)
    dXdt = mu * X
    dSdt = -Ysx * mu * X
    return [dXdt, dSdt]

# ── Solve ────────────────────────────────────────────────────────────────────

sol = solve_ivp(
    fun=monod_odes,
    t_span=(0, t_end),
    y0=[X0, S0],
    args=(mu_max, Ks, Ysx),
    method="RK45",
    t_eval=np.linspace(0, t_end, 500),
    max_step=0.1
)

t = sol.t
X = np.maximum(sol.y[0], 0)
S = np.maximum(sol.y[1], 0)

# ── Derived metrics ──────────────────────────────────────────────────────────

X_max = float(np.max(X))
S_final = float(S[-1])

depletion_idx = np.where(S < 0.01 * S0)[0]
t_depletion = float(t[depletion_idx[0]]) if len(depletion_idx) > 0 else t_end

mu_initial = mu_max * S0 / (Ks + S0)

# ── Metric cards ─────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
col1.metric("Max biomass", f"{X_max:.2f} g/L")
col2.metric("Substrate depleted at", f"{t_depletion:.2f} hr")
col3.metric("Final substrate", f"{S_final:.2f} g/L")
col4.metric("μ at t=0", f"{mu_initial:.4f} hr⁻¹")

st.markdown("---")

# ── Dual-axis plot ────────────────────────────────────────────────────────────
# Left axis  (y1): Substrate S — large scale
# Right axis (y2): Biomass X  — smaller scale

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Left axis — Substrate
fig.add_trace(
    go.Scatter(x=t, y=S, name="Substrate S (g/L)",
               line=dict(color="#E24B4A", width=2.5)),
    secondary_y=False
)

# Right axis — Biomass
fig.add_trace(
    go.Scatter(x=t, y=X, name="Biomass X (g/L)",
               line=dict(color="#378ADD", width=2.5, dash="dash")),
    secondary_y=True
)

# Substrate depletion marker
if t_depletion < t_end:
    fig.add_vline(
        x=t_depletion,
        line_dash="dash", line_color="gray",
        annotation_text=f"S depleted at {t_depletion:.1f} hr",
        annotation_position="top right"
    )

fig.update_yaxes(
    title_text="Substrate S (g/L)",
    secondary_y=False,
    title_font=dict(color="#E24B4A"),
    tickfont=dict(color="#E24B4A")
)
fig.update_yaxes(
    title_text="Biomass X (g/L)",
    secondary_y=True,
    title_font=dict(color="#378ADD"),
    tickfont=dict(color="#378ADD")
)
fig.update_xaxes(title_text="Time (hr)")
fig.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=440,
    margin=dict(l=20, r=20, t=40, b=20),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ── Explanation ───────────────────────────────────────────────────────────────

with st.expander("What is this model doing?"):
    st.markdown(f"""
**Monod growth model** — two coupled ODEs solved numerically using a 4th-order
Runge-Kutta method (RK45), equivalent to the SIMBAS VBA solver from HW1.

**Dual y-axis:** Substrate S (left, red) starts at {S0:.0f} g/L — much larger than
biomass X (right, blue), which starts at {X0:.1f} g/L. Splitting the axes lets both
curves show their full dynamics without the smaller one being flattened near zero.

**State variables:**
- **X** — biomass concentration (g/L). Grows as cells consume substrate.
- **S** — substrate concentration (g/L). Decreases as cells grow.

**Governing equations:**

$$\\frac{{dX}}{{dt}} = \\mu \\cdot X \\qquad \\frac{{dS}}{{dt}} = -Y_{{sx}} \\cdot \\mu \\cdot X$$

where the specific growth rate follows Monod kinetics:

$$\\mu = \\frac{{\\mu_{{max}} \\cdot S}}{{K_s + S}}$$

**Current parameters:**
- μmax = {mu_max} hr⁻¹ — controls how fast cells grow at saturating substrate
- Ks = {Ks} g/L — substrate concentration where μ = μmax/2; lower = efficient growth at low S
- Ysx = {Ysx} g substrate/g biomass — substrate consumed per gram of biomass formed
""")
