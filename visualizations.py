# FinPath Matplotlib charts. Each function draws onto a Figure that the
# interface passes in, so the charts don't depend on Tkinter.
import numpy as np

strategyColors = ["#7f8c8d", "#c0392b", "#2471a3"]


def formatDollars(value, position=None):
    return f"${value:,.0f}"


def createGrowthGraph(figure, balances, contributions, goalAmount):
    figure.clear()
    ax = figure.add_subplot(111)
    years = range(len(balances))
    ax.plot(years, balances, marker="o", color="#2471a3", label="Projected balance")
    ax.plot(years, contributions, linestyle="--", color="#7f8c8d", label="Total contributed")
    ax.fill_between(years, contributions, balances, color="#2471a3", alpha=0.15, label="Investment growth")
    ax.axhline(goalAmount, color="#27ae60", linewidth=1.5, label="Goal")
    ax.set_title("Savings Growth Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Balance")
    ax.yaxis.set_major_formatter(formatDollars)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    figure.tight_layout()


def createHistogram(figure, endingBalances, goalAmount, summary):
    figure.clear()
    ax = figure.add_subplot(111)
    ax.hist(endingBalances, bins=40, color="#2471a3", alpha=0.75, edgecolor="white")
    ax.axvline(goalAmount, color="#27ae60", linewidth=2, label="Goal")
    ax.axvline(summary["median"], color="black", linestyle="--", label="Median")
    ax.axvline(summary["percentile10"], color="#c0392b", linestyle=":", label="10th percentile")
    ax.axvline(summary["percentile90"], color="#8e44ad", linestyle=":", label="90th percentile")
    ax.set_title(f"Simulated Ending Balances ({len(endingBalances):,} runs)")
    ax.set_xlabel("Ending balance")
    ax.set_ylabel("Number of simulations")
    ax.xaxis.set_major_formatter(formatDollars)
    ax.tick_params(axis="x", labelrotation=20)
    ax.grid(alpha=0.3)
    ax.legend()
    figure.tight_layout()


def createComparisonGraph(figure, strategyResults, goalAmount):
    figure.clear()
    leftAx = figure.add_subplot(121)
    rightAx = figure.add_subplot(122)

    #Left: median path with a shaded 10th-90th percentile band for each strategy
    for result, color in zip(strategyResults, strategyColors):
        balances = result["balances"]
        years = np.arange(balances.shape[1]) / 12
        low, median, high = np.percentile(balances, [10, 50, 90], axis=0)
        leftAx.plot(years, median, color=color, label=result["name"])
        leftAx.fill_between(years, low, high, color=color, alpha=0.15)
    leftAx.axhline(goalAmount, color="#27ae60", linewidth=1.5, label="Goal")
    leftAx.set_title("Median Balance (10th-90th band)")
    leftAx.set_xlabel("Year")
    leftAx.yaxis.set_major_formatter(formatDollars)
    leftAx.grid(alpha=0.3)
    leftAx.legend(fontsize=8, loc="upper left")

    #Right: chance of reaching the goal
    names = [result["name"].replace(" ", "\n", 1) for result in strategyResults]
    probabilities = [result["probability"] * 100 for result in strategyResults]
    bars = rightAx.bar(names, probabilities, color=strategyColors)
    rightAx.bar_label(bars, fmt="%.1f%%")
    rightAx.set_ylim(0, 110)
    rightAx.set_title("Probability of Reaching Goal")
    rightAx.set_ylabel("Percent of simulations")
    rightAx.tick_params(axis="x", labelsize=8)
    figure.tight_layout()