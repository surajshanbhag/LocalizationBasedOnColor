class ColorMarker:
    color_lower=(255,255,255)
    color_upper=(255,255,255)
    marker_boundary=((0,0),(0,0))
    position_image=(0,0)
    position_map=(0,0)
    position_ideal=(0,0)
    position_real=(0,0)
    bounding_circle_radius=0
    def __init__(self,color_lower,color_upper,ideal):
        self.color_lower=color_lower
        self.color_upper=color_upper
        self.position_ideal=ideal
    def __getitem__(self,color):
        return self.color
    def __getitem__(self,position_image):
        return self.position_image
    def __getitem__(self,position_real):
        return self.position_real
    def updateImagePosition(self,position):
        self.position_image=position
    def addPointAsAvg(self,position):
        newpos1=(int)(self.position_image[0]*0.9+position[0]*0.1)
        newpos2=(int)(self.position_image[1]*0.9+position[1]*0.1)
        self.position_image=(newpos1,newpos2)
