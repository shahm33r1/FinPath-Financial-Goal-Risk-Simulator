#FinPath two-asset portfolio math and strategy comparison
import numpy as np
from finance import calculateSavings
from simulation import runSimulation, summarizeResults


def calculatePortfolioReturn(weight1, return1, return2):
    #Weighted expected return: w1*E(R1) + w2*E(R2)
    return weight1 * return1 + (1 - weight1) * return2


def calculateRisk(weight1, volatility1, volatility2, correlation):
    #Portfolio variance: w1^2*s1^2 + w2^2*s2^2 + 2*w1*w2*Cov(1,2)
    if not 0 <= weight1 <= 1:
        raise ValueError("Portfolio weight must be between 0% and 100%.")
    if not -1 <= correlation <= 1:
        raise ValueError("Correlation must be between -1 and 1.")
    if volatility1 < 0 or volatility2 < 0:
        raise ValueError("Volatility cannot be negative.")

    weight2 = 1 - weight1
    covariance = correlation * volatility1 * volatility2
    variance = (weight1 ** 2 * volatility1 ** 2 + weight2 ** 2 * volatility2 ** 2
                + 2 * weight1 * weight2 * covariance)
    return {"covariance": covariance, "variance": variance, "stdDev": float(np.sqrt(variance))}


def compareStrategies(inputs, settings, seed=None):
    #inputs: the savings plan from the goal calculator
    #settings: cash rate, risky asset, second asset, weight and correlation
    weight = settings["riskyWeight"]
    portfolioReturn = calculatePortfolioReturn(weight, inputs["annualReturn"], settings["asset2Return"])
    portfolioRisk = calculateRisk(weight, settings["annualVolatility"],
                                  settings["asset2Volatility"], settings["correlation"])

    strategyList = [
        ("Cash Savings", settings["cashRate"], 0.0),
        ("Risky Investment", inputs["annualReturn"], settings["annualVolatility"]),
        ("Diversified Portfolio", portfolioReturn, portfolioRisk["stdDev"]),
    ]

    #One shared seed so every strategy faces the same random "luck"
    if seed is None:
        seed = int(np.random.randint(0, 1000000))

    results = []
    for name, expectedReturn, volatility in strategyList:
        simResults = runSimulation(inputs["currentSavings"], inputs["monthlyContribution"],
                                   expectedReturn, volatility, inputs["years"],
                                   settings["numSimulations"], seed)
        summary = summarizeResults(simResults, inputs["goalAmount"])
        summary["name"] = name
        summary["expectedReturn"] = expectedReturn
        summary["volatility"] = volatility
        summary["projectedBalance"] = calculateSavings(inputs["currentSavings"], inputs["monthlyContribution"],
                                                       expectedReturn, inputs["years"])
        summary["balances"] = simResults["balances"]
        results.append(summary)
    return results, portfolioRisk
