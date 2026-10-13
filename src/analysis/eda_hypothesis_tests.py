"""
EDA and Hypothesis Testing for MMR Rental Market Intelligence.

This script performs:
- Exploratory data analysis (distributions, correlations)
- Hypothesis testing with effect sizes
- Statistical tests: Mann-Whitney U, Kruskal-Wallis
"""

import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, kruskal
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "rentals_enriched.csv"

# Load data
print("Loading data...")
df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} rows")
print(f"Columns: {len(df.columns)}")

# ============================================================================
# 1. Basic Statistics
# ============================================================================
print("\n" + "="*60)
print("1. BASIC STATISTICS")
print("="*60)

print(f"Rent - Mean: INR {df['monthly_rent_inr'].mean():,.0f}, Median: INR {df['monthly_rent_inr'].median():,.0f}")
print(f"Rent/sqft - Mean: INR {df['rent_per_sqft_carpet_inr'].mean():.2f}, Median: INR {df['rent_per_sqft_carpet_inr'].median():.2f}")

# Correlation
numeric_cols = ['monthly_rent_inr', 'rent_per_sqft_carpet_inr', 'carpet_area_sqft',
                'bhk', 'nearest_station_distance_km', 'min_dist_to_business_hub_km']
corr_matrix = df[numeric_cols].corr()
print("\nKey correlations with rent_per_sqft:")
print(corr_matrix['rent_per_sqft_carpet_inr'].sort_values(ascending=False))

# ============================================================================
# 2. Hypothesis Testing
# ============================================================================
print("\n" + "="*60)
print("2. HYPOTHESIS TESTING")
print("="*60)

# H1: Furnished vs Unfurnished
print("\nH1: Furnished flats have higher rent/sqft than unfurnished")
print("-" * 60)

furnished = df[df['furnishing'] == 'fully_furnished']['rent_per_sqft_carpet_inr']
unfurnished = df[df['furnishing'] == 'unfurnished']['rent_per_sqft_carpet_inr']

print(f"Furnished - n={len(furnished)}, Mean: ₹{furnished.mean():.2f}, Median: ₹{furnished.median():.2f}")
print(f"Unfurnished - n={len(unfurnished)}, Mean: ₹{unfurnished.mean():.2f}, Median: ₹{unfurnished.median():.2f}")
print(f"Difference: ₹{furnished.mean() - unfurnished.mean():.2f} ({(furnished.mean()/unfurnished.mean()-1)*100:.1f}%)")

# Mann-Whitney U test
stat, p_value_h1 = mannwhitneyu(furnished, unfurnished, alternative='greater')
print(f"\nMann-Whitney U test: statistic={stat:.2f}, p-value={p_value_h1:.2e}")

# Effect size (Cohen's d)
pooled_std = np.sqrt((furnished.std()**2 + unfurnished.std()**2) / 2)
cohens_d_h1 = (furnished.mean() - unfurnished.mean()) / pooled_std
print(f"Cohen's d: {cohens_d_h1:.3f}")

# Bootstrap CI (1000 iterations for speed)
n_bootstraps = 1000
boot_diffs = []
for _ in range(n_bootstraps):
    sample_f = np.random.choice(furnished, size=len(furnished), replace=True)
    sample_u = np.random.choice(unfurnished, size=len(unfurnished), replace=True)
    boot_diffs.append(sample_f.mean() - sample_u.mean())

ci_lower_h1 = np.percentile(boot_diffs, 2.5)
ci_upper_h1 = np.percentile(boot_diffs, 97.5)
print(f"Bootstrap 95% CI for difference: [₹{ci_lower_h1:.2f}, ₹{ci_upper_h1:.2f}]")

# H2: Station proximity
print("\n" + "="*60)
print("H2: Rent/sqft differs by station proximity")
print("-" * 60)

near_station = df[df['near_station_1km'] == True]['rent_per_sqft_carpet_inr']
far_station = df[df['nearest_station_distance_km'] > 2]['rent_per_sqft_carpet_inr']

print(f"Within 1km - n={len(near_station)}, Mean: ₹{near_station.mean():.2f}, Median: ₹{near_station.median():.2f}")
print(f"Beyond 2km - n={len(far_station)}, Mean: ₹{far_station.mean():.2f}, Median: ₹{far_station.median():.2f}")
print(f"Difference: ₹{near_station.mean() - far_station.mean():.2f} ({(near_station.mean()/far_station.mean()-1)*100:.1f}%)")

