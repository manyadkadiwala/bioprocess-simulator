import streamlit as st
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.stats import linregress
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="CSTBR Analyzer", layout="wide")

st.title("CSTBR Analyzer - Parameter Estimation & Transient Simulation")
st.caption(
    "Lineweaver–Burk regression to estimate Monod kinetic parameters · "
    "Transient CSTBR simulation with maintenance"
)

# ── Real HW3 experimental data ───────────────────────────────────────────────
# Fermenter: V = 0.8 L (800 mL working volume)

DEFAULT_DATA = pd.DataFrame([
    # S0 = 200
    [50,  200, 2.60, 6.25],
    [60,  200, 3.06, 6.76],
    [70,  200, 3.93, 7.26],
    [80,  200, 4.50, 7.22],
    [90,  200, 5.26, 8.11],
    [100, 200, 6.10, 8.47],
    [120, 200, 8.26, 8.41],
    [200, 200,27.31, 9.17],
    # S0 = 100
    [50,  100, 2.52, 2.95],
    [60,  100, 3.08, 3.36],
    [70,  100, 3.96, 3.40],
    [80,  100, 4.65, 3.69],
    [90,  100, 5.27, 3.83],
    [100, 100, 6.61, 4.04],
    [120, 100, 8.25, 4.06],
    [200, 100,27.48, 3.88],
    # S0 = 50
    [50,   50, 2.48, 1.40],
    [60,   50, 3.01, 1.57],
    [70,   50, 3.67, 1.63],
    [80,   50, 4.83, 1.75],
    [90,   50, 5.20, 1.85],
    [100,  50, 6.30, 1.79],
    [120,  50, 8.36, 1.91],
    [200,  50,25.97, 1.16],
    # S0 = 10
    [50,   10, 2.53, 0.24],
    [60,   10, 3.27, 0.23],
    [70,   10, 3.67, 0.23],
    [80,   10, 4.41, 0.20],
    [90,   10, 5.20, 1.71],
    [100,  10, 6.53, 1.82],
    [120,  10, 8.74, 1.82],
    [200,  10,10.00, 0.00],
    # S0 = 5
    [50,    5, 2.60, 0.07],
    [60,    5, 3.09, 0.06],
    [70,    5, 4.03, 1.66],
    [80,    5, 4.83, 1.72],
    [90,    5, 5.00, 0.00],
    [100,   5, 5.00, 0.00],
    [120,   5, 5.00, 0.00],
    [200,   5, 5.00, 0.00],
], columns=["F (mL/hr)", "S0 (g/L)", "S_ss (g/L)", "X_ss (g/L)"])

V_reactor = 0.8  # L

# ── Tabs ─────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📈 Lineweaver–Burk Regression", "⚙️ Transient CSTBR Simulation"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Lineweaver–Burk
# ════════════════════════════════════════════════════════════════════════════

