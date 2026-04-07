# Bioprocess Simulator

An interactive web application for modelling microbial fermentation, bioreactor design, and industrial scale-up. Built with Python and Streamlit.

**[Live App](https://bioprocess-simulator-manyadkadiwala.streamlit.app)** — open in your browser, no installation required.

---

## Overview

This simulator translates classical bioprocess engineering models into an interactive tool where parameters can be adjusted in real time and the biological and engineering consequences are shown instantly. It covers the full arc from a simple batch fermenter through to industrial-scale bioreactor design.

The models are grounded in peer-reviewed kinetics literature and validated against analytical solutions and experimental data from laboratory-scale fermentation experiments.

---

## Modules

| # | Module | Methods |
|---|--------|---------|
| 01 | **Batch Fermenter** | Monod growth kinetics, coupled ODE system, RK45 numerical solver |
| 02 | **Ethanol Fermentation** | Inhibition kinetics, sensitivity analysis, stoichiometric yield |
| 03 | **CSTBR Analyzer** | Lineweaver-Burk regression, yield/maintenance estimation, transient simulation |
| 04 | **2,3-BDO Fermentation** | Two-phase aerobic/anaerobic model, automatic phase transition detection |
| 05 | **Scale-Up Calculator** | Geometric similarity, constant P/V, turbulent impeller scaling |

---

## Technical Stack

- **Python 3.11+**
- **Streamlit** — web app framework and UI
- **SciPy** — `solve_ivp` RK45 ODE solver for all dynamic simulations
- **Plotly** — interactive dual-axis plots
- **Pandas** — editable data tables in the CSTBR module
- **NumPy** — numerical computation

---

## Running Locally

**1. Clone the repository**
```bash
git clone https://github.com/manyadkadiwala/bioprocess-simulator.git
cd bioprocess-simulator
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## Project Structure

```
bioprocess-simulator/
├── app.py                        # Home page and navigation shell
├── requirements.txt              # Python dependencies
├── pages/
│   ├── 0_Welcome.py              # Introduction, glossary, parameter guide
│   ├── 1_Batch_Fermenter.py      # Module 01
│   ├── 2_Ethanol_Fermentation.py # Module 02
│   ├── 3_CSTBR_Analyzer.py       # Module 03
│   ├── 4_BDO_Fermentation.py     # Module 04
│   └── 5_Scale_Up_Calculator.py  # Module 05
└── README.md
```

---

## Models and Methods

### Monod Growth Kinetics
All growth models use the Monod relationship for substrate-limited growth:

$$\mu = \mu_{max} \frac{S}{K_s + S}$$

The coupled ODE system is integrated numerically using SciPy's `solve_ivp` with the RK45 method, equivalent to a classical fourth-order Runge-Kutta solver.

### Ethanol Inhibition
The ethanol fermentation model incorporates noncompetitive product inhibition:

$$\nu_E = \nu_m \cdot \frac{S}{K_s + S} \cdot \left(1 - \frac{P}{P_{max}}\right)^n$$

### Lineweaver-Burk Parameter Estimation
Monod parameters are estimated by linearising the growth equation via double-reciprocal transformation and applying ordinary least squares regression to steady-state CSTBR data.

### Two-Phase BDO Model
The 2,3-butanediol model detects the aerobic-to-anaerobic phase transition automatically when oxygen demand exceeds the maximum transfer rate kLa·C*. Biomass is fixed at the transition value and the fermentation kinetics switch to anaerobic equations for the remainder of the simulation.

### Bioreactor Scale-Up
Scale-up applies three principles simultaneously: geometric similarity (all linear dimensions scale as V^(1/3)), constant power per unit volume (P/V = const), and constant vvm for aeration. Impeller speed is derived from the turbulent power number correlation.

---

## References

- Monod, J. (1949). The growth of bacterial cultures. *Annual Review of Microbiology*, 3, 371-394.
- Maiorella, B. L., Blanch, H. W., & Wilke, C. R. (1983). By-product inhibition effects on ethanolic fermentation by *Saccharomyces cerevisiae*. *Biotechnology and Bioengineering*, 25(1), 103-121.
- Bailey, J. E., & Ollis, D. F. (1986). *Biochemical Engineering Fundamentals* (2nd ed.). McGraw-Hill.

---

## Author

**Manya Kadiwala**  
B.S. Fermentation Science (Honors) · Minors in Biotechnology and Innovation & Transformational Change  
Purdue University  
[LinkedIn](https://linkedin.com/in/manya-kadiwala) · kadiwala@purdue.edu
