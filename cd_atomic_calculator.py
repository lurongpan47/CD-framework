#!/usr/bin/env python3
"""
Communication Dynamics (CD) Atomic Energy Calculator
Based on: Pan & Tanik (2026) PRX paper
Calculates orbital energies and radii for the entire periodic table
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
from dataclasses import dataclass

# Physical constants
E_RYDBERG = 13.6056980659  # eV (CODATA 2018)
ALPHA_CD = 0.0118  # CD noise constant (calibrated from Na D-doublet)
HBAR = 1.054571817e-34  # J·s
M_E = 9.1093837015e-31  # kg
BOHR_RADIUS = 0.529177210903  # Å (a₀)

@dataclass
class OrbitalState:
    """CD orbital quantum state"""
    n: int  # Principal quantum number
    l: int  # Angular momentum
    m_l: int  # Magnetic quantum number
    Z_eff: float  # Effective nuclear charge
    
    @property
    def multiplicity(self) -> int:
        """Channel multiplicity M = 2ℓ+1"""
        return 2 * self.l + 1
    
    @property
    def jump_step(self) -> int:
        """Star polygon jump step a = n+1"""
        return self.n + 1


class CDAtomicCalculator:
    """
    Communication Dynamics atomic energy calculator
    Implements the error-content polygon Fourier framework
    """
    
    def __init__(self):
        """Initialize calculator with Slater shielding rules"""
        self.slater_rules = self._load_slater_rules()
    
    def _load_slater_rules(self) -> Dict:
        """
        Slater effective nuclear charge rules
        Returns: {orbital: {screening_group: shielding_constant}}
        """
        return {
            '1s': {'1s': 0.30, 'higher': 0.00},
            '2s': {'1s': 0.85, '2s2p': 0.35, 'higher': 0.00},
            '2p': {'1s': 0.85, '2s2p': 0.35, 'higher': 0.00},
            '3s': {'1s': 1.00, '2s2p': 0.85, '3s3p': 0.35, 'higher': 0.00},
            '3p': {'1s': 1.00, '2s2p': 0.85, '3s3p': 0.35, 'higher': 0.00},
            '3d': {'1s': 1.00, '2s2p': 1.00, '3s3p': 1.00, '3d': 0.35, 'higher': 0.00},
            '4s': {'1s': 1.00, '2s2p': 1.00, '3s3p3d': 0.85, '4s4p': 0.35, 'higher': 0.00},
            '4p': {'1s': 1.00, '2s2p': 1.00, '3s3p3d': 0.85, '4s4p': 0.35, 'higher': 0.00},
            '4d': {'1s': 1.00, '2s2p': 1.00, '3s3p': 1.00, '3d': 1.00, '4s4p': 1.00, '4d': 0.35},
            '5s': {'inner': 1.00, '4d': 0.85, '5s5p': 0.35},
        }
    
    def calculate_Z_eff(self, Z: int, orbital: str, electron_config: Dict[str, int]) -> float:
        """
        Calculate effective nuclear charge using Slater's rules
        
        Args:
            Z: Atomic number
            orbital: Orbital designation (e.g., '3d', '4s')
            electron_config: Electron configuration {orbital: count}
        
        Returns:
            Z_eff: Effective nuclear charge
        """
        n, l_symbol = int(orbital[0]), orbital[1]
        
        # Simple Slater approximation
        if n == 1:
            screening = 0.30 * (electron_config.get('1s', 0) - 1)
        elif n == 2:
            screening = 0.85 * electron_config.get('1s', 0) + \
                       0.35 * (electron_config.get('2s', 0) + electron_config.get('2p', 0) - 1)
        elif n == 3:
            screening = 1.00 * electron_config.get('1s', 0) + \
                       0.85 * (electron_config.get('2s', 0) + electron_config.get('2p', 0)) + \
                       0.35 * (electron_config.get('3s', 0) + electron_config.get('3p', 0) + 
                              electron_config.get('3d', 0) - 1)
        elif n == 4:
            screening = 1.00 * (electron_config.get('1s', 0) + electron_config.get('2s', 0) + 
                               electron_config.get('2p', 0) + electron_config.get('3s', 0) + 
                               electron_config.get('3p', 0)) + \
                       0.85 * electron_config.get('3d', 0) + \
                       0.35 * (electron_config.get('4s', 0) + electron_config.get('4p', 0) + 
                              electron_config.get('4d', 0) - 1)
        else:
            # Simplified for n ≥ 5
            screening = Z - n * 2
        
        Z_eff = max(Z - screening, 1.0)
        return Z_eff
    
    def fourier_shape_factor(self, n: int, l: int) -> float:
        """
        Calculate Fourier shape factor F_ℓ(n)
        Eq. (6) from paper
        
        Args:
            n: Principal quantum number
            l: Angular momentum quantum number
        
        Returns:
            F_l: Fourier shape factor (dimensionless)
        """
        if l == 0:
            return 0.0
        
        # Sum over m_l from -l to +l
        numerator = 0.0
        denominator = 0.0
        
        for m_l in range(-l, l + 1):
            # U_m coefficient from Eq. (5)
            U_m_sq = 1.0 / (n/2 + 3*m_l)**4  # Squared magnitude
            numerator += m_l**2 * U_m_sq
            denominator += U_m_sq
        
        F_l = numerator / denominator if denominator > 0 else 0.0
        return F_l
    
    def base_energy(self, n: int, l: int, Z_eff: float) -> float:
        """
        Calculate base CD energy E_CD^(0)
        Eq. (7) from paper
        
        Args:
            n: Principal quantum number
            l: Angular momentum quantum number
            Z_eff: Effective nuclear charge
        
        Returns:
            E_0: Base energy in eV
        """
        F_l = self.fourier_shape_factor(n, l)
        E_0 = -(Z_eff**2 * E_RYDBERG / n**2) * (1 + 0.1 * F_l)
        return E_0
    
    def shannon_correction(self, n: int, l: int, Z_eff: float, E_0: float) -> float:
        """
        Calculate Shannon correction (fine-structure analogue)
        Eq. (8) from paper
        
        Args:
            n: Principal quantum number
            l: Angular momentum quantum number
            Z_eff: Effective nuclear charge
            E_0: Base energy
        
        Returns:
            ΔE_Shannon: Shannon correction in eV
        """
        if l == 0:
            return 0.0  # No Shannon correction for s-states
        
        denominator = n**3 * l * (l + 0.5) * (l + 1)
        Delta_E = -E_0 * (ALPHA_CD**2 * Z_eff**4) / denominator
        return Delta_E
    
    def fisher_correction(self, n: int, l: int, Z_eff: float) -> float:
        """
        Calculate Fisher information correction (Lamb-shift analogue)
        Eq. (10) from paper
        
        Args:
            n: Principal quantum number
            l: Angular momentum quantum number
            Z_eff: Effective nuclear charge
        
        Returns:
            ΔE_Fisher: Fisher correction in eV
        """
        if l != 0:
            return 0.0  # Fisher correction only for s-states
        
        # Discrete Fisher information for delta-localized distribution
        # I_CD[ρ] ~ Z_eff^2 / (n * a₀^2)
        I_CD = (Z_eff / (n * BOHR_RADIUS))**2
        
        # Convert to eV: (ℏ²/8m_e) * I_CD
        Delta_E_Fisher = (HBAR**2 / (8 * M_E)) * I_CD
        # Convert J to eV
        Delta_E_Fisher *= 6.241509074e18  # J to eV conversion
        
        return Delta_E_Fisher
    
    def total_energy(self, n: int, l: int, Z_eff: float) -> Tuple[float, Dict[str, float]]:
        """
        Calculate total CD energy with all corrections
        Eq. (12) from paper
        
        Args:
            n: Principal quantum number
            l: Angular momentum quantum number
            Z_eff: Effective nuclear charge
        
        Returns:
            E_total: Total energy in eV
            breakdown: Dictionary with energy component breakdown
        """
        E_0 = self.base_energy(n, l, Z_eff)
        Delta_Shannon = self.shannon_correction(n, l, Z_eff, E_0)
        Delta_Fisher = self.fisher_correction(n, l, Z_eff)
        
        E_total = E_0 + Delta_Shannon + Delta_Fisher
        
        breakdown = {
            'E_base': E_0,
            'Delta_Shannon': Delta_Shannon,
            'Delta_Fisher': Delta_Fisher,
            'E_total': E_total
        }
        
        return E_total, breakdown
    
    def orbital_radius(self, n: int, l: int, Z_eff: float) -> float:
        """
        Calculate expectation value of orbital radius ⟨r⟩
        Hydrogenic approximation with CD correction
        
        Args:
            n: Principal quantum number
            l: Angular momentum quantum number
            Z_eff: Effective nuclear charge
        
        Returns:
            <r>: Expectation value of radius in Bohr radii (a₀)
        """
        # Hydrogenic formula: ⟨r⟩ = (n²/Z_eff)[1 + 0.5(1 - l(l+1)/n²)]
        r_hydro = (n**2 / Z_eff) * (1 + 0.5 * (1 - l*(l+1)/n**2))
        
        # CD correction factor from Fourier shape
        F_l = self.fourier_shape_factor(n, l)
        r_CD = r_hydro * (1 + 0.05 * F_l)  # Empirical 5% correction
        
        return r_CD


class PeriodicTableCalculator:
    """
    Calculate CD energies and radii for the entire periodic table
    """
    
    def __init__(self):
        self.cd_calc = CDAtomicCalculator()
        self.electron_configs = self._load_electron_configs()
    
    def _load_electron_configs(self) -> Dict[int, Dict[str, int]]:
        """
        Load ground-state electron configurations
        Returns: {Z: {orbital: electron_count}}
        """
        configs = {}
        
        # Simplified aufbau for Z=1-54
        # Full implementation would include Hund's rules and exceptions
        
        # 1s: H, He
        configs[1] = {'1s': 1}
        configs[2] = {'1s': 2}
        
        # 2s, 2p: Li-Ne
        for Z in range(3, 11):
            configs[Z] = {'1s': 2, '2s': min(Z-2, 2), '2p': max(0, Z-4)}
        
        # 3s, 3p: Na-Ar
        for Z in range(11, 19):
            configs[Z] = {'1s': 2, '2s': 2, '2p': 6, '3s': min(Z-10, 2), '3p': max(0, Z-12)}
        
        # 4s, 3d, 4p: K-Kr
        for Z in range(19, 37):
            if Z <= 20:  # K, Ca
                configs[Z] = {'1s': 2, '2s': 2, '2p': 6, '3s': 2, '3p': 6, 
                             '4s': Z-18, '3d': 0, '4p': 0}
            elif Z <= 30:  # Sc-Zn (3d filling)
                configs[Z] = {'1s': 2, '2s': 2, '2p': 6, '3s': 2, '3p': 6,
                             '4s': 2, '3d': Z-20, '4p': 0}
            else:  # Ga-Kr
                configs[Z] = {'1s': 2, '2s': 2, '2p': 6, '3s': 2, '3p': 6,
                             '4s': 2, '3d': 10, '4p': Z-30}
        
        # 5s, 4d, 5p: Rb-Xe
        for Z in range(37, 55):
            if Z <= 38:  # Rb, Sr
                configs[Z] = {'1s': 2, '2s': 2, '2p': 6, '3s': 2, '3p': 6,
                             '4s': 2, '3d': 10, '4p': 6, '5s': Z-36, '4d': 0}
            elif Z <= 48:  # Y-Cd (4d filling)
                configs[Z] = {'1s': 2, '2s': 2, '2p': 6, '3s': 2, '3p': 6,
                             '4s': 2, '3d': 10, '4p': 6, '5s': 2, '4d': Z-38}
            else:  # In-Xe
                configs[Z] = {'1s': 2, '2s': 2, '2p': 6, '3s': 2, '3p': 6,
                             '4s': 2, '3d': 10, '4p': 6, '5s': 2, '4d': 10, '5p': Z-48}
        
        return configs
    
    def calculate_atom(self, Z: int, valence_only: bool = False) -> pd.DataFrame:
        """
        Calculate all orbital energies and radii for an atom
        
        Args:
            Z: Atomic number
            valence_only: If True, only calculate valence shell
        
        Returns:
            DataFrame with orbital energies and radii
        """
        if Z not in self.electron_configs:
            raise ValueError(f"Electron configuration for Z={Z} not available")
        
        config = self.electron_configs[Z]
        results = []
        
        for orbital, count in config.items():
            if count == 0:
                continue
            
            n = int(orbital[0])
            l_symbol = orbital[1]
            l = {'s': 0, 'p': 1, 'd': 2, 'f': 3}[l_symbol]
            
            # Calculate Z_eff for this orbital
            Z_eff = self.cd_calc.calculate_Z_eff(Z, orbital, config)
            
            # Calculate energy and radius
            E_total, breakdown = self.cd_calc.total_energy(n, l, Z_eff)
            r_avg = self.cd_calc.orbital_radius(n, l, Z_eff)
            
            results.append({
                'Z': Z,
                'orbital': orbital,
                'n': n,
                'l': l,
                'occupancy': count,
                'Z_eff': Z_eff,
                'E_base_eV': breakdown['E_base'],
                'Delta_Shannon_eV': breakdown['Delta_Shannon'],
                'Delta_Fisher_eV': breakdown['Delta_Fisher'],
                'E_total_eV': E_total,
                'r_avg_bohr': r_avg,
                'r_avg_angstrom': r_avg * BOHR_RADIUS
            })
        
        df = pd.DataFrame(results)
        
        # Calculate valence electron energy (HOMO)
        if len(df) > 0:
            valence_energy = df['E_total_eV'].iloc[-1]
            df['is_valence'] = df['E_total_eV'] == valence_energy
        
        return df
    
    def calculate_periodic_table(self, Z_max: int = 54) -> pd.DataFrame:
        """
        Calculate CD energies for entire periodic table
        
        Args:
            Z_max: Maximum atomic number (default 54 for Xe)
        
        Returns:
            DataFrame with all atomic orbital data
        """
        all_results = []
        
        for Z in range(1, Z_max + 1):
            try:
                df_atom = self.calculate_atom(Z, valence_only=False)
                all_results.append(df_atom)
            except Exception as e:
                print(f"Warning: Failed to calculate Z={Z}: {e}")
                continue
        
        df_full = pd.concat(all_results, ignore_index=True)
        return df_full


def main():
    """
    Main calculation routine
    """
    print("=" * 70)
    print("Communication Dynamics (CD) Atomic Calculator")
    print("Based on: Pan & Tanik (2026) PRX paper")
    print("=" * 70)
    print()
    
    # Initialize calculator
    calc = PeriodicTableCalculator()
    
    # Example: Calculate hydrogen atom
    print("Example 1: Hydrogen atom (Z=1)")
    print("-" * 70)
    df_H = calc.calculate_atom(Z=1)
    print(df_H[['orbital', 'Z_eff', 'E_total_eV', 'r_avg_angstrom']].to_string(index=False))
    print()
    
    # Example: Calculate sodium atom (Na D-doublet calibration)
    print("Example 2: Sodium atom (Z=11) - Na D-doublet")
    print("-" * 70)
    df_Na = calc.calculate_atom(Z=11)
    print(df_Na[['orbital', 'Z_eff', 'E_base_eV', 'Delta_Shannon_eV', 'E_total_eV']].to_string(index=False))
    
    # Calculate Na 3p fine structure splitting
    p_states = df_Na[df_Na['orbital'] == '3p']
    if len(p_states) > 0:
        Delta_Shannon = p_states['Delta_Shannon_eV'].values[0]
        print(f"\nNa 3p Shannon correction: {Delta_Shannon*1000:.3f} meV")
        print(f"Experimental D-doublet: 2.07 meV")
        print(f"(Used for α_CD calibration)")
    print()
    
    # Example: Transition metal (Fe)
    print("Example 3: Iron (Z=26) - 3d transition metal")
    print("-" * 70)
    df_Fe = calc.calculate_atom(Z=26)
    print(df_Fe[['orbital', 'occupancy', 'Z_eff', 'E_total_eV', 'r_avg_angstrom']].to_string(index=False))
    print()
    
    # Calculate entire periodic table
    print("Calculating entire periodic table (Z=1-54)...")
    print("-" * 70)
    df_full = calc.calculate_periodic_table(Z_max=54)
    
    # Save to CSV
    output_file = "cd_periodic_table_energies.csv"
    df_full.to_csv(output_file, index=False, float_format='%.6f')
    print(f"✓ Saved to {output_file}")
    print(f"✓ Total orbitals calculated: {len(df_full)}")
    print()
    
    # Summary statistics
    print("Summary: Valence orbital energies")
    print("-" * 70)
    df_valence = df_full[df_full['is_valence'] == True]
    summary = df_valence.groupby('orbital').agg({
        'Z': 'count',
        'E_total_eV': ['mean', 'min', 'max'],
        'r_avg_angstrom': ['mean', 'min', 'max']
    }).round(3)
    print(summary)
    print()
    
    print("=" * 70)
    print("Calculation complete!")
    print("Use this data for:")
    print("  - Superconductor screening (χ_CD pairing susceptibility)")
    print("  - Battery cathode voltage prediction")
    print("  - Catalytic d-band centre calculation")
    print("  - Thermoelectric Seebeck coefficient estimation")
    print("=" * 70)


if __name__ == "__main__":
    main()
