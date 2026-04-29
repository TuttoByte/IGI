
import pandas as pd
import numpy as np
from IPython.display import display
from os import system

def menu() -> None:

        system("clear")
            
        df = pd.read_csv('/home/udainoko/Documents/453503_SAVINOV_26/IGI/LR4/task6/car_price_dataset_medium.csv')
        df.set_index(['Model_Year', 'Brand'], inplace=True)
        df = df[['Price_USD', 'Mileage_kmpl']]
        display(df)



                

        df = pd.read_csv('/home/udainoko/Documents/453503_SAVINOV_26/IGI/LR4/task6/car_price_dataset_medium.csv')

        q1 = df['Price_USD'].quantile(0.25)
        q3 = df['Price_USD'].quantile(0.75)


        highers = df[df['Price_USD'] <= q1]
        lowers = df[df['Price_USD'] >= q3]

        

        lowerEngineHp = lowers['Maxp_Power_bh'].mean()
        higherEngineHp = highers['Maxp_Power_bh'].mean()

        print("Low-Price EnginePowers mean", lowerEngineHp)
        print("High-Price EnginePowers mean", higherEngineHp)



        ratio = round(higherEngineHp/lowerEngineHp, 2)
        print("The result ratio between two types:", ratio)
         


        
    
# If module is executing run it
if __name__ == "__main__":
    menu()
