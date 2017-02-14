class ColorMarker:
    color_lower=(255,255,255)
    color_upper=(255,255,255)
    position_image=(0,0)
    position_real=(0,0)
    bounding_circle_radius=0
    def __init__(self,color_lower,color_upper):
        self.color_lower=color_lower
        self.color_upper=color_upper
    def __getitem__(self,color):
        return self.color
    def __getitem__(self,position_image):
        return self.position_image
    def __getitem__(self,position_real):
        return self.position_real
