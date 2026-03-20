

import sys


import math
from .. utils import io
from .. utils import menu


def TaylorExp(x, eps :float) -> tuple:

    etalon = math.exp(x)
    tseries = 0

    for i in range(500):
        tseries += math.pow(x, i) / math.factorial(i)
        if (math.fabs(tseries - etalon) <= eps):
            return i, tseries, etalon


    return -1, tseries, etalon



def Task1():
    print("Welcome to the programm that help with finding the number of Taylort seriece")
    screen = True

    while (screen):
        print("Input the float x to calculate TaylorSeries series number")
        x = io.validate_user_input_float("Enter float number: ")


        print("Input the float epsilon to calculate TaylorSeries series number")
        eps = io.validate_user_input_float("Enter float number: ")


        ret = TaylorExp(x, eps)
        print("-----------------------------------------------------------------------")
        print(f"|{"X":>10}|{"n":>5}|{"F(x)":>20}|{"FMATH(x)":>20}|{"EPSILON":>10}|")
        print(f"|{x:>10}|{ret[0]:>5}|{ret[1]:>20}|{ret[2]:>20}|{eps:>10}|")
        print("-----------------------------------------------------------------------")

        screen = menu.ProgramEnd()





Task1()


