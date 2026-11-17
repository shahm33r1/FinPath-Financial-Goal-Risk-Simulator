# FinPath: Financial Goal & Risk Simulator

FinPath is a Python application designed to help users set savings goals, compare investment strategies, and understand financial risk. The application uses financial calculations, Monte Carlo simulations, and visualizations to demonstrate how different saving habits, investment returns, and market conditions can affect financial goals.

This project was developed for my Programming in FinTech course to apply the financial concepts and Python programming techniques learned throughout the semester.

## How to Run

1. Open the project in PyCharm.

2. Open the Terminal at the bottom of PyCharm.

3. Navigate to the project folder if you are not already in it.

4. Activate the project's Python environment:

```bash
source .venv/bin/activate
```

5. Start the application:

```bash
python main.py
```

6. Running the tests (optional):

```bash
python -m unittest discover
```

7. When you're done:

Close the FinPath application window. To exit the Python environment, enter:

```bash
deactivate
```

## Project Development Progress

### September 17, 2026: 25% Completed

The first implementation focused on developing the foundation of the application and its financial calculations. This included creating functions for compound interest, future value, monthly savings contributions, inflation adjustments, and savings projections. These calculations provided the foundation for the more advanced features introduced in later implementations.

### October 17, 2026: 50% Completed

The second implementation focused on incorporating financial risk analysis and investment simulations. Monte Carlo simulations were developed to model different investment outcomes based on expected returns and volatility. This also included calculating the probability of reaching financial goals and comparing potential outcomes under different market conditions.

### November 17, 2026: 75% Completed

The third implementation focused on combining the financial calculations and simulations into a functional application. This included developing the graphical user interface, connecting the different components, and implementing visualizations to display financial results. Users can now enter their financial information, run simulations, and compare different financial strategies.

### December 2026: 100% Completion (Planned)

The final implementation will focus on improving the application's functionality, reliability, and overall presentation. This will include adding the ability to save and load financial scenarios, expanding automated testing, improving visualizations, and making final adjustments to the user interface. The goal is to complete a fully functional application that demonstrates the financial and programming concepts covered throughout the semester.

## Technologies Used

Python, NumPy, Matplotlib, Tkinter, JSON, and unittest.

## Project Purpose

The purpose of FinPath is to provide users with a practical way to evaluate financial decisions and understand how different factors can affect their savings and investments. By combining financial calculations, simulations, and visualizations, the application demonstrates how Python can be used to analyze financial risk and support better financial planning.