with tab1:

    st.subheader("Estimating μmax and Km from Steady-State CSTBR Data")
    st.markdown(
        "At steady state in a CSTBR, **μ = D** (dilution rate). "
        "The Lineweaver–Burk transformation linearises the Monod equation so "
        "μmax and Km can be read from the slope and intercept of a 1/μ vs 1/S plot. "
        "**Edit any cell in the table below** — the regression and all four parameters update instantly."
    )

    st.markdown("---")

    col_table, col_filter = st.columns([3, 1])

    with col_filter:
        st.markdown("**Regression filters**")
        x_min_filter = st.number_input(
            "Exclude X_ss below (g/L)",
            value=0.5, min_value=0.0, max_value=5.0, step=0.1,
            help="Near-washout rows have very low X — small measurement errors get "
                 "amplified when you take 1/S and 1/μ, so they're excluded."
        )
        s0_options = sorted(DEFAULT_DATA["S0 (g/L)"].unique().tolist())
        s0_selected = st.multiselect(
            "Include S0 values in L-B regression",
            options=s0_options,
            default=[200, 100, 50],
            help="Which feed concentrations to include. Try removing S0=5 and S0=10 to see R² improve."
        )
        yield_s0 = st.selectbox(
            "S0 for yield/maintenance regression",
            options=[s for s in s0_options if s in s0_selected] or s0_options,
            index=0,
            help="The yield regression uses one S0 dataset. HW3 used S0=50."
        )

    with col_table:
        st.markdown("**Experimental steady-state data** — edit any cell and watch the regression update")
        edited_df = st.data_editor(
            DEFAULT_DATA,
            use_container_width=True,
            num_rows="dynamic",
            height=340,
            key="hw3_data_editor"
        )

    # ── Compute D ─────────────────────────────────────────────────────────────

    df = edited_df.copy()
    df["D (hr⁻¹)"] = (df["F (mL/hr)"] / 1000.0) / V_reactor

    # ── Lineweaver–Burk regression ────────────────────────────────────────────

    lb_mask = (
        (df["X_ss (g/L)"] > x_min_filter) &
        (df["S0 (g/L)"].isin(s0_selected)) &
        (df["S_ss (g/L)"] > 0) &
        (df["D (hr⁻¹)"] > 0)
    )
    df_lb = df[lb_mask].copy()
    df_lb["1/μ"] = 1.0 / df_lb["D (hr⁻¹)"]
    df_lb["1/S"] = 1.0 / df_lb["S_ss (g/L)"]

    if len(df_lb) >= 2:
        slope_LB, intercept_LB, r_lb, _, _ = linregress(df_lb["1/S"], df_lb["1/μ"])
        mu_max_est = 1.0 / intercept_LB if intercept_LB > 0 else float("nan")
        Km_est     = slope_LB * mu_max_est
        R2_LB      = r_lb ** 2
    else:
        slope_LB = intercept_LB = 0
        mu_max_est = Km_est = R2_LB = float("nan")

    # ── Yield / maintenance regression ────────────────────────────────────────

    ym_mask = (
        (df["S0 (g/L)"] == yield_s0) &
        (df["X_ss (g/L)"] > x_min_filter) &
        (df["S_ss (g/L)"] > 0) &
        (df["D (hr⁻¹)"] > 0)
    )
    df_ym = df[ym_mask].copy()
    df_ym["y_norm"] = df_ym["D (hr⁻¹)"] * (yield_s0 - df_ym["S_ss (g/L)"]) / df_ym["X_ss (g/L)"]

    if len(df_ym) >= 2:
        slope_YM, intercept_YM, r_ym, _, _ = linregress(df_ym["D (hr⁻¹)"], df_ym["y_norm"])
        Ysx_est = 1.0 / slope_YM if slope_YM > 0 else float("nan")
        me_est  = intercept_YM
        R2_YM   = r_ym ** 2
    else:
        Ysx_est = me_est = R2_YM = float("nan")

    # Push to session state so Tab 2 reads them
    st.session_state["mu_max_est"] = mu_max_est
    st.session_state["Km_est"]     = Km_est
    st.session_state["Ysx_est"]    = Ysx_est
    st.session_state["me_est"]     = me_est

    # ── Parameter cards ───────────────────────────────────────────────────────

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("μmax",
              f"{mu_max_est:.5f} hr⁻¹" if not np.isnan(mu_max_est) else "—",
              help="1 / y-intercept of L-B plot")
    c2.metric("Km",
              f"{Km_est:.4f} g/L" if not np.isnan(Km_est) else "—",
              help="slope × μmax from L-B plot")
    c3.metric("Ysx",
              f"{Ysx_est:.5f} g/g" if not np.isnan(Ysx_est) else "—",
              help="1 / slope of yield regression")
    c4.metric("me",
              f"{me_est:.5f} gS/gX·hr" if not np.isnan(me_est) else "—",
              help="y-intercept of yield regression")

    if not np.isnan(R2_LB):
        st.markdown(
            f"**R² (Lineweaver–Burk):** {R2_LB:.4f} &nbsp;&nbsp; "
            f"**R² (yield regression):** {R2_YM:.4f}"
        )

    st.info(
        "💡 These four parameters are automatically passed to **Tab 2 — Transient Simulation**. "
        "Change a data point or filter above, then switch tabs to see the simulation update."
    )

    st.markdown("---")

    # ── L-B plot ──────────────────────────────────────────────────────────────

    fig_lb = go.Figure()

    df_all_valid = df[(df["S_ss (g/L)"] > 0) & (df["D (hr⁻¹)"] > 0)].copy()
    df_all_valid["1/S"] = 1.0 / df_all_valid["S_ss (g/L)"]
    df_all_valid["1/μ"] = 1.0 / df_all_valid["D (hr⁻¹)"]

    # Grey = excluded
    df_excl = df_all_valid[~df_all_valid.index.isin(df_lb.index)]
    fig_lb.add_trace(go.Scatter(
        x=df_excl["1/S"], y=df_excl["1/μ"],
        mode="markers",
        name="Excluded (near-washout or filtered S0)",
        marker=dict(color="lightgray", size=8, line=dict(color="gray", width=1))
    ))

    # Blue = included
    fig_lb.add_trace(go.Scatter(
        x=df_lb["1/S"], y=df_lb["1/μ"],
        mode="markers",
        name="Included in regression",
        marker=dict(color="#378ADD", size=9)
    ))

    if not np.isnan(mu_max_est) and len(df_lb) >= 2:
        x_line = np.linspace(0, df_lb["1/S"].max() * 1.15, 200)
        y_line = slope_LB * x_line + intercept_LB
        fig_lb.add_trace(go.Scatter(
            x=x_line, y=y_line, mode="lines",
            name=f"Linear fit (R²={R2_LB:.4f})",
            line=dict(color="#E24B4A", width=2, dash="dot")
        ))
        fig_lb.add_annotation(
            x=0, y=intercept_LB,
            text=(f"y-intercept = {intercept_LB:.4f}<br>"
                  f"→ μmax = {mu_max_est:.5f} hr⁻¹"),
            showarrow=True, arrowhead=2, ax=110, ay=-50,
            font=dict(size=12), bgcolor="white", bordercolor="#E24B4A"
        )

    fig_lb.update_layout(
        title="Lineweaver–Burk Plot — 1/μ vs 1/S",
        xaxis_title="1/S  (L/g)",
        yaxis_title="1/μ  (hr)",
        height=420,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_lb, use_container_width=True)

    # ── Yield regression plot ─────────────────────────────────────────────────

    if len(df_ym) >= 2:
        fig_ym = go.Figure()
        x_ym_line = np.linspace(df_ym["D (hr⁻¹)"].min() * 0.9,
                                df_ym["D (hr⁻¹)"].max() * 1.1, 100)
        fig_ym.add_trace(go.Scatter(
            x=df_ym["D (hr⁻¹)"], y=df_ym["y_norm"],
            mode="markers",
            name=f"S0 = {yield_s0} g/L",
            marker=dict(color="#1D9E75", size=9)
        ))
        fig_ym.add_trace(go.Scatter(
            x=x_ym_line, y=slope_YM * x_ym_line + intercept_YM,
            mode="lines",
            name=f"Linear fit (R²={R2_YM:.4f})",
            line=dict(color="#BA7517", width=2, dash="dot")
        ))
        fig_ym.update_layout(
            title=f"Yield & Maintenance Regression  (S0 = {yield_s0} g/L)",
            xaxis_title="μ = D  (hr⁻¹)",
            yaxis_title="D(S₀ − S) / X",
            height=320,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_ym, use_container_width=True)

    with st.expander("How does this work — and what can you interact with?"):
        st.markdown(f"""
**What you can interact with:**
- **Edit any cell** in the data table — change an S or X value and all four parameters
  and both plots update instantly
- **Exclude near-washout rows** using the X filter — rows where X is very low are
  unreliable because taking 1/X amplifies noise. Try raising the threshold from 0.5 to 1.0
- **Toggle S0 values** — include or exclude entire feed concentration columns from the
  regression. Try removing S0=5 and S0=10 and watch R² improve significantly
- **Change the yield S0** — switch between S0=50, 100, 200 for the Ysx/me regression

**How the L-B regression works:**

Taking reciprocals of the Monod equation gives a straight line:

$$\\frac{{1}}{{\\mu}} = \\frac{{K_m}}{{\\mu_{{max}}}} \\cdot \\frac{{1}}{{S}} + \\frac{{1}}{{\\mu_{{max}}}}$$

slope = Km/μmax → **Km = {Km_est:.4f} g/L** &nbsp;&nbsp; intercept = 1/μmax → **μmax = {mu_max_est:.5f} hr⁻¹**

**How the yield regression works:**

The CSTBR substrate balance at steady state rearranges to:

$$\\frac{{D(S_0 - S)}}{{X}} = \\frac{{1}}{{Y_{{sx}}}} \\cdot \\mu + m_e$$

slope = 1/Ysx → **Ysx = {Ysx_est:.5f} g/g** &nbsp;&nbsp; intercept = me → **me = {me_est:.5f} gS/gX·hr**
""")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Transient CSTBR Simulation
# ════════════════════════════════════════════════════════════════════════════

