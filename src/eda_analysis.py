import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================
# Load Data
# =====================================

df = pd.read_csv("data/processed/berlin_airbnb_cleaned.csv")

# =====================================
# Create output folders
# =====================================

os.makedirs("reports", exist_ok=True)
os.makedirs("reports/figures", exist_ok=True)

# =====================================
# Numerical columns for analysis
# =====================================

numerical_cols = [
    "Price",
    "Accomodates",
    "Bathrooms",
    "Bedrooms",
    "Beds",
    "Reviews",
    "Min Nights"
]

# =====================================
# 1. Price Distribution
# =====================================

plt.figure(figsize=(8,5))
df["Price"].hist(bins=50)

plt.title("Price Distribution")
plt.xlabel("Price (€)")
plt.ylabel("Frequency")

plt.tight_layout()
plt.savefig("reports/figures/price_distribution.png")
plt.close()

# =====================================
# 2. Room Type Distribution
# =====================================

plt.figure(figsize=(8,5))

df["Room Type"].value_counts().plot(kind="bar")

plt.title("Room Type Distribution")
plt.xlabel("Room Type")
plt.ylabel("Count")

plt.tight_layout()
plt.savefig("reports/figures/room_type_distribution.png")
plt.close()

# =====================================
# 3. Average Price by Neighborhood
# =====================================

plt.figure(figsize=(12,5))

df.groupby("Neighborhood Group")["Price"].mean().sort_values().plot(kind="bar")

plt.title("Average Price by Neighborhood")
plt.xlabel("Neighborhood")
plt.ylabel("Average Price")

plt.tight_layout()
plt.savefig("reports/figures/neighborhood_price.png")
plt.close()

# =====================================
# 4. Correlation Heatmap
# =====================================

plt.figure(figsize=(10,7))

corr = df[numerical_cols].corr()

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("Correlation Heatmap")

plt.tight_layout()
plt.savefig("reports/figures/correlation_heatmap.png")
plt.close()

# =====================================
# 5. Superhost vs Price
# =====================================

plt.figure(figsize=(6,5))

df.groupby("Is Superhost")["Price"].mean().plot(kind="bar")

plt.title("Average Price by Superhost Status")
plt.xlabel("Is Superhost")
plt.ylabel("Average Price")

plt.tight_layout()
plt.savefig("reports/figures/superhost_price.png")
plt.close()

# =====================================
# 6. Boxplot (Price)
# =====================================

plt.figure(figsize=(6,5))

sns.boxplot(y=df["Price"])

plt.title("Price Boxplot")

plt.tight_layout()
plt.savefig("reports/figures/price_boxplot.png")
plt.close()

# =====================================
# 7. Scatter: Bedrooms vs Price
# =====================================

plt.figure(figsize=(7,5))

sns.scatterplot(
    data=df,
    x="Bedrooms",
    y="Price"
)

plt.title("Bedrooms vs Price")

plt.tight_layout()
plt.savefig("reports/figures/bedrooms_price.png")
plt.close()

# =====================================
# 8. Scatter: Bathrooms vs Price
# =====================================

plt.figure(figsize=(7,5))

sns.scatterplot(
    data=df,
    x="Bathrooms",
    y="Price"
)

plt.title("Bathrooms vs Price")

plt.tight_layout()
plt.savefig("reports/figures/bathrooms_price.png")
plt.close()

# =====================================
# Report
# =====================================

with open("reports/eda_report.txt", "w", encoding="utf-8") as f:

    f.write("=====================================\n")
    f.write("BERLIN AIRBNB - EDA REPORT\n")
    f.write("=====================================\n\n")

    # Dataset info
    f.write("DATASET INFORMATION\n")
    f.write("-----------------------------\n")

    f.write(f"Rows: {df.shape[0]}\n")
    f.write(f"Columns: {df.shape[1]}\n\n")

    # Column names
    f.write("COLUMN NAMES\n")
    f.write("-----------------------------\n")

    for col in df.columns:
        f.write(f"{col}\n")

    f.write("\n")

    # Missing values
    f.write("MISSING VALUES\n")
    f.write("-----------------------------\n")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        f.write("No missing values.\n")
    else:
        f.write(str(missing))

    f.write("\n\n")

    # Descriptive statistics
    f.write("DESCRIPTIVE STATISTICS\n")
    f.write("-----------------------------\n")

    f.write(str(df[numerical_cols].describe()))

    f.write("\n\n")

    # Correlation with price
    f.write("CORRELATION WITH PRICE\n")
    f.write("-----------------------------\n")

    corr_price = (
        df[numerical_cols]
        .corr()["Price"]
        .sort_values(ascending=False)
    )

    f.write(str(corr_price))

    f.write("\n\n")

    # Top Neighborhoods
    f.write("TOP NEIGHBORHOODS\n")
    f.write("-----------------------------\n")

    f.write(
        str(
            df["Neighborhood Group"]
            .value_counts()
            .head(10)
        )
    )

    f.write("\n\n")

    # Room Types
    f.write("ROOM TYPES\n")
    f.write("-----------------------------\n")

    f.write(
        str(
            df["Room Type"]
            .value_counts()
        )
    )

    f.write("\n\n")

    # Property Types
    f.write("PROPERTY TYPES\n")
    f.write("-----------------------------\n")

    f.write(
        str(
            df["Property Type"]
            .value_counts()
            .head(10)
        )
    )

print("========================================")
print("EDA COMPLETED SUCCESSFULLY")
print("========================================")
print("Report saved to:")
print("reports/eda_report.txt")
print()
print("Figures saved to:")
print("reports/figures/")
print("========================================")