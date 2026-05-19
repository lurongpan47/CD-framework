#!/usr/bin/env python3
"""Update the CD Superconductor Screening Excel with production process details."""
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = load_workbook("CD_Superconductor_Screen.xlsx")

# ═══════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════
hdr_font = Font(name='Arial', bold=True, size=9, color='FFFFFF')
hdr_fill = PatternFill('solid', fgColor='2F5496')
data_font = Font(name='Arial', size=8)
wrap_align = Alignment(horizontal='left', vertical='top', wrap_text=True)
green_fill = PatternFill('solid', fgColor='C6EFCE')
yellow_fill = PatternFill('solid', fgColor='FFEB9C')
blue_fill = PatternFill('solid', fgColor='D6E4F0')

def add_header(ws, col, text, width=25):
    c = ws.cell(row=1, column=col, value=text)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = Alignment(horizontal='center', wrap_text=True)
    ws.column_dimensions[get_column_letter(col)].width = width

# ═══════════════════════════════════════════
# Sheet 2: Binary Pairs — add Production Process columns
# ═══════════════════════════════════════════
ws2 = wb["Binary Pairs"]
add_header(ws2, 13, "Production Method", 30)
add_header(ws2, 14, "Precursors", 25)
add_header(ws2, 15, "Temperature Profile", 30)
add_header(ws2, 16, "Atmosphere/Pressure", 18)
add_header(ws2, 17, "Post-Treatment", 25)
add_header(ws2, 18, "Equipment Needed", 25)
add_header(ws2, 19, "Est. Cost ($)", 15)
add_header(ws2, 20, "Timeline", 12)
add_header(ws2, 21, "Safety Notes", 25)

# Production data for binary pairs
production_db = {
    "default_d-d": {
        "method": "Arc melting (Cu hearth, W electrode) + long anneal",
        "precursors": "Elemental pieces 99.9%+ purity, weighed in Ar glovebox",
        "temp": "Arc: 200-400A DC, 20-40s × 4-6 remelts; Anneal: 1000-1200°C for 100-400h, cool 5-10°C/h",
        "atm": "5N Ar (0.5 atm), Ti/Zr getter pre-melted",
        "post": "Slow cool through ordering T; XRD phase check; polish for transport",
        "equip": "Arc melter ($30-60k), tube furnace ($10-25k), glovebox ($30-80k)",
        "cost": "$50-150k (lab setup)",
        "timeline": "2-4 weeks",
        "safety": "Pyrophoric metals (Sc,Y,La); UV from arc; standard PPE + Ar glovebox"
    },
    "default_hydride": {
        "method": "Diamond Anvil Cell (DAC) + laser heating + NH3BH3 H-source",
        "precursors": "Metal foil 1-2µm + ammonia borane (NH3BH3); Rhenium gasket",
        "temp": "Laser heat 1064nm YAG pulsed 0.3-1s at 1700-2000K after compression",
        "atm": "80-200 GPa in DAC; ruby fluorescence pressure calibration",
        "post": "In-situ synchrotron XRD (APS/ESRF); 4-probe transport; NV magnetometry",
        "equip": "Symmetric DAC ($5-20k), YAG laser ($50-100k), synchrotron beamtime",
        "cost": "$300k-1M (setup) + beamtime",
        "timeline": "6-12 months",
        "safety": "High-pressure hazard (blast shield); Class 4 laser; Be handling if used (OSHA PEL 0.2µg/m³)"
    },
    "C-Sc": {
        "method": "Arc melting Sc+C → Sc3C4; or high-P for ScCx phases",
        "precursors": "Sc ingot (99.99% Ames-distilled, <300ppm O) + spectroscopic graphite",
        "temp": "Arc: 200A, 5 remelts; Anneal in Ta tube at 1400-1700°C for 1-7 days, cool 5-10°C/h",
        "atm": "5N Ar; Ta tube sealed by arc welding, jacketed in evacuated quartz",
        "post": "Powder XRD to confirm Sc3C4 (P4/mnc); SQUID R(T) down to 1.8K",
        "equip": "Arc melter, high-T tube furnace (1700°C capable), glovebox, SQUID/PPMS",
        "cost": "$100-200k (Sc metal ~$200/g)",
        "timeline": "3-6 weeks",
        "safety": "Sc pyrophoric as powder (bulk only!); O contamination → oxycarbide"
    },
    "Mo-Tc": {
        "method": "Arc melting Mo+Tc under radiological containment",
        "precursors": "Mo pieces 99.95% + Tc-99 metal (DOE Isotope Program, ORNL)",
        "temp": "Arc: 300A, 6 remelts; Anneal 1000°C/200h in sealed Ta",
        "atm": "Ar glovebox with HEPA exhaust; negative pressure containment",
        "post": "XRD for A15/α-Mn phase; R(T) with shielded cryostat",
        "equip": "Licensed radiological facility; dedicated arc melter; GM monitors",
        "cost": "$500k+ (licensing + facility)",
        "timeline": "12-18 months (procurement)",
        "safety": "NRC 10CFR30 license for Tc-99; β-emitter 294keV; plexiglas shielding; BeLPT"
    },
    "Nb-V": {
        "method": "Arc melting → bcc solid solution",
        "precursors": "Nb rod 99.9% + V pieces 99.7%, cut in Ar glovebox",
        "temp": "Arc: 250A, 4 remelts; Anneal 1200°C/48h",
        "atm": "5N Ar",
        "post": "XRD (bcc single phase); R(T) to 2K",
        "equip": "Arc melter, tube furnace, PPMS",
        "cost": "$50-100k",
        "timeline": "2-3 weeks",
        "safety": "Standard arc melting PPE; Nb/V non-toxic"
    },
}

