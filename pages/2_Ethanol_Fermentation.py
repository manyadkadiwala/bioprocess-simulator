import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Ethanol Fermentation", layout="wide")

st.title("Ethanol Fermentation — Inhibition Kinetics")
st.caption(
    "Batch ethanol production with Monod growth and ethanol inhibition"
    
)

# ── Sidebar: parameters ──────────────────────────────────────────────────────

st.sidebar.header("Model parameters")

st.sidebar.subheader("Kinetic constants")
mu_max = st.sidebar.slider(
    "μmax — max specific growth rate (hr⁻¹)",
    min_value=0.05, max_value=0.80,
    value=0.40, step=0.01
)
Ks = st.sidebar.slider(
    "Ks — Monod constant (g/L)",
    min_value=0.05, max_value=5.0,
    value=0.315, step=0.005
)
nu_m = st.sidebar.slider(
    "νm — max specific ethanol production rate (g ethanol / g biomass / hr)",
    min_value=0.1, max_value=3.0,
    value=1.15, step=0.05,
    help="Scales how fast ethanol is produced per unit biomass. Used directly in dP/dt."
)

st.sidebar.subheader("Inhibition parameters")
P_max = st.sidebar.slider(
    "Pmax — max ethanol tolerance (g/L)",
    min_value=50.0, max_value=150.0,
    value=87.5, step=1.0,
    help="Ethanol concentration at which growth and production completely stop"
)
n = st.sidebar.slider(
    "n — inhibition exponent",
    min_value=0.1, max_value=3.0,
    value=0.36, step=0.02,
    help="Higher n = inhibition kicks in later and more sharply"
)

st.sidebar.subheader("Yield coefficients")
E = st.sidebar.slider(
    "E — cell yield on ethanol (g biomass / g ethanol)",
    min_value=0.05, max_value=0.80,
    value=0.249, step=0.005,
    help="How much biomass forms per unit ethanol produced (links dX/dt to dP/dt)"
)
Yxs = st.sidebar.slider(
    "Yxs — biomass yield on substrate (g biomass / g substrate)",
    min_value=0.01, max_value=0.20,
    value=0.07, step=0.005
)

st.sidebar.subheader("Initial conditions")
X0  = st.sidebar.slider("X₀ — initial biomass (g/L)", 0.1, 5.0, 1.0, 0.1)
S0  = st.sidebar.slider("S₀ — initial glucose (g/L)", 50.0, 300.0, 150.0, 5.0)
P0  = st.sidebar.slider("P₀ — initial ethanol (g/L)", 0.0, 10.0, 0.0, 0.5)

st.sidebar.subheader("Simulation settings")
t_end = st.sidebar.slider("Stop time (hr)", 5, 48, 24, 1)

# ── Model ODEs ───────────────────────────────────────────────────────────────
# Matches the HW2 VBA structure exactly:
#   nuE  = nu_m * (S / (Ks + S)) * inhibition   ← specific ethanol production rate
#   dP/dt = nuE * X                               ← ethanol production
#   dX/dt = E  * dP/dt                            ← biomass growth coupled to ethanol
#   dS/dt = -(1/Yxs) * dX/dt                     ← substrate consumption
#   dC/dt = (44/46) * dP/dt                       ← CO₂ from stoichiometry

def ethanol_odes(t, y, mu_max, Ks, nu_m, P_max, n, E, Yxs):
    X, S, P, C = y
    X = max(X, 0)
    S = max(S, 0)
    P = max(P, 0)

    # Ethanol inhibition: (1 - P/Pmax)^n, clamped to zero above Pmax
    inhibition = max(1.0 - (P / P_max), 0.0) ** n

    # Specific ethanol production rate (g ethanol / g biomass / hr)
    nuE = nu_m * (S / (Ks + S)) * inhibition

    dPdt = nuE * X                    # ethanol production
    dXdt = E * dPdt                   # biomass growth
    dSdt = -(1.0 / Yxs) * dXdt       # substrate consumption
    dCdt = (44.0 / 46.0) * dPdt      # CO₂ from C₆H₁₂O₆ → 2 C₂H₅OH + 2 CO₂

    return [dXdt, dSdt, dPdt, dCdt]

