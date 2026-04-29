import numpy as np
from typing import Tuple, Optional


class MatrixController:
    def __init__(self, n):
        self.matrix = np.random.rand(n,n)

    def Minimum(self) -> float:
        """Glemet minimum elemnt"""
        return np.min(self.matrix)
        
    def AllMinimum(self) -> list[list]:
        """Get all minimus"""
        return np.argwhere(self.matrix == self.Minimum)




class MatrixOperation:
    """Mixin class providing statistical methods."""
    
    @staticmethod
    def mean(data: np.ndarray) -> Optional[float]:
        """Calculate the mean of an array."""
        return np.mean(data) if data.size > 0 else None
    
    @staticmethod
    def median(data: np.ndarray) -> Optional[float]:
        """Calculate the median of an array."""
        return np.median(data) if data.size > 0 else None
    
    @staticmethod
    def variance(data: np.ndarray) -> Optional[float]:
        """Calculate the variance of an array."""
        return np.var(data) if data.size > 0 else None
    
    @staticmethod
    def std_dev(data: np.ndarray) -> Optional[float]:
        """Calculate the standard deviation of an array."""
        return np.std(data) if data.size > 0 else None
    

    def std_arif(data :np.ndarray) ->Optional[float]:
        """Calculate the standard deviation of an array by arifm."""
        return np.sum(data) / (data.shape[0] * data.shape[1])
    
    @staticmethod
    def corr_coef(arr1: np.ndarray, arr2: np.ndarray) -> Optional[float]:
        """Calculate the Pearson correlation coefficient between two arrays."""
        if len(arr1) < 2 or len(arr2) < 2:
            return None
        try:
            return np.corrcoef(arr1, arr2)[0, 1]
        except:
            return None



