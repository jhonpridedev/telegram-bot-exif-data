from exif import Image
import os
import warnings
import mimetypes

class ExifService:
    
    def __init__(self, file_path: str, file_name: str) -> None:
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        self.file_name = file_name
        self.file_image = self.get(file_path)
        self.file_size = os.path.getsize(file_path)        
        
    
    def get(self, file_path: str)-> Image:
        with open(file_path, "rb") as image_1:
            return Image(image_1)
            
    def get_data(self) -> dict:
        has_exif = self.file_image.has_exif        
        
        exif = {}
        if has_exif:          
            
            gps = self.gps_data(
                self.file_image.get('gps_latitude', None), 
                self.file_image.get('gps_latitude_ref', None),                
                self.file_image.get('gps_longitude', None), 
                self.file_image.get('gps_longitude_ref', None)                
            )
            
            exif = {                
                'image': {
                    'name': self.file_name,                    
                    'created_at': f"{self.file_image.get('datetime_original', '')} {self.file_image.get('offset_time', '')}",
                    'height': self.file_image.get('pixel_y_dimension', None),
                    'width': self.file_image.get('pixel_x_dimension', None),                                  
                    'size': self.file_size
                },
                'camera': {
                    'camera_make': self.file_image.get('make', None),                    
                    'camera_model': self.file_image.get('model', None),   
                    'lens_make': self.file_image.get('lens_make', None),
                    'lens_model': self.file_image.get('lens_model', None),
                    'lens_specification': self.file_image.get('lens_specification', None),
                    'height': self.file_image.get('y_resolution', None),
                    'width': self.file_image.get('x_resolution', None),
                    'software': self.file_image.get('software', None),                         
                },
                'gps': gps
            }            
        
        return {
            'has_exif': has_exif,
            'exif': exif
        }
        
        
    def gps_data(self, gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref) -> dict:        
        try:
            latitude_dms = None
            longitude_dms = None
            latitude_dd = None
            longitude_dd = None
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:            
                latitude_dms = f"{self.format_dms_coordinates(gps_latitude)} {gps_latitude_ref}"
                longitude_dms = f"{self.format_dms_coordinates(gps_longitude)} {gps_longitude_ref}"
                latitude_dd = self.dms_coordinates_to_dd_coordinates(gps_latitude, gps_latitude_ref)
                longitude_dd = self.dms_coordinates_to_dd_coordinates(gps_longitude, gps_longitude_ref)
        
        finally:                         
            return {
                'latitude_dms': latitude_dms,
                'longitude_dms': longitude_dms,
                'latitude_dd': latitude_dd,
                'longitude_dd': longitude_dd,
            }
            
        
    def format_dms_coordinates(self, coordinates) -> str:        
        if coordinates is not None  and len(coordinates) > 0:            
            return  f"{coordinates[0]}° {coordinates[1]}\' {coordinates[2]}\""
        
        return None

    def dms_coordinates_to_dd_coordinates(self, coordinates, coordinates_ref) -> float:
        decimal_degrees = coordinates[0] + \
                        coordinates[1] / 60 + \
                        coordinates[2] / 3600
        
        if coordinates_ref == "S" or coordinates_ref == "W":
            decimal_degrees = -decimal_degrees
        
        return decimal_degrees