import streamlit as st

st.set_page_config(page_title="Bioprocess Simulator", page_icon="🧫", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0e0608 0%, #1e0d12 45%, #0e1a1a 100%);
    border-radius: 20px;
    padding: 64px 56px;
    margin-bottom: 48px;
    position: relative;
    overflow: hidden;
    border: 1px solid #3a1a22;
}
.hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -60px;
    width: 380px; height: 380px;
    background: radial-gradient(circle, rgba(139,58,82,0.18) 0%, transparent 65%);
    border-radius: 50%;
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 35%;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(42,127,127,0.12) 0%, transparent 65%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-tag {
    display: inline-block;
    background: transparent;
    border: 1px solid #8B3A52;
    color: #c47a90;
    font-size: 0.70rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 2px;
    margin-bottom: 28px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 700;
    color: #f5eef0;
    margin: 0 0 20px 0;
    line-height: 1.1;
    letter-spacing: -0.01em;
}
.hero-title span {
    color: #c47a90;
}
.hero-sub {
    font-size: 1.05rem;
    color: rgba(235,220,225,0.68);
    max-width: 560px;
    line-height: 1.8;
    margin: 0;
    font-weight: 300;
}
.hero-rule {
    width: 48px;
    height: 2px;
    background: linear-gradient(90deg, #8B3A52, #2A7F7F);
    margin: 28px 0;
    border: none;
}

/* ── Section headers ── */
.sec-label {
    font-size: 0.70rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #2A7F7F;
    margin: 0 0 6px 0;
}
.sec-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.85rem;
    font-weight: 600;
    color: #1a0a0e;
    margin: 0 0 6px 0;
    line-height: 1.2;
}
.sec-sub {
    color: #6a5a5e;
    font-size: 0.9rem;
    margin: 0 0 28px 0;
}
.rule {
    border: none;
    border-top: 1px solid #e8dde0;
    margin: 44px 0;
}

/* ── Module cards ── */
.module-card {
    background: #ffffff;
    border: 1px solid #ddd0d4;
    border-top: 3px solid #8B3A52;
    border-radius: 4px;
    padding: 26px 22px;
    height: 100%;
}
.module-card.alt {
    border-top-color: #2A7F7F;
    background: #f5fafa;
}
.module-number {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8B3A52;
    margin-bottom: 10px;
}
.module-card.alt .module-number {
    color: #2A7F7F;
}
.module-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #1a0a0e;
    margin: 0 0 10px 0;
    font-weight: 600;
}
.module-body {
    font-size: 0.875rem;
    color: #4a3a3e;
    line-height: 1.7;
    margin: 0;
    font-weight: 300;
}
.module-pill {
    display: inline-block;
    background: #fdf0f3;
    border: 1px solid #ddb0bc;
    color: #7a2a42;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 2px;
    margin-top: 14px;
    letter-spacing: 0.04em;
}
.module-card.alt .module-pill {
    background: #f0fafa;
    border-color: #9ac8c8;
    color: #1a5f5f;
}

/* ── Concept boxes ── */
.concept-box {
    border-left: 2px solid #2A7F7F;
    padding: 14px 18px;
    margin-bottom: 16px;
    background: #f5fafa;
}
.concept-term {
    font-weight: 500;
    color: #1a0a0e;
    font-size: 0.92rem;
    margin-bottom: 4px;
}
.concept-def {
    color: #4a3a3e;
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.65;
    font-weight: 300;
}

/* ── Param rows ── */
.param-row {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 16px 0;
    border-bottom: 1px solid #ecdde0;
}
.param-symbol {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #2A7F7F;
    min-width: 56px;
    padding-top: 1px;
    font-weight: 600;
    flex-shrink: 0;
}
.param-name {
    font-weight: 500;
    color: #1a0a0e;
    font-size: 0.88rem;
}
.param-desc {
    color: #4a3a3e;
    font-size: 0.83rem;
    margin-top: 3px;
    line-height: 1.6;
    font-weight: 300;
}