# Mann-Whitney U test
stat, p_value_h2 = mannwhitneyu(near_station, far_station, alternative='greater')
print(f"\nMann-Whitney U test: statistic={stat:.2f}, p-value={p_value_h2:.2e}")

# Effect size
pooled_std = np.sqrt((near_station.std()**2 + far_station.std()**2) / 2)
cohens_d_h2 = (near_station.mean() - far_station.mean()) / pooled_std
print(f"Cohen's d: {cohens_d_h2:.3f}")

# Bootstrap CI
boot_diffs = []
for _ in range(1000):
    sample_near = np.random.choice(near_station, size=len(near_station), replace=True)
    sample_far = np.random.choice(far_station, size=len(far_station), replace=True)
    boot_diffs.append(sample_near.mean() - sample_far.mean())

ci_lower_h2 = np.percentile(boot_diffs, 2.5)
ci_upper_h2 = np.percentile(boot_diffs, 97.5)
print(f"Bootstrap 95% CI for difference: [₹{ci_lower_h2:.2f}, ₹{ci_upper_h2:.2f}]")

# H3: Localities
print("\n" + "="*60)
print("H3: Rent/sqft differs across localities")
print("-" * 60)

locality_groups = [group['rent_per_sqft_carpet_inr'].values for name, group in df.groupby('locality')]

stat, p_value_h3 = kruskal(*locality_groups)
print(f"Kruskal-Wallis test: statistic={stat:.2f}, p-value={p_value_h3:.2e}")
print(f"Number of localities: {len(locality_groups)}")

# Effect size
n_total = len(df)
eta_squared = (stat - len(locality_groups) + 1) / (n_total)
print(f"Eta-squared (effect size): {eta_squared:.3f}")

# Top and bottom localities
locality_stats = df.groupby('locality')['rent_per_sqft_carpet_inr'].agg(['mean', 'count']).sort_values('mean', ascending=False)
print("\nTop 5 localities by rent/sqft:")
print(locality_stats.head(10))
print("\nBottom 5 localities by rent/sqft:")
print(locality_stats.tail(10))

# ============================================================================
# 3. Summary
# ============================================================================
print("\n" + "="*60)
print("SUMMARY OF HYPOTHESIS TEST RESULTS")
print("="*60)

print("\nH1: Furnished flats have higher rent/sqft than unfurnished")
print(f"- Furnished avg: ₹{furnished.mean():.2f}/sqft")
print(f"- Unfurnished avg: ₹{unfurnished.mean():.2f}/sqft")
print(f"- Difference: ₹{furnished.mean() - unfurnished.mean():.2f}/sqft ({(furnished.mean()/unfurnished.mean()-1)*100:.1f}% premium)")
print(f"- Mann-Whitney p-value: {p_value_h1:.2e}")
print(f"- Cohen's d: {cohens_d_h1:.3f}")
print(f"- Bootstrap 95% CI: [₹{ci_lower_h1:.2f}, ₹{ci_upper_h1:.2f}]")
print(f"- CONCLUSION: {'REJECTED' if p_value_h1 < 0.05 else 'FAILED TO REJECT'}")

print("\nH2: Rent/sqft differs by station proximity")
print(f"- Within 1km avg: ₹{near_station.mean():.2f}/sqft")
print(f"- Beyond 2km avg: ₹{far_station.mean():.2f}/sqft")
print(f"- Difference: ₹{near_station.mean() - far_station.mean():.2f}/sqft ({(near_station.mean()/far_station.mean()-1)*100:.1f}% premium)")
print(f"- Mann-Whitney p-value: {p_value_h2:.2e}")
print(f"- Cohen's d: {cohens_d_h2:.3f}")
print(f"- Bootstrap 95% CI: [₹{ci_lower_h2:.2f}, ₹{ci_upper_h2:.2f}]")
print(f"- CONCLUSION: {'REJECTED' if p_value_h2 < 0.05 else 'FAILED TO REJECT'}")

print("\nH3: Rent/sqft differs across localities")
print(f"- Kruskal-Wallis p-value: {p_value_h3:.2e}")
print(f"- Eta-squared: {eta_squared:.3f}")
print(f"- CONCLUSION: {'REJECTED' if p_value_h3 < 0.05 else 'FAILED TO REJECT'}")

print("\n" + "="*60)
print("EDA and Hypothesis Testing Complete")
print("="*60)
