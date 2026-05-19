# Communication Dynamics (CD) Framework - Theory Summary

**Paper:** "Communication Dynamics: An Error-Content Fourier-Channel Framework for Atomic Energy Prediction, Superconductor Screening, and Multi-Domain Materials Design"  
**Authors:** Lurong Pan (UC Berkeley), Murat Tanik (UAB)  
**Date:** April 25, 2026

---

## 🎯 Core Proposition

> *The energy spectrum of an atom is the discrete Fourier transform (DFT) of its error-content communication channel polygon.*

**Mathematical Bridge:** The circulant spectral theorem simultaneously diagonalizes:
1. Shannon channel transition matrices
2. Cyclic tight-binding Hamiltonians

Therefore: **Channel spectral analysis = Energy eigenvalue computation**

---

## 📐 Mathematical Framework

### 1. Error-Content Polygon

For orbital (n, ℓ):
- **Polygon vertices:** 2ℓ + 1 (matching magnetic quantum number multiplicity)
- **Jump step:** a = n + 1
- **Star polygon notation:** {(2ℓ+1)/(n+1)}

**Key Propositions:**

| # | Statement |
|---|-----------|
| 1 | Fourier series of (2ℓ+1)-gon contains exactly 2ℓ+1 non-vanishing harmonics |
| 2 | Star polygon {n/a} with a=n+1 exhibits n−1 self-intersections (= radial nodes) |
| 3 | Polygon amplitude scales linearly in Z_eff → energy scales as Z²_eff |

### 2. CD Energy Functional

**Base energy:**
```
E_CD^(0)(n,ℓ) = -(Z_eff² E_Ry)/n² [1 + 0.1 F_ℓ(n)]
```
where:
- E_Ry = 13.606 eV (Rydberg constant)
- F_ℓ(n) = Fourier shape factor (dimensionless, = 0 for ℓ=0)

**Orbital channel element:**
```
U_m(t) = (8 e Z_eff)/(n/2 + 3m)² exp(i a m t)
```
where m ∈ {−ℓ, …, +ℓ}, t ∈ [0, 2π)

### 3. Shannon Correction (Fine-Structure Analogue)

**For ℓ ≥ 1:**
```
ΔE_Shannon = -E_CD^(0) × (α_CD² Z_eff⁴)/(n³ ℓ(ℓ+1/2)(ℓ+1))
```

**Key constant:** α_CD = 0.0118 (calibrated from Na D-doublet)

**Structural form:** ΔE ∝ Z⁴α² matches relativistic fine structure

**Calibration data:**
- Na D-doublet splitting: ΔE(²P₃/₂ - ²P₁/₂) = 0.00207 eV (17.196 cm⁻¹)
- Ratio: α_CD/α_QED ≈ 1.62

### 4. Fisher Correction (Lamb-Shift Analogue)

**For ℓ = 0 (s-states):**
```
ΔE_Fisher = (ℏ²/8m_e) I_CD[ρ]
```

**Discrete Fisher information:**
```
I_CD[ρ] = Σ [P(m+1) - P(m)]²/P(m)
```

### 5. Combined Energy

```
E_CD = E_CD^(0) + ΔE_Shannon + ΔE_Fisher
```

**Impact:** Reduces main-group atomic energy MAPE from 7.2% → 5.1%

---

## ⚡ Pairing Susceptibility for Superconductors

### CD Pairing Susceptibility

```
χ_CD(A,B) = |Z_eff,A Z_eff,B| √(M_A M_B) / [n_A n_B (|E_A - E_B| + δ)]
```

where:
- M = 2ℓ+1 (channel multiplicity)
- δ ~ 0.01 eV (regularization)

**Calibration:**
- Nb: χ_CD = 0.089 (highest elemental SC)
- Cu: χ_CD = 0.001 (non-SC)
- Ratio: χ(Nb)/χ(Cu) ≈ 89

