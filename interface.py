#FinPath Tkinter interface. Reads the inputs, calls the calculation
#modules, and shows the numbers and charts. No financial math happens here.
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from finance import checkInputs, calculateGoal, calculateGrowthPath
from simulation import runSimulation, summarizeResults
from strategies import compareStrategies
from visualizations import createGrowthGraph, createHistogram, createComparisonGraph

#(key, label, default value, type) "percent" values are divided by 100
inputSections = {
    "Savings Plan": [
        ("currentSavings", "Current savings ($)", "10000", "money"),
        ("monthlyContribution", "Monthly contribution ($)", "500", "money"),
        ("goalAmount", "Goal amount ($)", "100000", "money"),
        ("annualReturn", "Expected annual return (%)", "7", "percent"),
        ("inflationRate", "Annual inflation rate (%)", "3", "percent"),
        ("years", "Number of years", "10", "whole"),
    ],
    "Risk Assumptions": [
        ("annualVolatility", "Annual volatility (%)", "15", "percent"),
        ("numSimulations", "Number of simulations", "1000", "whole"),
    ],
    "Strategy Comparison": [
        ("cashRate", "Cash interest rate (%)", "4", "percent"),
        ("asset2Return", "Second asset return (%)", "4", "percent"),
        ("asset2Volatility", "Second asset volatility (%)", "6", "percent"),
        ("riskyWeight", "Weight in risky asset (%)", "60", "percent"),
        ("correlation", "Correlation (-1 to 1)", "0.2", "number"),
    ],
}

entries = {}
tabs = {}
notebook = None
monoFont = ("Courier", 12)


def getInputs():
    #Reads every entry box and converts it to the right type
    inputs = {}
    for fields in inputSections.values():
        for key, label, default, valueType in fields:
            text = entries[key].get().strip().replace(",", "").replace("$", "").replace("%", "")
            try:
                value = float(text)
            except ValueError:
                raise ValueError(f"Please enter a number for \"{label}\".")
            if valueType == "whole":
                if value != int(value):
                    raise ValueError(f"\"{label}\" must be a whole number.")
                value = int(value)
            elif valueType == "percent":
                value = value / 100
            inputs[key] = value

    if not 100 <= inputs["numSimulations"] <= 10000:
        raise ValueError("Number of simulations should be between 100 and 10,000.")
    if inputs["annualVolatility"] > 1 or inputs["asset2Volatility"] > 1:
        raise ValueError("Volatility should be 100% or less.")
    if not -0.5 < inputs["cashRate"] < 1 or not -0.5 < inputs["asset2Return"] < 1:
        raise ValueError("Returns should be between -50% and 100%.")
    return inputs


def showResults(tabName, lines):
    textBox = tabs[tabName]["text"]
    textBox.config(state="normal")
    textBox.delete("1.0", tk.END)
    textBox.insert(tk.END, "\n".join(lines))
    textBox.config(state="disabled")


def money(value):
    return f"${value:,.2f}"


def onCalculateGoal():
    try:
        inputs = getInputs()
        results = calculateGoal(inputs)
    except ValueError as error:
        messagebox.showerror("Invalid input", str(error))
        return

    status = "Goal reached!" if results["goalReached"] else f"Short by {money(results['amountRemaining'])}"
    showResults("goal", [
        f"Deterministic projection: fixed {inputs['annualReturn']:.2%} annual return, compounded monthly",
        "",
        f"Future value of savings:          {money(results['futureValue']):>16}   ({status})",
        f"Total amount contributed:         {money(results['totalContributed']):>16}",
        f"Investment growth earned:         {money(results['interestEarned']):>16}",
        f"Amount remaining to reach goal:   {money(results['amountRemaining']):>16}",
        f"Required monthly contribution:    {money(results['requiredMonthly']):>16}",
        f"Inflation-adjusted future value:  {money(results['realFutureValue']):>16}   (today's dollars)",
        f"Real annual return (Fisher):      {results['realReturn']:>16.2%}",
    ])
    balances, contributions = calculateGrowthPath(inputs["currentSavings"], inputs["monthlyContribution"],
                                                  inputs["annualReturn"], inputs["years"])
    createGrowthGraph(tabs["goal"]["figure"], balances, contributions, inputs["goalAmount"])
    tabs["goal"]["canvas"].draw()
    notebook.select(0)


