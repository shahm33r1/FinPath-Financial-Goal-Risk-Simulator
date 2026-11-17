#All rates are decimals here (0.07 means 7%). Interest compounds monthly.
import numpy as np


def checkInputs(inputs):
    #Raises ValueError with a readable message if a value doesn't make sense
    if inputs["currentSavings"] < 0:
        raise ValueError("Current savings cannot be negative.")
    if inputs["monthlyContribution"] < 0:
        raise ValueError("Monthly contribution cannot be negative.")
    if inputs["goalAmount"] <= 0:
        raise ValueError("Goal amount must be greater than zero.")
    if not -0.5 < inputs["annualReturn"] < 1:
        raise ValueError("Expected annual return should be between -50% and 100%.")
    if not -0.1 < inputs["inflationRate"] < 0.5:
        raise ValueError("Inflation rate should be between -10% and 50%.")
    if not 1 <= inputs["years"] <= 60:
        raise ValueError("Number of years must be between 1 and 60.")


def calculateFutureValue(presentValue, annualRate, years):
    #Lump sum growing with monthly compounding: PV * (1 + r/12)^(12n)
    monthlyRate = annualRate / 12
    return presentValue * (1 + monthlyRate) ** (years * 12)


def calculateAnnuityValue(monthlyPayment, annualRate, years):
    #Future value of an ordinary annuity (deposits at the end of each month)
    monthlyRate = annualRate / 12
    months = years * 12
    if monthlyRate == 0:
        return monthlyPayment * months
    return monthlyPayment * ((1 + monthlyRate) ** months - 1) / monthlyRate


def calculateSavings(currentSavings, monthlyContribution, annualRate, years):
    return (calculateFutureValue(currentSavings, annualRate, years)
            + calculateAnnuityValue(monthlyContribution, annualRate, years))


def calculateRequiredContribution(currentSavings, goalAmount, annualRate, years):
    #Solve the annuity formula for the payment that closes the gap to the goal
    monthlyRate = annualRate / 12
    months = years * 12
    gap = goalAmount - calculateFutureValue(currentSavings, annualRate, years)
    if gap <= 0:
        return 0.0
    if monthlyRate == 0:
        return gap / months
    return gap * monthlyRate / ((1 + monthlyRate) ** months - 1)


def calculateInflation(amount, inflationRate, years):
    #What a future amount is worth in today's dollars
    return amount / (1 + inflationRate) ** years


def calculateRealReturn(nominalReturn, inflationRate):
    #Fisher equation: (1 + nominal) / (1 + inflation) - 1
    return (1 + nominalReturn) / (1 + inflationRate) - 1


def calculateArithmeticReturn(returns):
    return float(np.mean(returns))


def calculateGeometricReturn(returns):
    #Average compound return per period
    returns = np.array(returns)
    return float(np.prod(1 + returns) ** (1 / len(returns)) - 1)


def calculateGrowthPath(currentSavings, monthlyContribution, annualRate, years):
    #Balance and total money put in at the end of each year (year 0 included)
    monthlyRate = annualRate / 12
    balance = currentSavings
    contributed = currentSavings
    balances = [balance]
    contributions = [contributed]
    for month in range(1, years * 12 + 1):
        balance = balance * (1 + monthlyRate) + monthlyContribution
        contributed += monthlyContribution
        if month % 12 == 0:
            balances.append(balance)
            contributions.append(contributed)
    return balances, contributions


def calculateGoal(inputs):
    #Runs every Feature 1 calculation and returns the results in one dictionary
    checkInputs(inputs)
    currentSavings = inputs["currentSavings"]
    monthlyContribution = inputs["monthlyContribution"]
    annualReturn = inputs["annualReturn"]
    years = inputs["years"]

    futureValue = calculateSavings(currentSavings, monthlyContribution, annualReturn, years)
    totalContributed = currentSavings + monthlyContribution * 12 * years
    return {
        "futureValue": futureValue,
        "totalContributed": totalContributed,
        "interestEarned": futureValue - totalContributed,
        "amountRemaining": max(inputs["goalAmount"] - futureValue, 0),
        "requiredMonthly": calculateRequiredContribution(
            currentSavings, inputs["goalAmount"], annualReturn, years),
        "realFutureValue": calculateInflation(futureValue, inputs["inflationRate"], years),
        "realReturn": calculateRealReturn(annualReturn, inputs["inflationRate"]),
        "goalReached": futureValue >= inputs["goalAmount"],
    }
