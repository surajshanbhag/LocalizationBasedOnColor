
from Marker import ColorMarker


class Bot:
    bot_position_current=(0,0)
    bot_orientation_angle=0.0


    def __init__(self,color1,color2):
        self.Marker1=ColorMarker(0,color1)
        self.Marker2=ColorMarker(1,color2)
        pass
