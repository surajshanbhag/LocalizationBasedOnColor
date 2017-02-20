class ColorMarker:


    def __init__(self,index,colors):
        self.index=index
        self.hsv_lower=colors[0]
        self.hsv_upper=colors[1]
        self.position_current_pixels=(0,0)
        self.position_current_real=(0,0)
        self.position_average_pixels=(0,0)
        self.position_average_real=(0,0)
        self.boundaries=[(0,0),(0,0)]
        self.position_map=(0,0)
        self.boundingCircle_radius=0
        self.index=0
        pass

    def updateImagePosition(self,position,count):
        self.position_current_pixels=position
        newpos_x=(int)((self.position_current_pixels[0]*(count-1)+position[0])/count)
        newpos_y=(int)((self.position_current_pixels[1]*(count-1)+position[1])/count)
        self.position_average_pixels=(newpos_x,newpos_y)

    def updateRealPosition(self,positon):
        self.position_current_real=position
        newpos_x=(int)(self.position_current_real[0]*0.9+position[0]*0.1)
        newpos_y=(int)(self.position_current_real[1]*0.9+position[1]*0.1)
        self.position_average_real=(newpos_x,newpos_y)