/* ── Tip cards ── */
.tip-card {
    background: #ffffff;
    border: 1px solid #ddd0d4;
    border-left: 4px solid #8B3A52;
    border-radius: 0 4px 4px 0;
    padding: 20px 24px;
    margin-bottom: 12px;
    display: flex;
    gap: 20px;
    align-items: flex-start;
}
.tip-number {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #ddb0bc;
    line-height: 1;
    min-width: 32px;
    flex-shrink: 0;
    white-space: nowrap;
}
.tip-module {
    font-size: 0.70rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8B3A52;
    margin-bottom: 5px;
}
.tip-body {
    color: #3a2a2e;
    font-size: 0.875rem;
    line-height: 1.65;
    margin: 0;
    font-weight: 300;
}

/* ── How-to boxes ── */
.howto-box {
    background: #fdf8f9;
    border: 1px solid #ddd0d4;
    border-radius: 4px;
    padding: 22px 20px;
    margin-bottom: 12px;
}
.howto-title {
    font-weight: 500;
    color: #1a0a0e;
    font-size: 0.9rem;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid #ddd0d4;
}
.howto-body {
    color: #4a3a3e;
    font-size: 0.86rem;
    line-height: 1.7;
    font-weight: 300;
    margin: 0;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #9a8a8e;
    font-size: 0.80rem;
    padding: 12px 0 28px;
    font-weight: 300;
    letter-spacing: 0.03em;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-tag">Interactive Bioprocess Engineering</div>
    <h1 class="hero-title">Bioprocess<br><span>Simulator</span></h1>
    <hr class="hero-rule">
    <p class="hero-sub">
        An interactive tool for modelling microbial fermentation, bioreactor design,
        and industrial scale-up. Adjust parameters in real time and watch the biology
        respond. No prior knowledge required.
    </p>
</div>
""", unsafe_allow_html=True)

# ── What is this ──────────────────────────────────────────────────────────────

st.markdown('<p class="sec-label">Overview</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-title">What is this?</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-sub">The big picture, explained simply.</p>', unsafe_allow_html=True)

st.markdown("""
Fermentation is one of the oldest biotechnologies humans use. It is how we make beer,
yoghurt, antibiotics, biofuels, and hundreds of industrial chemicals. At its core,
fermentation is **microorganisms eating a sugar and producing something useful** as a
byproduct.

This simulator lets you explore how that process works mathematically. Every slider
controls a real biological or physical parameter. Every plot shows you the direct
consequence of changing it. The goal is to build intuition for how fermentation systems
behave, and why engineers care so deeply about the numbers behind them.
""")

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ── Five modules ──────────────────────────────────────────────────────────────

st.markdown('<p class="sec-label">Navigation</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-title">The five simulators</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-sub">Use the sidebar on the left to move between them.</p>',
            unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
<div class="module-card">
    <div class="module-number">Module 01</div>
    <p class="module-title">Batch Fermenter</p>
    <p class="module-body">The simplest fermentation setup: a closed tank where microbes
    eat a fixed sugar supply until it runs out. Watch biomass grow and substrate deplete
    in real time. This is the foundation everything else builds on.</p>
    <span class="module-pill">Monod kinetics · RK4 solver</span>
</div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""
<div class="module-card">
    <div class="module-number">Module 02</div>
    <p class="module-title">Ethanol Fermentation</p>
    <p class="module-body">Extends the batch model to track ethanol production by yeast.
    Includes an inhibition term: as ethanol builds up it slows the yeast that made it.
    A sensitivity analysis tool shows how each parameter shapes the outcome.</p>
    <span class="module-pill">Inhibition kinetics · Sensitivity analysis</span>
</div>""", unsafe_allow_html=True)

