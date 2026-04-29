import abc

import turtle
import math

class Shape(abc.ABC):
    """
    Abstract base class for geometric shapes.
    """

    @abc.abstractmethod
    def Area(self): pass



class ShapeCollor:
    """
    Manages fill color for geometric shapes.
    """
    def __init__(self):
        """
        Creates triangle from two sides and included angle.
        
        Args:
            a: length of first side
            b: length of second side
            c_angle: angle between sides (degrees)
        """
        self._color = "skyblue"

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = color


class Triangle(Shape):
    """
    Triangle defined by two sides and included angle (SAS).
    """
    def __init__(self, a, b, c):
        super().__init__()
        self.a = a
        self.b = b
        self.cAngle = c
        self.colorInfo = ShapeCollor()
        self.colorInfo.color = "none"


    def Area(self):
        """
        Calculates area using SAS formula: (1/2)*a*b*sin(C).
        """
        return self.a * self.b * 0.5 * math.sin(self.cAngle * math.pi / 180)    


    def GetInfo(self) -> str:
        """
        Returns triangle description string.
        """
        return 'The triangle with side A = {} and side B = {} and angle between them {}'.format(self.a, self.b, self.cAngle)



    def __drawColor(self, trtl):
        """Draws triangle with colored fill."""
        trtl.fillcolor(self.colorInfo.color)
        trtl.begin_fill()
        self.__drawInner(trtl)
        trtl.end_fill()



    def __drawInner(self, trtl):
        """
        Core drawing logic for triangle.
        Draws sides A and B at angle C.
        """
        trtl.forward(self.a)
        trtl.left(180 - self.cAngle)
        trtl.forward(self.b)
        trtl.goto(0,0)
    
            


    def Draw(self):
        """
        Renders triangle using turtle graphics.
        - "none" = outline only
        - other color = filled
        """
        trtl = turtle.Turtle()    
        if self.colorInfo.color == "none":
            self.__drawInner(trtl)
        else:
            self.__drawColor(trtl)   
            trtl.end_fill()
        turtle.exitonclick()
 

            
    
    
