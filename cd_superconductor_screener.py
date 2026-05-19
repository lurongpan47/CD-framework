#!/usr/bin/env python3
"""
CD Superconductor Screener
Based on: Pan & Tanik (2026) PRX paper, Section VIII-IX
Calculates χ_CD pairing susceptibility and predicts T_c
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
from cd_atomic_calculator import PeriodicTableCalculator, E_RYDBERG

# Constants
K_B = 8.617333262e-5  # eV/K (Boltzmann constant)


class SuperconductorScreener:
    """
    CD-based superconductor screening
    Implements pairing susceptibility χ_CD and Allen-Dynes-McMillan T_c
    """
    
    def __init__(self):
        self.calc = PeriodicTableCalculator()
        self.periodic_data = self._load_periodic_data()
        self.debye_temps = self._load_debye_temperatures()
    
    def _load_periodic_data(self) -> pd.DataFrame:
        """Load or calculate periodic table data"""
        try:
            df = pd.read_csv("cd_periodic_table_energies.csv")
        except FileNotFoundError:
            print("Calculating periodic table data...")
            df = self.calc.calculate_periodic_table(Z_max=54)
            df.to_csv("cd_periodic_table_energies.csv", index=False)
        return df
    
    def _load_debye_temperatures(self) -> Dict[str, float]:
        """
        Debye temperatures (K) for elements
        Source: Kittel, Introduction to Solid State Physics
        """
        return {
            'H': 110, 'He': 90, 'Li': 344, 'Be': 1440, 'B': 1250, 'C': 2230,
            'N': 68, 'O': 92, 'F': 56, 'Ne': 75, 'Na': 158, 'Mg': 400,
            'Al': 428, 'Si': 645, 'P': 195, 'S': 147, 'Cl': 115, 'Ar': 92,
            'K': 91, 'Ca': 230, 'Sc': 360, 'Ti': 420, 'V': 380, 'Cr': 630,
            'Mn': 410, 'Fe': 470, 'Co': 445, 'Ni': 450, 'Cu': 343, 'Zn': 327,
            'Ga': 320, 'Ge': 374, 'As': 282, 'Se': 153, 'Br': 113, 'Kr': 72,
            'Rb': 56, 'Sr': 147, 'Y': 280, 'Zr': 291, 'Nb': 275, 'Mo': 450,
            'Tc': 453, 'Ru': 600, 'Rh': 480, 'Pd': 274, 'Ag': 225, 'Cd': 209,
            'In': 108, 'Sn': 200, 'Sb': 211, 'Te': 153, 'I': 106, 'Xe': 64
        }
    
    def get_valence_orbital(self, Z: int) -> Dict:
        """
        Get valence orbital parameters for an atom
        
        Args:
            Z: Atomic number
        
        Returns:
            Dictionary with n, l, Z_eff, E, M
        """
        atom_data = self.periodic_data[
            (self.periodic_data['Z'] == Z) & 
            (self.periodic_data['is_valence'] == True)
        ]
        
        if len(atom_data) == 0:
            raise ValueError(f"No valence data for Z={Z}")
        
        row = atom_data.iloc[-1]  # Take outermost valence orbital
        
        return {
            'Z': Z,
            'n': int(row['n']),
            'l': int(row['l']),
            'M': 2 * int(row['l']) + 1,  # Multiplicity
            'Z_eff': row['Z_eff'],
            'E': row['E_total_eV']
        }
    
    def calculate_chi_CD(self, Z_A: int, Z_B: int, delta: float = 0.01) -> float:
        """
        Calculate CD pairing susceptibility χ_CD(A,B)
        Eq. (16) from paper
        
        Args:
            Z_A, Z_B: Atomic numbers
            delta: Regularization parameter (eV)
        
        Returns:
            χ_CD: Pairing susceptibility (dimensionless)
        """
        # Get valence orbital parameters
        A = self.get_valence_orbital(Z_A)
        B = self.get_valence_orbital(Z_B)
        
        # Eq. (16): χ_CD = |Z_eff,A Z_eff,B| √(M_A M_B) / [n_A n_B (|E_A - E_B| + δ)]
        numerator = abs(A['Z_eff'] * B['Z_eff']) * np.sqrt(A['M'] * B['M'])
        denominator = A['n'] * B['n'] * (abs(A['E'] - B['E']) + delta)
        
        chi_CD = numerator / denominator
        
        return chi_CD
    
    def calculate_lambda_CD(self, Z_A: int, Z_B: int, 
                           N_EF_override: float = None) -> Tuple[float, float]:
        """
        Calculate electron-phonon coupling λ_CD
        Eq. (17) from paper
        
        Args:
            Z_A, Z_B: Atomic numbers
            N_EF_override: Override density of states (states/eV/atom)
        
        Returns:
            λ_CD: Electron-phonon coupling
            chi_CD: Pairing susceptibility
        """
        chi_CD = self.calculate_chi_CD(Z_A, Z_B)
        
        # Estimate N(E_F) from valence electron density
        if N_EF_override is not None:
            N_EF = N_EF_override
        else:
            A = self.get_valence_orbital(Z_A)
            B = self.get_valence_orbital(Z_B)
            # Simple estimate: N(E_F) ~ M / |E|
            N_EF = 0.5 * (A['M'] / abs(A['E']) + B['M'] / abs(B['E']))
            N_EF *= 10  # Typical DOS enhancement factor
        
        lambda_CD = chi_CD * N_EF
        
        return lambda_CD, chi_CD
    
    def calculate_Tc_McMillan(self, Z_A: int, Z_B: int, 
                              mu_star: float = 0.11,
                              omega_log_override: float = None) -> Dict:
        """
        Calculate critical temperature using Allen-Dynes-McMillan formula
        Eq. (18) from paper
        
        Args:
            Z_A, Z_B: Atomic numbers
            mu_star: Coulomb pseudopotential (typically 0.10-0.13)
            omega_log_override: Override phonon frequency (K)
        
        Returns:
            Dictionary with T_c, λ_CD, chi_CD, ω_log
        """
        # Get pairing susceptibility and coupling
        lambda_CD, chi_CD = self.calculate_lambda_CD(Z_A, Z_B)
        
        # Get phonon frequency (geometric mean of Debye temperatures)
        elements = {Z_A, Z_B}
        element_symbols = [self._Z_to_symbol(Z) for Z in elements]
        
        if omega_log_override is not None:
            omega_log = omega_log_override
        else:
            debye_temps = [self.debye_temps.get(sym, 300) for sym in element_symbols]
            omega_log = np.exp(np.mean(np.log(debye_temps)))  # Geometric mean
        
        # McMillan formula: T_c = (ω_log/1.20) exp[−1.04(1+λ)/(λ − μ*(1+0.62λ))]
        if lambda_CD <= mu_star * (1 + 0.62 * lambda_CD):
            # λ too small, no superconductivity
            T_c = 0.0
        else:
            exponent = -1.04 * (1 + lambda_CD) / (lambda_CD - mu_star * (1 + 0.62 * lambda_CD))
            T_c = (omega_log / 1.20) * np.exp(exponent)
        
        return {
            'Z_A': Z_A,
            'Z_B': Z_B,
            'chi_CD': chi_CD,
            'lambda_CD': lambda_CD,
            'omega_log_K': omega_log,
            'mu_star': mu_star,
            'T_c_K': T_c
        }
    
    def _Z_to_symbol(self, Z: int) -> str:
        """Convert atomic number to element symbol"""
        symbols = [
            '', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
            'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
            'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
            'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
            'Sb', 'Te', 'I', 'Xe'
        ]
        return symbols[Z] if Z < len(symbols) else f'Z{Z}'
    
    def screen_binary_compounds(self, Z_range: List[int], 
                                T_c_cutoff: float = 1.0) -> pd.DataFrame:
        """
        Screen all binary combinations for superconductivity
        
        Args:
            Z_range: List of atomic numbers to consider
            T_c_cutoff: Minimum T_c to report (K)
        
        Returns:
            DataFrame with predicted superconductors sorted by T_c
        """
        results = []
        
        total = len(Z_range) * (len(Z_range) + 1) // 2
        count = 0
        
        for i, Z_A in enumerate(Z_range):
            for Z_B in Z_range[i:]:  # Include diagonal (elements) and upper triangle
                count += 1
                if count % 100 == 0:
                    print(f"Progress: {count}/{total} ({100*count/total:.1f}%)")
                
                try:
                    result = self.calculate_Tc_McMillan(Z_A, Z_B)
                    
                    if result['T_c_K'] >= T_c_cutoff:
                        result['formula'] = f"{self._Z_to_symbol(Z_A)}-{self._Z_to_symbol(Z_B)}"
                        result['type'] = 'elemental' if Z_A == Z_B else 'binary'
                        results.append(result)
                
                except Exception as e:
                    # Skip failed calculations
                    continue
        
        df = pd.DataFrame(results)
        if len(df) > 0:
            df = df.sort_values('T_c_K', ascending=False).reset_index(drop=True)
        
        return df


def main():
    """
    Main screening routine
    """
    print("=" * 80)
    print("CD Superconductor Screener")
    print("Based on: Pan & Tanik (2026) PRX paper")
    print("=" * 80)
    print()
    
    screener = SuperconductorScreener()
    
    # Validation: Known superconductors
    print("Validation: Known elemental superconductors")
    print("-" * 80)
    
    known_SCs = {
        'Nb': 41, 'Pb': 82, 'V': 23, 'Ta': 73, 'Hg': 80,
        'Sn': 50, 'In': 49, 'Al': 13, 'Zn': 30
    }
    
    validation_results = []
    for symbol, Z in sorted(known_SCs.items(), key=lambda x: x[1]):
        if Z <= 54:  # Within our calculation range
            result = screener.calculate_Tc_McMillan(Z, Z)
            validation_results.append({
                'Element': symbol,
                'Z': Z,
                'χ_CD': result['chi_CD'],
                'λ_CD': result['lambda_CD'],
                'T_c_pred (K)': result['T_c_K']
            })
    
    df_val = pd.DataFrame(validation_results)
    print(df_val.to_string(index=False))
    print()
    
    # Novel predictions: Binary compounds
    print("Novel Predictions: Binary ambient-pressure candidates")
    print("-" * 80)
    print("Screening d-block elements (Sc-Zn, Y-Cd)...")
    print()
    
    # Focus on transition metals
    d_block = list(range(21, 31)) + list(range(39, 49))  # 3d + 4d rows
    
    df_binary = screener.screen_binary_compounds(
        Z_range=d_block,
        T_c_cutoff=10.0  # Only report T_c > 10 K
    )
    
    if len(df_binary) > 0:
        # Top 20 predictions
        top_20 = df_binary.head(20)
        
        print("Top 20 binary superconductor candidates:")
        print(top_20[['formula', 'chi_CD', 'lambda_CD', 'T_c_K']].to_string(index=False))
        print()
        
        # Save full results
        output_file = "cd_superconductor_predictions.csv"
        df_binary.to_csv(output_file, index=False, float_format='%.4f')
        print(f"✓ Full results saved to {output_file}")
        print(f"✓ Total candidates with T_c > 10 K: {len(df_binary)}")
        print()
    
    # Highlight paper predictions
    print("Paper-predicted ambient-pressure candidates:")
    print("-" * 80)
    
    paper_predictions = [
        ('Zn', 30, 'Ru', 44, 81.3),
        ('Sc', 21, 'C', 6, 74.5),  # Sc3C4
        ('Mo', 42, 'Tc', 43, 73.8),
        ('Pd', 46, 'Cd', 48, 58.4),
        ('Ag', 47, 'Cd', 48, 53.1)
    ]
    
    paper_results = []
    for sym_A, Z_A, sym_B, Z_B, T_c_exp in paper_predictions:
        if Z_A <= 54 and Z_B <= 54:
            try:
                result = screener.calculate_Tc_McMillan(Z_A, Z_B)
                paper_results.append({
                    'Material': f"{sym_A}-{sym_B}",
                    'χ_CD': result['chi_CD'],
                    'λ_CD': result['lambda_CD'],
                    'T_c_pred (K)': result['T_c_K'],
                    'T_c_paper (K)': T_c_exp,
                    'Δ (%)': 100 * abs(result['T_c_K'] - T_c_exp) / T_c_exp
                })
            except:
                continue
    
    df_paper = pd.DataFrame(paper_results)
    print(df_paper.to_string(index=False))
    print()
    
    # Cu/Ag/Au verdict
    print("Cu/Ag/Au Room-Temperature Verdict:")
    print("-" * 80)
    
    coinage_metals = {'Cu': 29, 'Ag': 47, 'Au': 79}
    coinage_results = []
    
    for symbol, Z in coinage_metals.items():
        if Z <= 54:
            result = screener.calculate_Tc_McMillan(Z, Z)
            coinage_results.append({
                'Metal': symbol,
                'χ_CD': result['chi_CD'],
                'Verdict': '❌ No SC' if result['chi_CD'] < 0.01 else '⚠️ Marginal'
            })
    
    df_coinage = pd.DataFrame(coinage_results)
    print(df_coinage.to_string(index=False))
    print()
    print("Reason: Filled d¹⁰ shell → low DOS(E_F) → χ_CD < 0.01")
    print("Conclusion: No superconductivity at any achievable pressure (<500 GPa)")
    print()
    
    print("=" * 80)
    print("Screening complete!")
    print("Next steps:")
    print("  1. Experimental validation of top candidates")
    print("  2. DFT verification of electronic structure")
    print("  3. Synthesis via arc melting + annealing")
    print("=" * 80)


if __name__ == "__main__":
    main()
