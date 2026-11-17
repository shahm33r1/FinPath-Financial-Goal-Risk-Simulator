#FinPath tests run with: python -m unittest discover
import unittest
import numpy as np

from finance import (calculateFutureValue, calculateAnnuityValue, calculateSavings,
                     calculateRequiredContribution, calculateInflation, calculateRealReturn,
                     calculateArithmeticReturn, calculateGeometricReturn, calculateGrowthPath,
                     calculateGoal, checkInputs)
from simulation import runSimulation, summarizeResults
from strategies import calculatePortfolioReturn, calculateRisk, compareStrategies


def sampleInputs():
    return {"currentSavings": 10000, "monthlyContribution": 500, "goalAmount": 100000,
            "annualReturn": 0.07, "inflationRate": 0.03, "years": 10}


class TestFinance(unittest.TestCase):
    def testFutureValue(self):
        # 1000 at 12% compounded monthly for 1 year = 1000 * 1.01^12
        self.assertAlmostEqual(calculateFutureValue(1000, 0.12, 1), 1126.825030, places=5)

    def testAnnuityValue(self):
        self.assertAlmostEqual(calculateAnnuityValue(100, 0.12, 1), 1268.250301, places=5)

    def testZeroInterest(self):
        self.assertEqual(calculateFutureValue(5000, 0, 10), 5000)
        self.assertEqual(calculateAnnuityValue(100, 0, 5), 6000)
        self.assertEqual(calculateRequiredContribution(0, 12000, 0, 10), 100)

    def testZeroContribution(self):
        self.assertAlmostEqual(calculateSavings(1000, 0, 0.12, 1), calculateFutureValue(1000, 0.12, 1))

    def testRequiredContributionReachesGoal(self):
        payment = calculateRequiredContribution(10000, 100000, 0.07, 10)
        self.assertAlmostEqual(calculateSavings(10000, payment, 0.07, 10), 100000, places=6)

    def testRequiredContributionWhenGoalAlreadyMet(self):
        self.assertEqual(calculateRequiredContribution(200000, 100000, 0.05, 10), 0)

    def testInflation(self):
        self.assertAlmostEqual(calculateInflation(1000, 0.03, 10), 744.093915, places=5)
        self.assertAlmostEqual(calculateRealReturn(0.07, 0.03), 0.0388349515, places=8)

    def testArithmeticVsGeometric(self):
        # +50% then -50% averages 0% but actually loses money
        self.assertAlmostEqual(calculateArithmeticReturn([0.5, -0.5]), 0.0)
        self.assertAlmostEqual(calculateGeometricReturn([0.5, -0.5]), np.sqrt(0.75) - 1)

    def testGrowthPathMatchesFormula(self):
        balances, contributions = calculateGrowthPath(10000, 500, 0.07, 10)
        self.assertEqual(len(balances), 11)
        self.assertAlmostEqual(balances[-1], calculateSavings(10000, 500, 0.07, 10), places=6)
        self.assertEqual(contributions[-1], 70000)

    def testCalculateGoal(self):
        results = calculateGoal(sampleInputs())
        self.assertEqual(results["totalContributed"], 70000)
        self.assertAlmostEqual(results["interestEarned"], results["futureValue"] - 70000)
        self.assertEqual(results["amountRemaining"], 0)
        self.assertTrue(results["goalReached"])

    def testInvalidInputs(self):
        badValues = [("currentSavings", -1), ("monthlyContribution", -50), ("goalAmount", 0),
                     ("years", 0), ("years", 100), ("annualReturn", 2), ("inflationRate", 0.9)]
        for key, value in badValues:
            inputs = sampleInputs()
            inputs[key] = value
            with self.assertRaises(ValueError):
                checkInputs(inputs)


class TestSimulation(unittest.TestCase):
    def testReproducible(self):
        first = runSimulation(10000, 500, 0.07, 0.15, 10, 500, seed=42)["balances"]
        second = runSimulation(10000, 500, 0.07, 0.15, 10, 500, seed=42)["balances"]
        self.assertTrue(np.array_equal(first, second))

    def testZeroVolatilityMatchesFormula(self):
        simResults = runSimulation(10000, 500, 0.07, 0, 10, 50, seed=1)
        expected = calculateSavings(10000, 500, 0.07, 10)
        self.assertTrue(np.allclose(simResults["balances"][:, -1], expected))

    def testSummary(self):
        simResults = runSimulation(10000, 500, 0.07, 0.15, 10, 1000, seed=7)
        summary = summarizeResults(simResults, 100000)
        self.assertEqual(simResults["balances"].shape, (1000, 121))
        self.assertTrue(0 <= summary["probability"] <= 1)
        self.assertLess(summary["percentile10"], summary["median"])
        self.assertLess(summary["median"], summary["percentile90"])
        self.assertLess(summary["geometricReturn"], summary["arithmeticReturn"])

    def testInvalidSimulation(self):
        with self.assertRaises(ValueError):
            runSimulation(1000, 100, 0.07, -0.1, 5)


class TestStrategies(unittest.TestCase):
    def testPortfolioReturn(self):
        self.assertAlmostEqual(calculatePortfolioReturn(0.6, 0.08, 0.04), 0.064)

    def testPortfolioVariance(self):
        risk = calculateRisk(0.6, 0.18, 0.06, 0.2)
        self.assertAlmostEqual(risk["covariance"], 0.00216)
        self.assertAlmostEqual(risk["variance"], 0.0132768)
        self.assertAlmostEqual(risk["stdDev"], np.sqrt(0.0132768))

    def testDiversification(self):
        # Perfect correlation gives no benefit; lower correlation lowers risk
        self.assertAlmostEqual(calculateRisk(0.5, 0.2, 0.1, 1)["stdDev"], 0.15)
        self.assertLess(calculateRisk(0.5, 0.2, 0.1, 0)["stdDev"], 0.15)
        self.assertAlmostEqual(calculateRisk(0.5, 0.2, 0.2, -1)["stdDev"], 0)

    def testInvalidPortfolio(self):
        with self.assertRaises(ValueError):
            calculateRisk(0.5, 0.2, 0.1, 1.5)
        with self.assertRaises(ValueError):
            calculateRisk(1.2, 0.2, 0.1, 0.3)

    def testCompareStrategies(self):
        settings = {"cashRate": 0.04, "annualVolatility": 0.15, "asset2Return": 0.04,
                    "asset2Volatility": 0.06, "riskyWeight": 0.6, "correlation": 0.2, "numSimulations": 500}
        results, portfolioRisk = compareStrategies(sampleInputs(), settings, seed=3)
        self.assertEqual([r["name"] for r in results], ["Cash Savings", "Risky Investment", "Diversified Portfolio"])
        cash, risky, diversified = results
        self.assertAlmostEqual(cash["median"], cash["projectedBalance"])
        self.assertAlmostEqual(diversified["expectedReturn"], 0.058)
        self.assertLess(diversified["volatility"], risky["volatility"])


if __name__ == "__main__":
    unittest.main()
