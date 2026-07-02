import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import pearsonr
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings("ignore")

# =====================================
# Load Data
# =====================================

df = pd.read_csv("data/processed/berlin_airbnb_cleaned.csv")

os.makedirs("reports", exist_ok=True)
os.makedirs("reports/figures", exist_ok=True)

# =====================================
# Convert numeric columns
# =====================================

numeric_cols = [
    "Price",
    "Accomodates",
    "Bathrooms",
    "Bedrooms",
    "Beds",
    "Guests Included",
    "Min Nights",
    "Reviews",
    "Overall Rating",
    "Accuracy Rating",
    "Cleanliness Rating",
    "Checkin Rating",
    "Communication Rating",
    "Location Rating",
    "Value Rating",
    "Latitude",
    "Longitude"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# =====================================
# Open Report
# =====================================

report = open("reports/statistical_report.txt", "w", encoding="utf-8")

report.write("=====================================\n")
report.write("STATISTICAL ANALYSIS REPORT\n")
report.write("=====================================\n\n")

# =====================================
# Pearson Correlation
# =====================================

report.write("PEARSON CORRELATION\n")
report.write("---------------------------------\n\n")

pearson_features = [
    "Accomodates",
    "Bathrooms",
    "Bedrooms",
    "Beds",
    "Guests Included",
    "Min Nights",
    "Reviews",
    "Overall Rating",
    "Accuracy Rating",
    "Cleanliness Rating",
    "Checkin Rating",
    "Communication Rating",
    "Location Rating",
    "Value Rating"
]

for col in pearson_features:

    temp = df[["Price", col]].dropna()

    r, p = pearsonr(temp["Price"], temp[col])

    report.write(f"{col}\n")
    report.write(f"Correlation = {r:.4f}\n")
    report.write(f"P-value = {p:.6f}\n")
    report.write("---------------------------------\n")

# =====================================
# ANOVA
# =====================================

report.write("\n\n")
report.write("ANOVA TESTS\n")
report.write("---------------------------------\n\n")

categorical_features = [
    "Room Type",
    "Property Type",
    "Is Superhost",
    "Instant Bookable",
    "Neighborhood Group"
]

for feature in categorical_features:

    try:

        formula = f'Q("Price") ~ C(Q("{feature}"))'

        model = ols(formula, data=df).fit()

        anova = sm.stats.anova_lm(model, typ=2)

        report.write(f"\n{feature}\n")
        report.write(str(anova))
        report.write("\n")
        report.write("---------------------------------\n")

    except Exception as e:

        report.write(f"{feature} : ERROR\n")
        report.write(str(e))
        report.write("\n")

# =====================================
# OLS Regression
# =====================================

report.write("\n\n")
report.write("MULTIPLE LINEAR REGRESSION (OLS)\n")
report.write("---------------------------------\n\n")

ols_features = [
    "Accomodates",
    "Bathrooms",
    "Bedrooms",
    "Beds",
    "Guests Included",
    "Min Nights",
    "Reviews",
    "Overall Rating",
    "Accuracy Rating",
    "Cleanliness Rating",
    "Checkin Rating",
    "Communication Rating",
    "Location Rating",
    "Value Rating"
]

df_model = df[["Price"] + ols_features].dropna()

X = df_model.drop(columns="Price")
y = df_model["Price"]

X = sm.add_constant(X)

model = sm.OLS(y, X).fit()

report.write(model.summary().as_text())

# =====================================
# Actual vs Predicted
# =====================================

pred = model.predict(X)

plt.figure(figsize=(7,6))

plt.scatter(y, pred, alpha=0.4)

plt.plot(
    [y.min(), y.max()],
    [y.min(), y.max()],
    color="red"
)

plt.xlabel("Actual Price")
plt.ylabel("Predicted Price")
plt.title("Actual vs Predicted")

plt.tight_layout()

plt.savefig("reports/figures/actual_vs_predicted.png")

plt.close()

# =====================================
# Residual Plot
# =====================================

residuals = y - pred

plt.figure(figsize=(7,6))

sns.scatterplot(
    x=pred,
    y=residuals
)

plt.axhline(0, color="red")

plt.xlabel("Predicted Price")

plt.ylabel("Residuals")

plt.title("Residual Plot")

plt.tight_layout()

plt.savefig("reports/figures/residual_plot.png")

plt.close()

# =====================================
# Variance Inflation Factor (VIF)
# =====================================

report.write("\n\n")
report.write("VARIANCE INFLATION FACTOR (VIF)\n")
report.write("---------------------------------\n\n")

# استخدم نفس المتغيرات المستقلة المستخدمة في OLS
X_vif = df_model.drop(columns=["Price"]).copy()

# حذف أي صفوف تحتوي على قيم مفقودة
X_vif = X_vif.dropna()

# حساب VIF لكل متغير
vif_results = pd.DataFrame()
vif_results["Variable"] = X_vif.columns
vif_results["VIF"] = [
    variance_inflation_factor(X_vif.values, i)
    for i in range(X_vif.shape[1])
]

# ترتيب النتائج من الأكبر إلى الأصغر
vif_results = vif_results.sort_values(by="VIF", ascending=False)

# حفظ النتائج في التقرير
report.write(vif_results.to_string(index=False))
report.write("\n\n")

print("\nVIF Analysis Completed")
print(vif_results)

# =====================================
# Finish
# =====================================

report.close()

print("=========================================")
print("STATISTICAL ANALYSIS COMPLETED")
print("=========================================")
print("Report:")
print("reports/statistical_report.txt")
print()
print("Figures:")
print("reports/figures/actual_vs_predicted.png")
print("reports/figures/residual_plot.png")
print("=========================================")