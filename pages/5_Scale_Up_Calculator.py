import streamlit as st
import numpy as np

st.set_page_config(page_title="Scale-Up Calculator", layout="wide")

st.title("Bioreactor Scale-Up Calculator")
st.caption(
    "Geometric similarity · Constant power per unit volume · Turbulent impeller scaling"
)

st.markdown(
    "Scale a bioreactor from lab bench to pilot or industrial scale. "
    "Enter your lab-scale specifications, set a target fluid volume, and the calculator "
    "applies **geometric similarity** and **constant P/V** to determine all pilot-scale "
    "dimensions, impeller speed, and gas flow rate."
)
st.markdown("---")

# ── Lab-scale inputs ──────────────────────────────────────────────────────────

st.subheader("Lab-scale specifications")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Mechanical**")
    P_lab   = st.number_input("Power P (W)",             value=3.0,    step=0.1,   format="%.2f")
    N_lab   = st.number_input("Impeller speed N (rpm)",  value=750.0,  step=10.0,  format="%.0f")
    D_lab   = st.number_input("Impeller diameter D (m)", value=0.07,   step=0.005, format="%.3f",
                              help="Typically T/2 for a standard Rushton turbine")

with col2:
    st.markdown("**Geometry**")
    T_lab   = st.number_input("Reactor diameter T (m)",  value=0.14,   step=0.01,  format="%.3f")
    H_lab   = st.number_input("Reactor height H (m)",    value=0.46,   step=0.01,  format="%.3f")
    V_f_lab = st.number_input("Fluid volume (m³)",       value=0.003,  step=0.001, format="%.4f")

with col3:
    st.markdown("**Fluid & aeration**")
    rho      = st.number_input("Fluid density (kg/m³)",     value=1000.0, step=1.0,    format="%.0f")
    mu_fluid = st.number_input("Viscosity (cP)",            value=1.5,    step=0.1,    format="%.1f")
    QG_lab   = st.number_input("Gas flow rate QG (m³/min)", value=0.0033, step=0.0001, format="%.4f")

V_r_lab  = (np.pi / 4.0) * T_lab**2 * H_lab
fill_frac = V_f_lab / V_r_lab if V_r_lab > 0 else 0.8
vvm_lab   = QG_lab / V_f_lab  if V_f_lab > 0 else 0

st.info(
    f"Lab reactor total volume (π/4 · T² · H): **{V_r_lab*1000:.1f} L** · "
    f"Fill fraction: **{fill_frac:.2f}** · "
    f"vvm: **{vvm_lab:.4f} vol/vol/min**"
)

st.markdown("---")

# ── Target scale ──────────────────────────────────────────────────────────────

st.subheader("Target scale")

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    V_f_pilot = st.slider(
        "Target fluid volume (m³)",
        min_value=0.01, max_value=100.0, value=10.0, step=0.5
    )
with col_t2:
    st.metric("Scale factor",  f"{V_f_pilot/V_f_lab:.1f}×")
    st.metric("Target volume", f"{V_f_pilot*1000:.0f} L")

# ── Scale-up calculations ─────────────────────────────────────────────────────
# 1. Geometric similarity:  all linear dims ∝ V^(1/3)
# 2. Constant P/V:          P_pilot = P_lab × (V_pilot/V_lab)
# 3. Impeller speed:        constant P/V + geometric sim → N³·D² = const
#                           → N_pilot = N_lab × (D_lab/D_pilot)^(2/3)
# 4. Gas flow:              constant vvm (vol gas / vol liquid / min)
#                           → QG_pilot = vvm × V_f_pilot

ratio     = V_f_pilot / V_f_lab
lin_scale = ratio ** (1.0 / 3.0)

P_pilot   = P_lab * ratio
T_pilot   = T_lab * lin_scale
H_pilot   = H_lab * lin_scale
D_pilot   = D_lab * lin_scale
V_r_pilot = V_r_lab * ratio
N_pilot   = N_lab * (D_lab / D_pilot) ** (2.0 / 3.0)
QG_pilot  = vvm_lab * V_f_pilot        # constant vvm

st.markdown("---")

# ── Results ───────────────────────────────────────────────────────────────────

st.subheader("Pilot-scale results")

r1, r2, r3, r4 = st.columns(4)
r1.metric("Power P",             f"{P_pilot:,.0f} W",      delta=f"Lab: {P_lab:.1f} W")
r2.metric("Reactor height H",    f"{H_pilot:.2f} m",       delta=f"Lab: {H_lab:.2f} m")
r3.metric("Reactor diameter T",  f"{T_pilot:.2f} m",       delta=f"Lab: {T_lab:.3f} m")
r4.metric("Total reactor vol",   f"{V_r_pilot:.2f} m³",    delta=f"Lab: {V_r_lab*1000:.1f} L")

