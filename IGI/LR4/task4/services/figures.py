import abc

import turtle
import math

class Shape(abc.ABC):
    

    @abc.abstractmethod
    def Area(self): pass



class ShapeCollor:
    def __init__(self):
        self._color = "skyblue"

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = color


class Triangle(Shape):
    def __init__(self, a, b, c):
        super().__init__()
        self.a = a
        self.b = b
        self.cAngle = c
        self.colorInfo = ShapeCollor()
        self.colorInfo.color = "none"


    def Area(self):
        return self.a * self.b * 0.5 * math.sin(self.cAngle * math.pi / 180)    


    def GetInfo(self) -> str:
        return 'The triangle with side A = {} and side B = {} and angle between them {}'.format(self.a, self.b, self.cAngle)



    def __drawColor(self, trtl):
        trtl.fillcolor(self.colorInfo.color)
        trtl.begin_fill()
        self.__drawInner(trtl)
        trtl.end_fill()



    def __drawInner(self, trtl):
        trtl.forward(self.a)
        trtl.left(180 - self.cAngle)
        trtl.forward(self.b)
        trtl.goto(0,0)
    
            


    def Draw(self):
        trtl = turtle.Turtle()    
        if self.colorInfo.color == "none":
            self.__drawInner(trtl)
        else:
            self.__drawColor(trtl)   
            trtl.end_fill()
        turtle.exitonclick()
 

            
    
    
