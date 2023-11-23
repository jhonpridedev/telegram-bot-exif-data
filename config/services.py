from decouple import config

class Service:    
    APP_ENV = True if config('APP_ENV') == 'true' else False
    
    TELEGRAM_BOT = {        
        'token': config('TELEGRAM_BOT_TOKEN'),
        'webhook': config('TELEGRAM_BOT_WEBHOOK')
    }
    
    CONTACT_PAGE_LINK = config('CONTACT_PAGE_LINK')    
    GOOGLE_MAPS_LINK = config('GOOGLE_MAPS_LINK')    
    