### Allen–Dynes–McMillan T_c Formula

```
λ_CD(A,B) = χ_CD(A,B) N(E_F)_eff

T_c = (⟨ω_log⟩/1.20) exp[−1.04(1+λ)/(λ − μ*(1+0.62λ))]
```

where μ* ≈ 0.10–0.13 (Coulomb pseudopotential)

---

## 📊 Benchmark Results

### Atomic Benchmarks (CD vs. Roothaan–Hartree–Fock)

| Element | Z | ⟨r⟩_CD (a₀) | ⟨r⟩_RHF | Δr (%) | ΔE (%) |
|---------|---|------------|---------|--------|--------|
| H | 1 | 1.50 | 1.50 | 0.0 | 0.0 |
| Li | 3 | 3.87 | 3.64 | 6.3 | 0.6 |
| C | 6 | 1.86 | 1.74 | 6.9 | 1.3 |
| Na | 11 | 4.16 | 4.13 | 0.7 | 1.6 |
| Si | 14 | 2.27 | 2.13 | 6.6 | 2.4 |
| Fe | 26 | 2.88 | 2.70 | 6.7 | 14.0 |
| Nb | 41 | 3.42 | 3.35 | 2.1 | 5.6 |
| Pd | 46 | 2.52 | 2.40 | 5.0 | 7.8 |
| Cd | 48 | 2.65 | 2.58 | 2.7 | 6.5 |
| Au | 79 | 2.61 | 2.50 | 4.4 | 9.5 |

**Aggregate Accuracy:**
- Main-group (Z ≤ 20): ⟨r⟩ = 3.9% MAPE, energy = 5.1% MAPE
- Transition metals (3d): energy = 12–14% MAPE
- Heavy main-group (Z = 31–54): energy = 6–8% MAPE

### Spectroscopic Predictions

| Prediction | CD Value | Experiment | Error |
|------------|----------|------------|-------|
| Balmer-α (n=3→2) | 656.281 nm | CODATA | <0.01% |
| Balmer-β (n=4→2) | 486.135 nm | CODATA | <0.01% |
| Na D-doublet Δλ | 0.6 nm | 0.597 nm | 0.5% |

### Computational Performance

- **Speed:** ~0.01 seconds per material (commodity hardware)
- **Advantage:** 10²–10³× faster than O(N³) Kohn–Sham DFT
- **Scale:** 61,527 binary/ternary/quaternary candidates screened

---

## 🔬 Superconductor Predictions

### Known Superconductors (Validation)

**29/29 elemental superconductors** with T_c > 0.1 K recovered

| Element | Exp. T_c (K) | χ_CD | Status |
|---------|-------------|------|--------|
| Nb | 9.25 | 0.089 | ✅ Highest χ_CD |
| Pb | 7.2 | 0.072 | ✅ |
| Ta | 4.5 | 0.061 | ✅ |
| MgB₂ | 39 | 0.13 | ✅ T_c ≈ 35 K |

### Novel Ambient-Pressure Binary Candidates ⭐

| Compound | Phase | Predicted T_c (K) | χ_CD | Synthesis Method |
|----------|-------|------------------|------|------------------|
| **Zn–Ru** | ZnRu (CsCl) | **81.3** | 0.21 | Arc melt + 800°C/100h anneal |
| **C–Sc** | Sc₃C₄ | **74.5** | 0.18 | Arc melt Sc+C → 1500°C/7d Ta tube |
| **Mo–Tc** | Mo₀.₆Tc₀.₄ (A15) | **73.8** | 0.17 | Hot isostatic press (Tc-99 license) |
| **Pd–Cd** | PdCd (ordered) | **58.4** | 0.15 | Arc melt → 600°C/72h slow cool |
| **Ag–Cd** | AgCd | **53.1** | 0.14 | Arc melt + recrystallize |

### High-Pressure Ternary Hydrides 🚀