with tab2:

    st.subheader("Transient CSTBR Simulation")
    st.markdown(
        "Parameters are **auto-filled from the Tab 1 regression**. "
        "You can override them manually. Adjust operating conditions "
        "and watch the reactor approach steady state."
    )
    st.markdown("---")

    def safe(key, fallback):
        v = st.session_state.get(key, fallback)
        return fallback if (v is None or (isinstance(v, float) and np.isnan(v))) else v

    mu_max_default = safe("mu_max_est", 0.36640)
    Km_default     = safe("Km_est",     12.1463)
    Ysx_default    = safe("Ysx_est",    0.07351)
    me_default     = safe("me_est",     1.25539)

    col_p, col_ic = st.columns(2)

    with col_p:
        st.markdown("**Kinetic parameters** *(auto-filled from Tab 1)*")
        mu_max_sim = st.number_input("μmax (hr⁻¹)", value=round(mu_max_default, 5), format="%.5f")
        Km_sim     = st.number_input("Km (g/L)",    value=round(Km_default, 4),    format="%.4f")
        Ysx_sim    = st.number_input("Ysx (g biomass / g substrate)",
                                     value=round(Ysx_default, 5), format="%.5f")
        me_sim     = st.number_input("me — maintenance coefficient (gS/gX·hr)",
                                     value=round(me_default, 5), format="%.5f")

    with col_ic:
        st.markdown("**Operating conditions** *(HW3 defaults: F=75, V=0.8, S₀=50)*")
        F_sim     = st.slider("Flow rate F (mL/hr)", 10, 300, 75, 5)
        V_sim     = st.slider("Reactor volume V (L)", 0.1, 5.0, 0.8, 0.1)
        S0_sim    = st.slider("Feed substrate S₀ (g/L)", 5.0, 200.0, 50.0, 5.0)
        X0_sim    = st.slider("Initial biomass X₀ (g/L)", 0.01, 2.0, 0.1, 0.01)
        S_init    = st.slider("Initial substrate in reactor (g/L)", 0.0, 200.0, 50.0, 5.0)
        t_end_sim = st.slider("Simulation time (hr)", 10, 300, 80, 5)

    D_sim = (F_sim / 1000.0) / V_sim
    st.info(f"**Dilution rate D = {D_sim:.5f} hr⁻¹**  (F/V = {F_sim} mL/hr ÷ {V_sim} L)")

    def cstbr_odes(t, y, mu_max, Km, Ysx, me, D, S0):
        X, S = y
        X = max(X, 0); S = max(S, 0)
        mu   = mu_max * S / (Km + S)
        dXdt = (mu - D) * X
        dSdt = D * (S0 - S) - (mu / Ysx + me) * X
        return [dXdt, dSdt]

    sol_c = solve_ivp(
        cstbr_odes, (0, t_end_sim), [X0_sim, S_init],
        args=(mu_max_sim, Km_sim, Ysx_sim, me_sim, D_sim, S0_sim),
        method="RK45", t_eval=np.linspace(0, t_end_sim, 800), max_step=0.1
    )

    t_c = sol_c.t
    X_c = np.maximum(sol_c.y[0], 0)
    S_c = np.maximum(sol_c.y[1], 0)

    if mu_max_sim > D_sim and Ysx_sim > 0:
        S_star = D_sim * Km_sim / (mu_max_sim - D_sim)
        denom  = D_sim / Ysx_sim + me_sim
        X_star = D_sim * (S0_sim - S_star) / denom if denom > 0 else 0
        washout = False
    else:
        S_star = S0_sim; X_star = 0.0; washout = True

    tail = int(0.95 * len(t_c))
    X_num_ss = float(np.mean(X_c[tail:]))
    S_num_ss = float(np.mean(S_c[tail:]))

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Analytical X*", f"{X_star:.4f} g/L")
    mc2.metric("Analytical S*", f"{S_star:.4f} g/L")
    mc3.metric("Numerical X*",  f"{X_num_ss:.4f} g/L",
               delta=f"Δ = {abs(X_num_ss - X_star):.4f}")
    mc4.metric("Numerical S*",  f"{S_num_ss:.4f} g/L",
               delta=f"Δ = {abs(S_num_ss - S_star):.4f}")

    if washout:
        st.warning("⚠️ **Washout:** D ≥ μmax — biomass cannot be sustained at this dilution rate.")

    st.markdown("---")

    fig_c = make_subplots(specs=[[{"secondary_y": True}]])
    fig_c.add_trace(
        go.Scatter(x=t_c, y=S_c, name="Substrate S (g/L)",
                   line=dict(color="#E24B4A", width=2.5)),
        secondary_y=False
    )
    fig_c.add_trace(
        go.Scatter(x=t_c, y=X_c, name="Biomass X (g/L)",
                   line=dict(color="#378ADD", width=2.5)),
        secondary_y=True
    )
    fig_c.add_trace(
        go.Scatter(x=[t_c[0], t_c[-1]], y=[S_star, S_star],
                   name=f"S* = {S_star:.2f} g/L (analytical)",
                   line=dict(color="#E24B4A", width=1.5, dash="dash"), mode="lines"),
        secondary_y=False
    )
    fig_c.add_trace(
        go.Scatter(x=[t_c[0], t_c[-1]], y=[X_star, X_star],
                   name=f"X* = {X_star:.2f} g/L (analytical)",
                   line=dict(color="#378ADD", width=1.5, dash="dash"), mode="lines"),
        secondary_y=True
    )
    fig_c.update_yaxes(title_text="Substrate S (g/L)", secondary_y=False,
                       title_font=dict(color="#E24B4A"), tickfont=dict(color="#E24B4A"))
    fig_c.update_yaxes(title_text="Biomass X (g/L)", secondary_y=True,
                       title_font=dict(color="#378ADD"), tickfont=dict(color="#378ADD"))
    fig_c.update_xaxes(title_text="Time (hr)")
    fig_c.update_layout(
        title="Transient CSTBR Response — Approach to Steady State",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=460, margin=dict(l=20, r=20, t=60, b=20), hovermode="x unified"
    )
    st.plotly_chart(fig_c, use_container_width=True)

    with st.expander("What do the dashed lines represent?"):
        st.markdown(f"""
The **dashed lines** are the **analytical steady-state** values derived algebraically
from the CSTBR mass balances at steady state (dX/dt = dS/dt = 0).

$$S^* = \\frac{{D \\cdot K_m}}{{\\mu_{{max}} - D}} \\approx {S_star:.2f} \\text{{ g/L}}$$

$$X^* = \\frac{{D(S_0 - S^*)}}{{D/Y_{{sx}} + m_e}} \\approx {X_star:.2f} \\text{{ g/L}}$$

The simulation should converge to these values. If Δ is large, increase simulation time.

**HW3 reference** (F=75, S₀=50): S* ≈ 4.20 g/L, X* ≈ 1.71 g/L
""")

    with st.expander("Why does a CSTBR reach steady state but a batch fermenter doesn't?"):
        st.markdown("""
In a **batch fermenter**, substrate depletes monotonically — nothing replenishes it.

In a **CSTBR**, fresh substrate flows in at D·S₀ and broth flows out at D·X and D·S.
At steady state, growth exactly replaces washout losses. If D > μmax, cells wash out
faster than they can grow — the **washout condition** flagged above.
""")
