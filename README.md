# CD Superconductor Framework

**Computational framework for discovering room-temperature superconductors via correlation-driven (CD) mechanisms.**

## 📊 Overview

This repository contains production planning tools for synthesizing candidate CD superconductor materials identified through computational screening.

## 🔬 Contents

### `update_production_details.py`
Python script to augment the CD Superconductor screening Excel with detailed production process information:

- **Production Methods** - Arc melting, DAC synthesis, hydride formation
- **Precursor Materials** - High-purity elemental sources, isotopes
- **Temperature Profiles** - Annealing schedules, laser heating parameters
- **Safety Compliance** - OSHA, NRC, DOE regulations
- **Cost Estimates** - Equipment, materials, facility requirements
- **Timelines** - Realistic synthesis schedules

## 🛠️ Usage

```bash
# Install dependencies
pip install openpyxl

# Run the script (requires CD_Superconductor_Screen.xlsx in the same directory)
python update_production_details.py
```

**Output:** `CD_Superconductor_Screen_with_Production.xlsx`

## 📋 Supported Materials

### Binary Pairs (Sheet 2)
- **d-d Intermetallics** - Arc melting + long anneal (2-4 weeks, $50-150k)
- **Hydrides** - Diamond Anvil Cell + laser heating (6-12 months, $300k-1M)
- **Special Materials:**
  - `C-Sc` (Scandium carbide) - $100-200k, 3-6 weeks
  - `Mo-Tc` (Technetium alloy) - $500k+, 12-18 months (NRC license required)
  - `Nb-V` (Niobium-vanadium) - $50-100k, 2-3 weeks

### Ternary Hydrides (Sheet 3)
Automatic safety customization for:
- **Beryllium** - OSHA 29 CFR 1910.1024 compliance
- **Thorium** - NRC 10CFR40 source material license
- **Rare Earths** (La, Y) - Pyrophoric metal handling
- **Alkaline Earths** (Ca, Mg) - Moisture-sensitive protocols

### Top Candidates (Sheet 5)
Production summaries for leading materials:
- `Zn-Ru` - $80k, 3 weeks
- `Pd-Cd` - $100k, 3 weeks (cadmium toxicity protocols)

## ⚠️ Safety Notes

This script incorporates regulatory compliance requirements:
- **OSHA** - Beryllium PEL (0.2 µg/m³), cadmium (5 µg/m³)
- **NRC** - Radioactive materials (Tc-99, Th)
- **DOE** - High-pressure equipment, Class 4 lasers

**Always consult institutional EH&S before synthesis.**

## 📖 References

For scientific background on correlation-driven superconductivity, see:
- Hirsch & Marsiglio, *Physica C* (2022) - Hole superconductivity theory
- Experimental verification via transport & magnetometry

## 📜 License

MIT License - Academic research use encouraged

## 🤝 Contributing

Pull requests welcome for:
- Additional material recipes
- Cost/timeline updates
- Safety protocol improvements
- Equipment vendor information

---

**Contact:** lurongpan47@gmail.com  
**Last Updated:** 2026-05-18