def onRunSimulation():
    try:
        inputs = getInputs()
        checkInputs(inputs)
        simResults = runSimulation(inputs["currentSavings"], inputs["monthlyContribution"],
                                   inputs["annualReturn"], inputs["annualVolatility"],
                                   inputs["years"], inputs["numSimulations"])
    except ValueError as error:
        messagebox.showerror("Invalid input", str(error))
        return

    summary = summarizeResults(simResults, inputs["goalAmount"])
    showResults("simulation", [
        f"Monte Carlo: {inputs['numSimulations']:,} simulated paths, {inputs['annualReturn']:.2%} expected "
        f"return, {inputs['annualVolatility']:.2%} volatility",
        "",
        f"Probability of reaching goal:   {summary['probability']:>14.1%}",
        f"Average ending balance:         {money(summary['average']):>14}",
        f"Median ending balance:          {money(summary['median']):>14}",
        f"10th percentile (bad case):     {money(summary['percentile10']):>14}",
        f"90th percentile (good case):    {money(summary['percentile90']):>14}",
        f"Std. dev. of ending balances:   {money(summary['stdDev']):>14}",
        f"Avg arithmetic annual return:   {summary['arithmeticReturn']:>14.2%}",
        f"Avg geometric annual return:    {summary['geometricReturn']:>14.2%}   (volatility drag)",
        "",
        "These are hypothetical outcomes based on your assumptions, not predictions.",
    ])
    createHistogram(tabs["simulation"]["figure"], simResults["balances"][:, -1], inputs["goalAmount"], summary)
    tabs["simulation"]["canvas"].draw()
    notebook.select(1)


def onCompareStrategies():
    try:
        inputs = getInputs()
        checkInputs(inputs)
        # inputs also holds the strategy settings, so it's passed for both
        results, portfolioRisk = compareStrategies(inputs, inputs)
    except ValueError as error:
        messagebox.showerror("Invalid input", str(error))
        return

    lines = [
        f"{'Strategy':<22}{'Return':>8}{'Risk':>8}{'Projected*':>14}{'Median':>14}"
        f"{'10th pct':>14}{'Worst':>14}{'P(goal)':>9}",
        "-" * 103,
    ]
    for result in results:
        lines.append(f"{result['name']:<22}{result['expectedReturn']:>8.2%}{result['volatility']:>8.2%}"
                     f"{money(result['projectedBalance']):>14}{money(result['median']):>14}"
                     f"{money(result['percentile10']):>14}{money(result['worst']):>14}"
                     f"{result['probability']:>9.1%}")
    lines += [
        "",
        f"Diversified portfolio: {inputs['riskyWeight']:.0%} risky asset / {1 - inputs['riskyWeight']:.0%} "
        f"second asset, covariance = {portfolioRisk['covariance']:.5f}, variance = {portfolioRisk['variance']:.5f}",
        "*Projected = deterministic balance at the expected return. Median, 10th pct, worst case and",
        " P(goal) come from the Monte Carlo simulation (same random draws for each strategy).",
    ]
    showResults("compare", lines)
    createComparisonGraph(tabs["compare"]["figure"], results, inputs["goalAmount"])
    tabs["compare"]["canvas"].draw()
    notebook.select(2)


def createTab(name, title):
    frame = ttk.Frame(notebook, padding=8)
    notebook.add(frame, text=title)
    textBox = tk.Text(frame, height=12, font=monoFont, relief="flat", background="#f4f6f7", wrap="none")
    textBox.pack(fill="x")
    textBox.config(state="disabled")
    figure = Figure(figsize=(8, 4.5), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True, pady=(8, 0))
    tabs[name] = {"text": textBox, "figure": figure, "canvas": canvas}


def startApp():
    global notebook
    root = tk.Tk()
    root.title("FinPath - Financial Goal & Risk Simulator")
    root.geometry("1300x820")

    leftPanel = ttk.Frame(root, padding=10)
    leftPanel.pack(side="left", fill="y")
    ttk.Label(leftPanel, text="FinPath", font=("Helvetica", 20, "bold")).pack(anchor="w")
    ttk.Label(leftPanel, text="Financial Goal & Risk Simulator").pack(anchor="w", pady=(0, 8))

    for sectionName, fields in inputSections.items():
        section = ttk.LabelFrame(leftPanel, text=sectionName, padding=8)
        section.pack(fill="x", pady=4)
        for row, (key, label, default, valueType) in enumerate(fields):
            ttk.Label(section, text=label).grid(row=row, column=0, sticky="w", pady=2)
            entry = ttk.Entry(section, width=12, justify="right")
            entry.insert(0, default)
            entry.grid(row=row, column=1, padx=(8, 0), pady=2)
            entries[key] = entry

    ttk.Button(leftPanel, text="Calculate Goal", command=onCalculateGoal).pack(fill="x", pady=(10, 3))
    ttk.Button(leftPanel, text="Run Simulation", command=onRunSimulation).pack(fill="x", pady=3)
    ttk.Button(leftPanel, text="Compare Strategies", command=onCompareStrategies).pack(fill="x", pady=3)
    ttk.Label(leftPanel, text="Results are based on hypothetical assumptions\nand are not financial advice.",
              foreground="gray").pack(anchor="w", pady=(10, 0))

    notebook = ttk.Notebook(root)
    notebook.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
    createTab("goal", "Goal Calculator")
    createTab("simulation", "Monte Carlo Simulation")
    createTab("compare", "Strategy Comparison")

    onCalculateGoal()  #show the default example right away
    root.mainloop()
