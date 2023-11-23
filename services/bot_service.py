from .telegram_bot_service import TelegramBotService
from .util_service import UtilService
from .file_service import FileService
from .exif_service import ExifService
from config.services import Service
import traceback
from .logger_service import Logger

class BotService:
    
    def __init__(self) -> None:        
        self.util_svc = UtilService()
        self.file_svc = FileService()        
    
    def process(self, request_data) -> None:
        try:            
            if 'message' in request_data:         
                text = request_data.get('message').get('text')           
                chat_id = request_data.get('message').get('chat').get('id')
                message_id = request_data.get('message').get('message_id')
                user_first_name = request_data.get('message').get('from').get('first_name')                
                        
                if 'document' in request_data.get('message'):                    
                    document = request_data.get('message').get('document')
                    self._process_document(chat_id, message_id, document)
                    
                elif 'photo' in request_data.get('message'):                    
                    TelegramBotService.send_message({'chat_id': chat_id, 'reply_to_message_id': message_id, 'text': "Upload the photo or image as a document 😀"})
                    
                elif 'entities' in request_data.get('message'):
                    command_type = request_data.get('message').get('entities')[0].get('type')
                    
                    if command_type == 'bot_command' and text == '/start':                          
                        TelegramBotService.send_message({'chat_id': chat_id, 'text': f"Hi {user_first_name}, I am a bot that obtains exif data, hidden data or metadata from an image file."})
                        
        except Exception as ex:                            
            TelegramBotService.send_message({'chat_id': chat_id, 'reply_to_message_id': message_id, 'text': "An error occurred 😞, please try again"})
            
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
                 
                      
    def _process_document(self, chat_id: int, message_id: int , document: object) -> None:
        
        file_id = document.get('file_id')
        file_name = document.get('file_name')
        mime_type = document.get('mime_type')
        file_extension = self.util_svc.mimetype_to_ext(mime_type)    
        
        supported_ext = ('.jpg', '.png', '.jpeg')
        supported_ext_text = ', '.join(supported_ext)
        
        if file_extension in supported_ext:        
            file_repsonse = TelegramBotService.get_file(file_id)
            file_data = file_repsonse.json()
            
            file_content_response = TelegramBotService.get_content(file_data.get('result').get('file_path'))    
            file_name_for_storage = f"{self.util_svc.get_random_filename()}{file_extension}"   
            file_path = f"./storage/files/{file_name_for_storage}"
            self.file_svc.save_file(file_content_response.content, file_path)
                                    
            exif_svc = ExifService(file_path, file_name)
            exif_data = exif_svc.get_data()
            text = self._get_text_from_exif(exif_data)            
            TelegramBotService.send_message({'chat_id': chat_id, 'reply_to_message_id': message_id, 'parse_mode': 'HTML', 'text': text if text else 'No exif data'})                  
                
        else:
            TelegramBotService.send_message({'chat_id': chat_id, 'reply_to_message_id': message_id, 'text': f"I can only process files in the following formats {supported_ext_text} 😞"})  
        
    def _get_text_from_exif(self, exif_data: dict) -> str|None:
        text = None
        
        if exif_data.get('has_exif'):     
            url = None
            latitude_dd = exif_data.get('exif').get('gps').get('latitude_dd')
            longitude_dd = exif_data.get('exif').get('gps').get('longitude_dd')
            if latitude_dd and exif_data.get('exif').get('gps').get('longitude_dd'):                
                url = f"{Service.GOOGLE_MAPS_LINK}{latitude_dd},{longitude_dd}"                
                 
            text = "<b>🖼️ IMAGE</b>"
            text += f" \n✓ File name → {exif_data.get('exif').get('image').get('name')}"
            text += f" \n✓ File size → {exif_data.get('exif').get('image').get('size', 'unknown')} B"
            text += f" \n✓ Created at → {exif_data.get('exif').get('image').get('created_at', 'unknown')}"
            text += f" \n✓ Height → {exif_data.get('exif').get('image').get('height', 'unknown')} px"
            text += f" \n✓ Width → {exif_data.get('exif').get('image').get('width', 'unknown')} px"
            
            text += f"\n\n<b>📸 CAMERA</b>"
            text += f" \n✓ Make → {exif_data.get('exif').get('camera').get('camera_make', 'unknown')}"
            text += f" \n✓ Model → {exif_data.get('exif').get('camera').get('camera_model', 'unknown')}"
            text += f" \n✓ Height → {exif_data.get('exif').get('camera').get('height', 'unknown')} ppp"
            text += f" \n✓ Width → {exif_data.get('exif').get('camera').get('width', 'unknown')} ppp"
            text += f" \n✓ Software → {exif_data.get('exif').get('camera').get('software', 'unknown')}"
            
            text += f"\n\n<b>🌎 GPS</b>"
            text += f" \n✓ latitude dms → {exif_data.get('exif').get('gps').get('latitude_dms', 'unknown')}"
            text += f" \n✓ longitude dms → {exif_data.get('exif').get('gps').get('longitude_dms', 'unknown')}"
            text += f" \n✓ latitude dd → {exif_data.get('exif').get('gps').get('latitude_dd', 'unknown')}"
            text += f" \n✓ longitude dd → {exif_data.get('exif').get('gps').get('longitude_dd', 'unknown')}"
                        
            text += f"\n\n<b>📍 LOCATION</b> \n"
            text += url if url else 'unknown'
            
        return text