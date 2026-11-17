#FinPath Monte Carlo simulation of savings
import numpy as np
from finance import calculateArithmeticReturn, calculateGeometricReturn


def runSimulation(currentSavings, monthlyContribution, annualReturn, annualVolatility,
                  years, numSimulations=1000, seed=None):
    if annualVolatility < 0:
        raise ValueError("Volatility cannot be negative.")
    if numSimulations < 1:
        raise ValueError("Number of simulations must be at least 1.")

    months = years * 12
    monthlyMean = annualReturn / 12
    monthlyStd = annualVolatility / np.sqrt(12)

    rng = np.random.default_rng(seed)
    monthlyReturns = rng.normal(monthlyMean, monthlyStd, size=(numSimulations, months))
    monthlyReturns = np.maximum(monthlyReturns, -1)  # can't lose more than 100%

    #balances[i, m] = balance of simulation i after month m
    balances = np.zeros((numSimulations, months + 1))
    balances[:, 0] = currentSavings
    for month in range(1, months + 1):
        balances[:, month] = balances[:, month - 1] * (1 + monthlyReturns[:, month - 1]) + monthlyContribution

    return {"balances": balances, "returns": monthlyReturns}


def summarizeResults(simResults, goalAmount):
    endingBalances = simResults["balances"][:, -1]
    returns = simResults["returns"]

    #Average annual return of each simulated path, arithmetic vs geometric
    arithmeticAnnual = np.mean([calculateArithmeticReturn(path) for path in returns]) * 12
    geometricMonthly = np.mean([calculateGeometricReturn(path) for path in returns])

    return {
        "probability": float(np.mean(endingBalances >= goalAmount)),
        "average": float(np.mean(endingBalances)),
        "median": float(np.median(endingBalances)),
        "stdDev": float(np.std(endingBalances)),
        "percentile10": float(np.percentile(endingBalances, 10)),
        "percentile90": float(np.percentile(endingBalances, 90)),
        "worst": float(np.min(endingBalances)),
        "arithmeticReturn": float(arithmeticAnnual),
        "geometricReturn": float((1 + geometricMonthly) ** 12 - 1),
    }