r5, r6, r7, r8 = st.columns(4)
r5.metric("Fluid volume",        f"{V_f_pilot:.2f} m³",    delta=f"Lab: {V_f_lab*1000:.1f} L")
r6.metric("Impeller speed N",    f"{N_pilot:.0f} rpm",     delta=f"Lab: {N_lab:.0f} rpm")
r7.metric("Impeller diameter D", f"{D_pilot:.2f} m",       delta=f"Lab: {D_lab:.3f} m")
r8.metric("Gas flow QG",         f"{QG_pilot:.2f} m³/min", delta=f"Lab: {QG_lab:.4f} m³/min")

st.markdown("---")

# ── Expanders ─────────────────────────────────────────────────────────────────

with st.expander("How does the scale-up math work?"):
    st.markdown(f"""
Scaling from **{V_f_lab*1000:.0f} L** to **{V_f_pilot*1000:.0f} L**
(scale factor = {ratio:.1f}×, linear scale = {lin_scale:.3f}×) uses four principles:

**1. Geometric similarity** — all linear dimensions scale with the cube root of volume,
preserving H/T and D/T ratios at both scales:

$$\\frac{{T_p}}{{T_l}} = \\frac{{H_p}}{{H_l}} = \\frac{{D_p}}{{D_l}}
= \\left(\\frac{{V_p}}{{V_l}}\\right)^{{1/3}} = {ratio:.1f}^{{1/3}} = {lin_scale:.3f}$$

**2. Constant power per unit volume (P/V)** — preserves mixing intensity and kLa:

$$P_p = P_l \\times \\frac{{V_p}}{{V_l}} = {P_lab:.1f} \\times {ratio:.0f} = {P_pilot:,.0f} \\text{{ W}}$$

**3. Impeller speed** — in turbulent flow, the power number Np = P/(ρN³D⁵) is constant.
With geometric similarity (V ∝ D³), constant P/V simplifies to **N³·D² = const**:

$$N_p = N_l \\times \\left(\\frac{{D_l}}{{D_p}}\\right)^{{2/3}}
= {N_lab:.0f} \\times \\left(\\frac{{{D_lab:.3f}}}{{{D_pilot:.3f}}}\\right)^{{2/3}}
= {N_pilot:.0f} \\text{{ rpm}}$$

**4. Gas flow** — constant vvm (volumes of gas per volume of liquid per minute)
ensures the same aeration intensity at both scales:

$$\\text{{vvm}} = \\frac{{Q_{{G,l}}}}{{V_{{f,l}}}} = \\frac{{{QG_lab:.4f}}}{{{V_f_lab:.3f}}}
= {vvm_lab:.4f} \\text{{ min}}^{{-1}}$$

$$Q_{{G,p}} = \\text{{vvm}} \\times V_{{f,p}} = {vvm_lab:.4f} \\times {V_f_pilot:.1f}
= {QG_pilot:.2f} \\text{{ m³/min}}$$
""")

with st.expander("Why does impeller speed decrease at larger scale?"):
    st.markdown(f"""
This is one of the most counterintuitive results in bioprocess scale-up.

At constant P/V with geometric similarity, power scales as:

$$P/V \\propto N^3 \\cdot D^2$$

Since D increases with scale (D ∝ V^(1/3)), N must **decrease** to keep P/V constant:

$$N \\propto \\left(\\frac{{P/V}}{{D^2}}\\right)^{{1/3}} \\propto V^{{-2/9}}$$

At {V_f_pilot:.0f} m³ the impeller is {lin_scale:.2f}× larger in diameter — delivering the
same power at **{N_pilot:.0f} rpm** instead of {N_lab:.0f} rpm.

The practical consequence: you can't run a large fermenter at lab RPM. The shear forces
would be excessive, damaging cells and the impeller shaft. This is why industrial
bioreactors rotate slowly but have massive impellers.
""")

with st.expander("What are the limitations of this approach?"):
    st.markdown("""
Geometric similarity with constant P/V is a useful first approximation but has known
limitations at large scale:

- **Oxygen transfer** — kLa does not scale perfectly with P/V alone. At large scale,
  bubble coalescence and gas hold-up change in ways not captured by simple P/V matching.
- **Mixing time** — increases with scale even at constant P/V. A 10,000 L fermenter
  has much longer bulk mixing times than a 3 L lab fermenter, creating concentration
  gradients that can stress cells.
- **Shear sensitivity** — some cell lines (mammalian, filamentous fungi) are shear-
  sensitive. Constant P/V may still deliver excessive local shear near the impeller tip.
- **Alternative criteria** — constant tip speed (N·D = const) or constant Reynolds
  number are sometimes preferred depending on the organism and process.

For a first-pass feasibility study, constant P/V geometric scale-up is industry-standard.
Detailed CFD modelling is typically used before final design commitment.
""")