for row in range(2, ws2.max_row + 1):
    pair = ws2.cell(row, 2).value
    if not pair:
        continue

    # Select production data
    if pair in production_db:
        pd = production_db[pair]
    elif "H" in str(ws2.cell(row, 2).value):
        pd = production_db["default_hydride"]
    else:
        pd = production_db["default_d-d"]

    for col, key in [(13,"method"),(14,"precursors"),(15,"temp"),(16,"atm"),
                     (17,"post"),(18,"equip"),(19,"cost"),(20,"timeline"),(21,"safety")]:
        c = ws2.cell(row, col, pd[key])
        c.font = data_font
        c.alignment = wrap_align

# ═══════════════════════════════════════════
# Sheet 3: Ternary Hydrides — add Production columns
# ═══════════════════════════════════════════
ws3 = wb["Ternary Hydrides"]
add_header(ws3, 12, "Synthesis Method", 30)
add_header(ws3, 13, "Precursors & H-Source", 28)
add_header(ws3, 14, "DAC Parameters", 30)
add_header(ws3, 15, "Laser Heating", 25)
add_header(ws3, 16, "Phase Confirmation", 25)
add_header(ws3, 17, "SC Confirmation", 28)
add_header(ws3, 18, "Equipment", 25)
add_header(ws3, 19, "Est. Cost", 12)
add_header(ws3, 20, "Safety", 25)

for row in range(2, ws3.max_row + 1):
    formula = ws3.cell(row, 2).value
    if not formula:
        continue

    pressure = ws3.cell(row, 10).value or ""
    sym1 = ws3.cell(row, 3).value or ""
    sym2 = ws3.cell(row, 4).value or ""

    # Customize based on elements
    h_source = "NH3BH3 (ammonia borane)"
    if "Be" in (sym1, sym2):
        h_source = "NH3BH3 + CAUTION: Be requires OSHA 29 CFR 1910.1024"
        safety = "BERYLLIUM: 0.2µg/m³ PEL; HEPA glovebox; BeLPT medical surveillance; PAPR for any machining!"
    elif "Th" in (sym1, sym2):
        h_source = "NH3BH3; Th requires NRC 10CFR40 source material license"
        safety = "THORIUM: α-emitter, source material license; standard radiological controls"
    elif "La" in (sym1, sym2) or "Y" in (sym1, sym2):
        safety = "Pyrophoric rare earth metals (handle under Ar); laser safety Class 4"
    elif "Ca" in (sym1, sym2) or "Mg" in (sym1, sym2):
        safety = "Ca/Mg react with moisture; handle under Ar; standard DAC hazards"
    else:
        safety = "Standard high-pressure DAC safety; blast shield; Class 4 laser"

    if "ambient" in str(pressure):
        method = "Bulk synthesis: arc melt A-B alloy + gas-phase H2 loading at 1-10 kbar"
        dac = "Not required (ambient P); gas-phase H2 vessel at 300-500°C"
        laser = "N/A for ambient; anneal 500-800°C under H2"
        equip = "Arc melter, H2 gas vessel (rated 10 kbar), tube furnace"
        cost = "$100-300k"
    else:
        method = "DAC synthesis: arc-melt A-B foil + NH3BH3 in symmetric DAC"
        dac = f"80-150µm beveled culets; Re gasket pre-indented 30-40µm; compress to {pressure}"
        laser = "1064nm YAG/1070nm fiber; 0.3-1s pulses; 1700-2000K; double-sided flat-top 10-30µm"
        equip = "Symmetric DAC, YAG laser, synchrotron beamline, dilution fridge"
        cost = "$300k-1M"

    phase_confirm = "In-situ synchrotron XRD (0.3-0.6Å, 5µm spot); Raman spectroscopy"
    sc_confirm = "4-probe R(T) with FIB-cut electrodes; Hc2(T) WHH fit; NV-diamond magnetometry"

    for col, val in [(12,method),(13,f"{sym1}+{sym2} foil + {h_source}"),(14,dac),
                     (15,laser),(16,phase_confirm),(17,sc_confirm),(18,equip),(19,cost),(20,safety)]:
        c = ws3.cell(row, col, val)
        c.font = data_font
        c.alignment = wrap_align