# ── Solve ────────────────────────────────────────────────────────────────────

sol = solve_ivp(
    fun=ethanol_odes,
    t_span=(0, t_end),
    y0=[X0, S0, P0, 0.0],
    args=(mu_max, Ks, nu_m, P_max, n, E, Yxs),
    method="RK45",
    t_eval=np.linspace(0, t_end, 600),
    max_step=0.05
)

t   = sol.t
X   = np.maximum(sol.y[0], 0)
S   = np.maximum(sol.y[1], 0)
P   = np.maximum(sol.y[2], 0)
CO2 = np.maximum(sol.y[3], 0)

# ── Metrics ──────────────────────────────────────────────────────────────────

theoretical_max = 0.511 * S0          # g ethanol / g glucose × initial glucose
P_max_achieved  = float(np.max(P))
X_max           = float(np.max(X))
CO2_final       = float(CO2[-1])
pct_theoretical = (P_max_achieved / theoretical_max) * 100 if theoretical_max > 0 else 0

depletion_idx = np.where(S < 0.01 * S0)[0]
t_depletion   = float(t[depletion_idx[0]]) if len(depletion_idx) > 0 else t_end

col1, col2, col3, col4 = st.columns(4)
col1.metric("Max ethanol",      f"{P_max_achieved:.1f} g/L")
col2.metric("Theoretical max",  f"{theoretical_max:.1f} g/L",
            delta=f"{pct_theoretical:.0f}% achieved")
col3.metric("Max biomass",      f"{X_max:.1f} g/L")
col4.metric("Total CO₂",        f"{CO2_final:.1f} g/L")

st.markdown("---")

# ── Dual-axis plot ────────────────────────────────────────────────────────────
# Left axis  (y1): Glucose S  — large scale (0 → S0)
# Right axis (y2): Biomass X, Ethanol P, CO2 — smaller scale
# Theoretical max ethanol line goes on the RIGHT axis (where P is plotted)

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Left axis — Glucose
fig.add_trace(
    go.Scatter(x=t, y=S, name="Glucose S (g/L)",
               line=dict(color="#E24B4A", width=2.5)),
    secondary_y=False
)

# Right axis — Biomass, Ethanol, CO2
fig.add_trace(
    go.Scatter(x=t, y=X, name="Biomass X (g/L)",
               line=dict(color="#378ADD", width=2.5)),
    secondary_y=True
)
fig.add_trace(
    go.Scatter(x=t, y=P, name="Ethanol P (g/L)",
               line=dict(color="#1D9E75", width=2.5)),
    secondary_y=True
)
fig.add_trace(
    go.Scatter(x=t, y=CO2, name="CO₂ (g/L)",
               line=dict(color="#BA7517", width=2, dash="dot")),
    secondary_y=True
)

# Theoretical max ethanol — plotted as a trace on the RIGHT axis
# (add_hline doesn't support secondary_y reliably, so we use a scatter line)
fig.add_trace(
    go.Scatter(
        x=[t[0], t[-1]],
        y=[theoretical_max, theoretical_max],
        name=f"Theoretical max ethanol ({theoretical_max:.1f} g/L)",
        line=dict(color="gray", width=1.5, dash="dash"),
        mode="lines"
    ),
    secondary_y=True
)

# Substrate depletion vertical marker
if t_depletion < t_end:
    fig.add_vline(
        x=t_depletion,
        line_dash="dash", line_color="gray",
        annotation_text=f"Glucose depleted at {t_depletion:.1f} hr",
        annotation_position="top left"
    )

fig.update_yaxes(
    title_text="Glucose S (g/L)",
    secondary_y=False,
    title_font=dict(color="#E24B4A"),
    tickfont=dict(color="#E24B4A")
)
fig.update_yaxes(
    title_text="Biomass / Ethanol / CO₂ (g/L)",
    secondary_y=True,
    title_font=dict(color="#378ADD"),
    tickfont=dict(color="#555")
)
fig.update_xaxes(title_text="Time (hr)")
fig.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=460,
    margin=dict(l=20, r=20, t=40, b=20),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ── Sensitivity analysis ─────────────────────────────────────────────────────