with c3:
    st.markdown("""
<div class="module-card">
    <div class="module-number">Module 03</div>
    <p class="module-title">CSTBR Analyzer</p>
    <p class="module-body">A continuous reactor where fresh feed flows in and broth flows
    out constantly. Estimate kinetic parameters from real experimental data using linear
    regression, then simulate how the reactor approaches steady state from startup.</p>
    <span class="module-pill">Lineweaver-Burk · Parameter estimation</span>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
c4, c5, c6 = st.columns(3)

with c4:
    st.markdown("""
<div class="module-card">
    <div class="module-number">Module 04</div>
    <p class="module-title">2,3-BDO Fermentation</p>
    <p class="module-body">A two-phase model where bacteria first grow aerobically using
    oxygen, then automatically switch to producing 2,3-butanediol when oxygen runs out.
    The phase transition is detected and marked on the plot automatically.</p>
    <span class="module-pill">Two-phase model · Phase transition</span>
</div>""", unsafe_allow_html=True)

with c5:
    st.markdown("""
<div class="module-card">
    <div class="module-number">Module 05</div>
    <p class="module-title">Scale-Up Calculator</p>
    <p class="module-body">Takes a lab-scale bioreactor and calculates what it looks like
    at industrial volumes: dimensions, impeller speed, power requirements, and gas flow.
    Applies geometric similarity and constant power-per-volume principles.</p>
    <span class="module-pill">Geometric similarity · Constant P/V</span>
</div>""", unsafe_allow_html=True)

with c6:
    st.markdown("""
<div class="module-card alt">
    <div class="module-number">Quick Start</div>
    <p class="module-title" style="color:#1a5f5f;">New here?</p>
    <p class="module-body">Start with Module 01 and drag the μmax slider.
    Read this page top to bottom for the glossary and parameter guide.
    Each simulator has expandable explanation sections built in.</p>
    <span class="module-pill">Start at Module 01</span>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ── Key concepts ──────────────────────────────────────────────────────────────

st.markdown('<p class="sec-label">Glossary</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-title">Key concepts</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-sub">Plain-language definitions of the biology and engineering you will encounter.</p>',
            unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
<div class="concept-box">
    <div class="concept-term">Biomass (X)</div>
    <p class="concept-def">The total mass of living microorganisms in the fermenter,
    measured in grams per litre. When conditions are good, biomass grows exponentially:
    each cell divides to make two, which each divide again, and so on.</p>
</div>
<div class="concept-box">
    <div class="concept-term">Substrate (S)</div>
    <p class="concept-def">The sugar (glucose, xylose, etc.) that microbes consume as
    food and energy. As cells grow they eat the substrate, so S decreases as X increases.
    When substrate runs out, growth stops.</p>
</div>
<div class="concept-box">
    <div class="concept-term">Specific growth rate (μ)</div>
    <p class="concept-def">How fast the cell population is growing at any given moment,
    expressed per hour. A rate of 0.3 per hour means the population increases by 30%
    each hour. It depends on how much substrate is available: low substrate means
    slow growth.</p>
</div>
<div class="concept-box">
    <div class="concept-term">Monod kinetics</div>
    <p class="concept-def">The standard mathematical model describing how growth rate
    depends on substrate concentration. At high substrate, cells grow at their maximum
    rate. As substrate gets scarce, growth slows along a curve that flattens near zero,
    like a car decelerating as it runs out of fuel.</p>
</div>
""", unsafe_allow_html=True)

with col_b:
    st.markdown("""
<div class="concept-box">
    <div class="concept-term">Yield coefficient (Ysx)</div>
    <p class="concept-def">How efficiently cells convert substrate into biomass.
    A yield of 0.5 g/g means 1 gram of sugar produces 0.5 grams of cells.
    The rest is lost as heat, CO2, or other byproducts.</p>
</div>
<div class="concept-box">
    <div class="concept-term">Dilution rate (D)</div>
    <p class="concept-def">In a continuous reactor, D equals flow rate divided by reactor
    volume. It sets how quickly liquid is refreshed. Too high and cells wash out faster
    than they grow. Too low and it behaves essentially like a batch fermenter.</p>
</div>
<div class="concept-box">
    <div class="concept-term">Steady state</div>
    <p class="concept-def">The condition in a continuous reactor where nothing is changing:
    the same amount of cells grows as washes out each hour, and substrate consumption
    equals the incoming supply. The simulator shows the transient journey from startup
    to this equilibrium point.</p>
</div>
<div class="concept-box">
    <div class="concept-term">Inhibition</div>
    <p class="concept-def">When a product of fermentation, such as ethanol or 2,3-BDO,
    builds up and starts slowing or poisoning the microbes that made it. This is why
    industrial fermentations rarely reach the theoretical maximum yield: organisms
    slow down before all the substrate is consumed.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ── How to use ────────────────────────────────────────────────────────────────

st.markdown('<p class="sec-label">Guide</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-title">How to use this app</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-sub">Getting the most out of each simulator.</p>',
            unsafe_allow_html=True)

h1, h2 = st.columns(2)

with h1:
    st.markdown("""
<div class="howto-box">
    <div class="howto-title">Navigating between simulators</div>
    <p class="howto-body">Use the sidebar on the left to switch between modules.
    Each page is completely independent. Changing parameters on one page has no effect
    on another.</p>
</div>
<div class="howto-box">
    <div class="howto-title">Sliders and inputs</div>
    <p class="howto-body">Every slider or number input corresponds to a real biological
    or engineering parameter. Drag a slider and the simulation reruns instantly without
    pressing any button. Plots and metric cards update in real time.</p>
</div>
<div class="howto-box">
    <div class="howto-title">The dual-axis plots</div>
    <p class="howto-body">Most plots show two variables on very different scales.
    Glucose might range from 0 to 150 g/L while biomass ranges from 0 to 15 g/L.
    Glucose uses the left axis in red and biomass or products use the right axis
    in blue and green. Hover over the chart to read exact values at any time point.</p>
</div>
""", unsafe_allow_html=True)

with h2:
    st.markdown("""
<div class="howto-box">
    <div class="howto-title">Metric cards</div>
    <p class="howto-body">Each page shows key outputs as large metric cards at the top.
    These update as you adjust parameters and are the fastest way to see the overall
    effect of a change without reading the full plot.</p>
</div>
<div class="howto-box">
    <div class="howto-title">Expandable sections</div>
    <p class="howto-body">Every page has expandable sections marked with a triangle arrow.
    These explain the underlying equations and what the model is doing, written to be
    readable without a mathematics background.</p>
</div>
<div class="howto-box">
    <div class="howto-title">The CSTBR data table</div>
    <p class="howto-body">Module 03 has an editable data table. Click any cell and change
    the experimental value to see how it affects the regression and the estimated
    parameters. Try changing a few substrate values and watch the Lineweaver-Burk
    plot update instantly.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ── Parameter reference ───────────────────────────────────────────────────────

st.markdown('<p class="sec-label">Reference</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-title">Parameter guide</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-sub">What each slider controls and why it matters.</p>',
            unsafe_allow_html=True)

col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown("""
<div class="param-row">
    <div class="param-symbol">μmax</div>
    <div>
        <div class="param-name">Maximum specific growth rate (hr⁻¹)</div>
        <div class="param-desc">The fastest cells can possibly grow when food is unlimited.
        Increasing it speeds up the whole fermentation. Substrate depletes faster and
        biomass peaks earlier. Typical bacteria range from 0.2 to 1.5 per hour.</div>
    </div>
</div>
<div class="param-row">
    <div class="param-symbol">Ks</div>
    <div>
        <div class="param-name">Monod constant (g/L)</div>
        <div class="param-desc">The substrate concentration at which growth rate is exactly
        half of μmax. Low Ks means cells grow well even when food is scarce.
        High Ks means they need a lot of substrate to grow efficiently.</div>
    </div>
</div>
<div class="param-row">
    <div class="param-symbol">Ysx</div>
    <div>
        <div class="param-name">Yield coefficient (g biomass / g substrate)</div>
        <div class="param-desc">How much cell mass is produced per gram of sugar consumed.
        Controls the final biomass concentration. Higher yield means more cells
        from the same amount of sugar.</div>
    </div>
</div>
<div class="param-row">
    <div class="param-symbol">Pmax</div>
    <div>
        <div class="param-name">Maximum ethanol tolerance (g/L)</div>
        <div class="param-desc">The ethanol concentration at which yeast growth completely
        stops. Beyond this point, the product poisons its own producers. Most industrial
        yeast strains tolerate 80 to 120 g/L ethanol.</div>
    </div>
</div>
""", unsafe_allow_html=True)

with col_p2:
    st.markdown("""
<div class="param-row">
    <div class="param-symbol">n</div>
    <div>
        <div class="param-name">Inhibition exponent</div>
        <div class="param-desc">Controls the shape of the inhibition curve. Low n means
        inhibition kicks in strongly even at low product concentrations. High n means
        cells are relatively tolerant until the product concentration gets very high.</div>
    </div>
</div>
<div class="param-row">
    <div class="param-symbol">D</div>
    <div>
        <div class="param-name">Dilution rate (hr⁻¹)</div>
        <div class="param-desc">Flow rate divided by reactor volume in a continuous fermenter.
        Sets how quickly cells are washed out. If D exceeds μmax, the reactor washes
        out completely. This is a critical design boundary in continuous bioprocessing.</div>
    </div>
</div>
<div class="param-row">
    <div class="param-symbol">me</div>
    <div>
        <div class="param-name">Maintenance coefficient (gS / gX · hr)</div>
        <div class="param-desc">Substrate consumed just to keep cells alive, separate from
        growth. Even when growth stops, cells burn energy for maintenance processes.
        Most significant at low dilution rates.</div>
    </div>
</div>
<div class="param-row">
    <div class="param-symbol">kLa·C*</div>
    <div>
        <div class="param-name">Oxygen transfer limit (g/L/hr)</div>
        <div class="param-desc">The maximum rate at which oxygen dissolves into the broth
        from air bubbles. When cell oxygen demand exceeds this, the reactor switches from
        aerobic to anaerobic metabolism, triggering 2,3-BDO production in Module 04.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ── Tips ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="sec-label">Experiments</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-title">Things worth trying</p>', unsafe_allow_html=True)
st.markdown('<p class="sec-sub">Good starting experiments for each module.</p>',
            unsafe_allow_html=True)

tips = [
    ("Batch Fermenter",
     "Raise μmax to 0.50 and watch fermentation finish in half the time. "
     "Then drop Ks to 0.05 and notice how the substrate curve changes shape near the end. "
     "Finally, lower Ysx to 5 and see how much faster the sugar disappears."),
    ("Ethanol Fermentation",
     "Set n to 0.1 and watch ethanol production stall early due to strong inhibition. "
     "Then push n to 2.0 and see how much more ethanol accumulates before inhibition bites. "
     "Use the sensitivity analysis dropdown to see the full relationship in one plot."),
    ("CSTBR Analyzer",
     "In Tab 1, uncheck S0 = 5 and S0 = 10 from the filter and watch R-squared jump from "
     "0.91 to over 0.99. In Tab 2, drag the flow rate up until the washout warning appears. "
     "That is the critical dilution rate where D equals μmax."),
    ("2,3-BDO Fermentation",
     "Lower kLa·C* from 0.027 to 0.010. The phase switch happens much earlier with less "
     "biomass built up, and total BDO drops significantly. This shows why oxygen transfer "
     "engineering is so critical in industrial fermenters."),
    ("Scale-Up Calculator",
     "Try scaling from 3 L to 1 cubic metre, then to 10, then to 100. Notice how impeller "
     "speed keeps dropping as volume grows, and how power requirements become very large "
     "at industrial scale."),
]

for i, (module, body) in enumerate(tips):
    st.markdown(f"""
<div class="tip-card">
    <div class="tip-number">0{i+1}</div>
    <div>
        <div class="tip-module">{module}</div>
        <p class="tip-body">{body}</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="footer">
    Built with Python, Streamlit, SciPy, and Plotly &nbsp;&middot;&nbsp;
    Models based on Monod (1949), Maiorella et al. (1983), and classical bioprocess engineering theory
</div>
""", unsafe_allow_html=True)