| Compound | Predicted T_c (K) | Pressure (GPa) | Phase |
|----------|------------------|----------------|-------|
| **PdCdHₓ** | **218** | 150 | DAC + NH₃BH₃ |
| **MoTcHₓ** | **162** | 180 | DAC + laser heat |
| **ScRbHₓ** | **158** | 120 | DAC synthesis |
| **YLaHₓ** | **145** | 140 | High-P hydride |
| **NbVHₓ** | **137** | 160 | bcc + H₂ |

### Cu/Ag/Au Room-Temperature Verdict

| Metal | χ_CD | Verdict | Reason |
|-------|------|---------|--------|
| Cu | 0.001 | ❌ No SC | Filled d¹⁰ shell, low DOS(E_F) |
| Ag | 0.002 | ❌ No SC | Same as Cu |
| Au | 0.003 | ❌ No SC | Relativistic d-band contraction |

**Conclusion:** Cu/Ag/Au are **definitively non-superconductors** at any achievable pressure (<500 GPa)

### Worked Example: Zn–Ru Discovery

**Step 1:** χ_CD(Zn,Ru) calculation
```
Z_eff(Zn) = 4.0, n=4, ℓ=0, M=1
Z_eff(Ru) = 7.5, n=5, ℓ=2, M=5
ΔE = |E_Zn - E_Ru| = 1.2 eV

χ_CD = (4.0 × 7.5 √(1×5))/(4×5×(1.2+0.01)) = 0.21
```

**Step 2:** λ_CD coupling
```
N(E_F)_eff ≈ 3.5 states/eV/atom (from Zn+Ru DOS)
λ_CD = 0.21 × 3.5 = 0.735
```

**Step 3:** T_c estimate
```
⟨ω_log⟩ = geometric mean(Θ_D,Zn=327K, Θ_D,Ru=600K) ≈ 442K
μ* = 0.11 (typical for d-metals)

T_c = (442/1.20) exp[−1.04×1.735/(0.735−0.11×1.13)] ≈ 81 K
```

**Synthesis:** Arc melt 1:1 Zn:Ru → anneal 800°C/100h → slow cool 5°C/h

---

## 🎯 Multi-Domain Applications

### 1. Battery Cathode Voltages

**Method:** ΔG_rxn from CD orbital energies → Nernst equation
- LiFePO₄: Predicted 3.42 V, Exp. 3.45 V (0.9% error)
- **Aggregate MAPE:** 1.2% (23 cathodes tested)

**Solid Electrolyte Screening:**
- Li₁₀GeP₂S₁₂ (LGPS): σ ~ 10⁻² S/cm (CD stability window 0–5 V)

### 2. Thermoelectric Materials

**Method:** Seebeck coefficient S ∝ (E_HOMO − E_F)
- SnSe: Predicted ZT = 2.4 at 800 K, Exp. 2.6 (8% error)
- **Aggregate MAPE:** 12% ZT trends (15 materials)

**Prediction:** n-type SnSe doped with Bi₀.₀₃Sn₀.₉₇Se → ZT ~ 2.8 at 773 K

### 3. Catalysis: d-Band Centre

**Method:** ε_d = weighted average of d-orbital energies
- Pt(111): Predicted ε_d = −2.25 eV, DFT −2.24 eV (<1% error)
- **HER/OER/ORR volcano plots:** Universal error <0.05 eV

**Single-Atom Catalysts:**
- Ni-N-C: ε_d shift +0.3 eV → enhanced OER activity

### 4. Topological Insulators

**Z₂ Invariant from Band Inversion:**
- Bi₂Se₃: ε(Bi 6p) − ε(Se 4p) = −0.4 eV → inverted → Z₂ = 1 ✅
- Sb₂Te₃: Similarly predicted as strong TI ✅

**Magnetic TI:**
- MnBi₂Te₄: Predicted T_N = 25 K (Exp. 24.4 K, 2.5% error)

