"""Visualizations for annual training frequency
"""

from src.utils.config import settings  # type: ignore
import numpy as np
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt
import seaborn as sns  # type: ignore

# Generate synthetic workout data for 4 years (208 weeks)
np.random.seed(42)
dates = pd.date_range(start="2019-01-01", end="2023-12-31", freq="W")
workouts = np.random.poisson(lam=3, size=len(dates))  # Simulate weekly workout counts

data = pd.DataFrame({"Date": dates, "Workouts": workouts})
data["Year"] = data["Date"].dt.year
data["Month"] = data["Date"].dt.month
data["Week"] = data["Date"].dt.isocalendar().week

# Rolling average for smoothing trends
data["Rolling_Avg"] = data["Workouts"].rolling(window=4).mean()

# Aggregate data by year and month for heatmaps and bar charts
monthly_data = data.groupby(["Year", "Month"]).Workouts.sum().reset_index()
yearly_data = data.groupby("Year").Workouts.sum().reset_index()


# Helper functions
def add_labels(ax, x, y):
    for i in range(len(x)):
        ax.text(i, y[i] + 0.2, str(y[i]), ha="center", va="bottom", fontsize=8)


# 1. Time Series Line Plot
path = f"{settings['IMG_PATH']}simulations/time-series-line-plot.png"
plt.figure(figsize=(14, 5))
plt.plot(data["Date"], data["Workouts"], label="Weekly Workouts", alpha=0.5)
plt.plot(
    data["Date"],
    data["Rolling_Avg"],
    label="4-Week Rolling Average",
    color="red",
    linewidth=2,
)
plt.title("Weekly Workouts Over 4 Years")
plt.xlabel("Date")
plt.ylabel("Number of Workouts")
plt.legend()
plt.grid(True)
# plt.show()
# plt.clf()
# plt.close()
plt.savefig(path)

# 2. Calendar Heatmap
path = f"{settings['IMG_PATH']}simulations/calendar-heatmap.png"
plt.figure(figsize=(14, 5))
# pivot = monthly_data.pivot("Year", "Month", "Workouts")
pivot = monthly_data.pivot(index="Year", columns="Month", values="Workouts")
sns.heatmap(
    pivot, annot=True, fmt="d", cmap="coolwarm", cbar_kws={"label": "Total Workouts"}
)
plt.title("Monthly Workout Heatmap")
plt.xlabel("Month")
plt.ylabel("Year")
# plt.show()
plt.savefig(path)

# 3. Bar Chart
path = f"{settings['IMG_PATH']}simulations/bar-chart.png"
plt.figure(figsize=(10, 5))
sns.barplot(x="Year", y="Workouts", data=yearly_data, hue="Year", legend=False)  # palette="viridis")
plt.title("Yearly Workout Totals")
plt.xlabel("Year")
plt.ylabel("Total Workouts")
add_labels(plt.gca(), yearly_data["Year"], yearly_data["Workouts"])
# plt.show()
plt.savefig(path)

# 4. Box Plot
path = f"{settings['IMG_PATH']}simulations/box-plot.png"
plt.figure(figsize=(10, 5))
sns.boxplot(x="Year", y="Workouts", data=data)
plt.title("Distribution of Weekly Workouts by Year")
plt.xlabel("Year")
plt.ylabel("Number of Workouts")
plt.grid(True, axis="y", linestyle="--", alpha=0.6)
# plt.show()
plt.savefig(path)

# 5. Cumulative Sum Plot
path = f"{settings['IMG_PATH']}simulations/cumulative-sum-plot.png"
data["Cumulative_Workouts"] = data["Workouts"].cumsum()
plt.figure(figsize=(14, 5))
plt.plot(
    data["Date"],
    data["Cumulative_Workouts"],
    label="Cumulative Workouts",
    color="green",
)
plt.title("Cumulative Workouts Over 4 Years")
plt.xlabel("Date")
plt.ylabel("Cumulative Workouts")
plt.legend()
plt.grid(True)
# plt.show()
plt.savefig(path)

# 6. Stacked Area Chart
path = f"{settings['IMG_PATH']}simulations/stacked-area-chart.png"
types = ["Strength", "Cardio", "Flexibility"]
stacked_data = pd.DataFrame(
    {
        "Date": data["Date"],
        "Strength": np.random.poisson(1, size=len(data)),
        "Cardio": np.random.poisson(1, size=len(data)),
        "Flexibility": np.random.poisson(1, size=len(data)),
    }
)
stacked_data["Total"] = stacked_data[types].sum(axis=1)
plt.figure(figsize=(14, 5))
plt.stackplot(
    stacked_data["Date"],
    stacked_data["Strength"],
    stacked_data["Cardio"],
    stacked_data["Flexibility"],
    labels=types,
    colors=["#FF9999", "#99FF99", "#9999FF"],
)
plt.title("Weekly Workouts by Type")
plt.xlabel("Date")
plt.ylabel("Workouts")
plt.legend(loc="upper left")
# plt.show()
plt.savefig(path)

# 7. Seasonality Analysis (Polar Plot)
path = f"{settings['IMG_PATH']}simulations/seasonality-analysis-polar-plot.png"
monthly_avg = data.groupby("Month").Workouts.mean()
theta = np.linspace(0, 2 * np.pi, len(monthly_avg))
plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)
ax.plot(theta, monthly_avg, marker="o", label="Average Workouts")
ax.fill(theta, monthly_avg, alpha=0.3)
ax.set_xticks(theta)

# ax.set_xticklabels(range(1, 13))
ax.set_xticklabels(map(str, range(1, 13)))

plt.title("Seasonality in Workouts (Monthly Averages)")
plt.legend()
# plt.show()
plt.savefig(path)

# 8. Bubble Chart
path = f"{settings['IMG_PATH']}simulations/bubble-chart.png"
bubble_data = data.copy()
bubble_data["Intensity"] = np.random.uniform(1, 3, size=len(data))
plt.figure(figsize=(14, 5))
plt.scatter(
    bubble_data["Date"],
    bubble_data["Workouts"],
    s=bubble_data["Intensity"] * 50,
    alpha=0.6,
    c=bubble_data["Workouts"],
    cmap="viridis",
)
plt.title("Weekly Workouts and Intensity")
plt.xlabel("Date")
plt.ylabel("Number of Workouts")
plt.colorbar(label="Workouts")
# plt.show()
plt.savefig(path)