# ═══════════════════════════════════════════
# Sheet 5: TOP CANDIDATES — add Production Summary
# ═══════════════════════════════════════════
ws5 = wb["★ TOP CANDIDATES"]
add_header(ws5, 10, "Synthesis Route", 35)
add_header(ws5, 11, "Key Equipment", 25)
add_header(ws5, 12, "Est. Cost & Timeline", 20)
add_header(ws5, 13, "Critical Safety", 30)

# Top candidates production summaries
top_production = {
    "C-Sc": ("Arc melt Sc(Ames)+C in Ar → anneal Ta tube 1500°C/7d → slow cool",
             "Arc melter, 1700°C furnace, glovebox, PPMS",
             "$150k; 4-6 weeks",
             "Sc pyrophoric (bulk only); O contamination control critical"),
    "Mo-Tc": ("Arc melt under Tc-99 license → anneal 1000°C/200h → A15 phase",
              "Licensed rad facility, dedicated arc melter, SQUID",
              "$500k+; 12-18 mo",
              "NRC Tc-99 license required; β-emitter; negative-P glovebox"),
    "Zn-Ru": ("Arc melt Zn+Ru in Ar → homogenize 800°C/100h",
              "Arc melter, tube furnace, PPMS",
              "$80k; 3 weeks",
              "Zn fumes (ventilation); Ru non-toxic; standard"),
    "Pd-Cd": ("Arc melt → anneal 600°C/72h → slow cool for ordering",
              "Arc melter, furnace, SQUID",
              "$100k; 3 weeks",
              "Cd toxic (PEL 5µg/m³); ventilated glovebox required"),
}

for row in range(5, ws5.max_row + 1):
    formula = ws5.cell(row, 3).value
    mat_type = ws5.cell(row, 2).value
    if not formula:
        continue

    if formula in top_production:
        route, equip, cost_time, safety = top_production[formula]
    elif "Ternary" in str(mat_type):
        cond = ws5.cell(row, 5).value or ""
        if "ambient" in str(cond):
            route = f"Arc melt alloy → gas-phase H2 loading at 1-10 kbar, 300-500°C"
            equip = "Arc melter, H2 vessel, furnace, PPMS"
            cost_time = "$150-300k; 4-8 weeks"
        else:
            route = f"DAC: arc-melt foil + NH3BH3 → compress → laser heat 1700-2000K"
            equip = "Symmetric DAC, YAG laser, synchrotron, dil. fridge"
            cost_time = "$300k-1M; 6-12 months"
        safety = "High-P DAC blast shield; Class 4 laser; element-specific (see Sheet 3)"
    else:
        route = "Arc melt in Ar → anneal for phase ordering → slow cool"
        equip = "Arc melter, tube furnace, glovebox, PPMS"
        cost_time = "$80-150k; 3-6 weeks"
        safety = "Standard arc melting PPE; element-specific hazards (see Sheet 2)"

    for col, val in [(10,route),(11,equip),(12,cost_time),(13,safety)]:
        c = ws5.cell(row, col, val)
        c.font = data_font
        c.alignment = wrap_align

# Save the updated workbook
wb.save("CD_Superconductor_Screen_with_Production.xlsx")
print("✓ Production details added successfully!")
print("✓ Output: CD_Superconductor_Screen_with_Production.xlsx")