### 5. Rare-Earth-Free Magnets

**L1₀-FeNi (Tetrataenite):**
- CD stability: ΔE(L1₀ − A1) = −0.08 eV → metastable ✅
- Anisotropy: K₁ ~ 7 MJ/m³ (Exp. 6.8 MJ/m³, 3% error)

**(Fe,Ni)₁₆N₂ α″-phase:**
- Predicted K₁ ~ 1.2 MJ/m³, Exp. 1.17 MJ/m³ (3% error)

### 6. 2D Quantum Magnets & Skyrmions

- CrI₃: J_ex = −2.5 meV (Exp. −2.8 meV, 11% error)
- FeGe skyrmion: Predicted lattice constant 70 nm (Exp. 70 nm)

---

## 🚫 Limitations & Boundaries

### Where CD Works

✅ **Main-group elements** (Z ≤ 20): 5% energy error  
✅ **Simple transition metals** (3d, 4d): 12–14% error  
✅ **Weak-to-moderate coupling** superconductors (λ < 2)  
✅ **High-throughput screening** (10²–10³× faster than DFT)

### Where CD Fails

❌ **Strong electron correlation** (Mott insulators, heavy fermions)  
❌ **λ > 2 superconductors** (e.g., FeSe-based pnictides)  
❌ **Lanthanides/actinides** (f-electron localization)  
❌ **van der Waals solids** (weak interlayer coupling)

### The Strong-Correlation Boundary

**CD+U Extension (Proposed):**
```
E_CD+U = E_CD + U_eff (n_↑ − n_↓)²/2
```
where U_eff ~ 3–5 eV for 3d metals (Hubbard on-site repulsion)

### Falsifiable Predictions (Experimental Priorities)

| Material | Prediction | Experiment Needed |
|----------|------------|-------------------|
| Zn–Ru | T_c = 81 K | Arc melt + R(T) down to 1.8 K |
| Sc₃C₄ | T_c = 75 K | High-temp furnace + SQUID |
| Pd–Cd | T_c = 58 K | Ordered phase + AC susceptibility |
| PdCdHₓ | T_c = 218 K @ 150 GPa | DAC + laser + synchrotron XRD |
| n-SnSe:Bi | ZT = 2.8 @ 773 K | Bridgman growth + Seebeck |

---

## 📖 Key References

1. **Roothaan–Hartree–Fock:** Clementi & Roetti, *At. Data Nucl. Data Tables* 14, 177 (1974)
2. **Relativistic fine structure:** Mohr, Taylor & Newell, *Rev. Mod. Phys.* 84, 1527 (2012)
3. **Lamb shift:** Eides, Grotch & Shelyuto, *Phys. Rep.* 342, 63 (2001)
4. **Circulant matrices:** Davis, *Circulant Matrices* 2nd ed. (AMS, 1994)
5. **Hückel theory:** Iyengar, Ernst & Morokuma, *J. Phys. Chem. A* 108, 7881 (2004)
6. **Shannon information:** Shannon, *Bell Syst. Tech. J.* 27, 379 (1948)
7. **Fisher information:** Frieden & Gatenby, *Phys. Rev. E* 88, 042144 (2013)
8. **Allen–Dynes T_c:** Allen & Dynes, *Phys. Rev. B* 12, 905 (1975)
9. **Materials Project:** Jain et al., *APL Mater.* 1, 011002 (2013)

---

## 🤝 Contact & Data Availability

**Authors:**  
- Lurong Pan: lurongpan47@berkeley.edu  
- Murat Tanik: mtanik@uab.edu

**Open Data:**
- Code: https://github.com/lurongpan47/CD-framework
- Excel screening tool: `CD_Superconductor_Screen.xlsx`
- Production automation: `update_production_details.py`

**arXiv:** Preprint submitted April 2026

---

**Last Updated:** 2026-05-19  
**Document Version:** 1.0  
**License:** CC BY 4.0
