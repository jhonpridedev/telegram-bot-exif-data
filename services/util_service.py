import re
import uuid
import mimetypes 

class UtilService:
    
    def get_random_filename(self) -> str:
        return uuid.uuid4()
    
    def string_to_slug(self, text: str) -> str:
        # Remove non-alphanumeric characters
        text = re.sub(r'\W+', ' ', text)

        # Replace spaces with hyphens
        # And prevent consecutive hyphens
        text = re.sub(r'\s+', '-', text)

        # Remove leading and trailing hyphens
        text = text.strip('-')

        # Convert to lowercase
        text = text.lower()

        return text
    
    def mimetype_to_ext(self, mime_type: str) -> str:
        return mimetypes.guess_extension(mime_type, strict=False)    