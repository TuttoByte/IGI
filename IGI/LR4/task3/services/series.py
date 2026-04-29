import sys
import math
import statistics
from utils import menu

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


import numpy as np
import math




class Taylor:
    """
    Compute Taylor series for e^x and basic statistics for its terms.
    """

    def __init__(self):

        self.seriesElements = []
        pass

    def TaylorExp(self, x, eps :float) -> tuple:


        """
        Computes Taylor series for e^x until precision eps is reached.

        Args:
            x (float): input value
            eps (float): required precision
        
        Returns:
            tuple: (n, tseries, etalon) - iterations, approximation, exact value
        """

        etalon = math.exp(x)
        tseries = 0

        for i in range(500):

            element = math.pow(x, i) / math.factorial(i)
            
            #add element
            self.seriesElements.append(element)

            tseries += element
            if (math.fabs(tseries - etalon) <= eps):
                return i, tseries, etalon


        return -1, tseries, etalon


    def CalculateArifmetic(self) -> float:
        """Return arithmetic mean of series elements."""
        return sum(self.seriesElements) / len(self.seriesElements)
    
    def CalculateMedian(self) -> float:
        """Return median of series elements."""
        return statistics.median(self.seriesElements)
    
    def CalculateMode(self) -> float:
        """Return mode of series elements."""
        return statistics.mode(self.seriesElements)
    
    def CalcualDisperison(self) -> float:
        """Return sample variance of series elements."""
        return statistics.variance(self.seriesElements)
    
    def CalculatePST(self) -> float:
        """Return population standard deviation of series elements."""
        return statistics.pstdev(self.seriesElements)
    
    def Plot(selt) -> None:
        """Plot partial sums and the exact exponential function."""
        dat= np.array(selt.seriesElements)
        

        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot(dat)
        ax1.set_title("График чвстичных сумм")
        

        x = np.linspace(0, 10, 100) # 100 points from -10 to 10
        y = np.exp(x)
        ax2.plot(x, y)
        ax2.set_title("График e^x")

        plt.tight_layout()
        plt.show()