st.markdown("---")
st.subheader("Sensitivity analysis")
st.caption("See how the final ethanol yield changes as you vary one parameter at a time.")

sens_param = st.selectbox(
    "Parameter to vary",
    ["n — inhibition exponent",
     "νm — max specific ethanol production rate",
     "E — cell yield on ethanol"]
)

param_ranges = {
    "n — inhibition exponent":                  np.linspace(0.1, 3.0, 30),
    "νm — max specific ethanol production rate": np.linspace(0.1, 3.0, 30),
    "E — cell yield on ethanol":                np.linspace(0.05, 0.80, 30),
}

sweep = param_ranges[sens_param]
final_ethanol = []

for val in sweep:
    if "n —" in sens_param:
        args = (mu_max, Ks, nu_m, P_max, val, E, Yxs)
    elif "νm —" in sens_param:
        args = (mu_max, Ks, val, P_max, n, E, Yxs)
    else:
        args = (mu_max, Ks, nu_m, P_max, n, val, Yxs)

    s = solve_ivp(
        ethanol_odes, (0, t_end), [X0, S0, P0, 0.0],
        args=args, method="RK45",
        t_eval=np.linspace(0, t_end, 200),
        max_step=0.1
    )
    final_ethanol.append(float(np.max(np.maximum(s.y[2], 0))))

current_val = {"n —": n, "νm —": nu_m, "E —": E}

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=sweep, y=final_ethanol,
    mode="lines+markers",
    line=dict(color="#1D9E75", width=2.5),
    marker=dict(size=5)
))
for k, v in current_val.items():
    if k in sens_param:
        fig2.add_vline(
            x=v, line_dash="dash", line_color="#378ADD",
            annotation_text="Current value",
            annotation_position="top right"
        )

fig2.update_layout(
    xaxis_title=sens_param.split("—")[0].strip(),
    yaxis_title="Max ethanol achieved (g/L)",
    height=300,
    margin=dict(l=20, r=20, t=20, b=20)
)
st.plotly_chart(fig2, use_container_width=True)

# ── Explanation ───────────────────────────────────────────────────────────────

with st.expander("What is this model doing?"):
    st.markdown(f"""
**Ethanol fermentation model** — matches the HW2 VBA structure exactly. Four coupled ODEs:

| Variable | Equation | Meaning |
|---|---|---|
| Ethanol P | dP/dt = νE · X | νE scales with substrate and inhibition |
| Biomass X | dX/dt = E · dP/dt | growth coupled to ethanol production |
| Substrate S | dS/dt = −(1/Yxs) · dX/dt | consumed as cells grow |
| CO₂ C | dC/dt = (44/46) · dP/dt | stoichiometric from fermentation |

**Specific ethanol production rate νE:**

$$\\nu_E = \\nu_m \\cdot \\frac{{S}}{{K_s + S}} \\cdot \\left(1 - \\frac{{P}}{{P_{{max}}}}\\right)^n$$

Note that **νm** (the slider) directly scales dP/dt — changing it changes how fast ethanol
accumulates. The previous version of this code accidentally left νm unused; this is now fixed.

**Theoretical maximum ethanol** from stoichiometry (C₆H₁₂O₆ → 2 C₂H₅OH + 2 CO₂):

$$Y_{{eth/glc}}^{{theo}} = \\frac{{2 \\times 46}}{{180}} = 0.511 \\text{{ g/g}}$$

For S₀ = {S0:.0f} g/L → theoretical max = **{theoretical_max:.1f} g/L**.
Simulation achieved **{P_max_achieved:.1f} g/L ({pct_theoretical:.0f}%)**.

The gap from 100% is due to substrate diverted to biomass growth and the ethanol
inhibition term slowing production before all glucose is consumed.
""")
