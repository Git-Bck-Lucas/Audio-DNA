import logging
import os
# Logger erstellen - wie heißt mein Logger 

def setup_logging():
    
    env = os.getenv("ENV", "development")

    console_handler = logging.StreamHandler() # Objekt das Logging auf Konsole ausgibt
    console_handler.setLevel(logging.DEBUG) # Mit Level DEBUG

    file_handler = logging.FileHandler("logs/app.log") # Objekt das Logging in einer Datei ausgibt
    file_handler.setLevel(logging.ERROR) # Mit Level Error

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') # GewünschtesFormat
    console_handler.setFormatter(formatter) # Füge Format dem Handler hinzu
    file_handler.setFormatter(formatter)
    
    if env == 'production':
        handlers = [file_handler]
    else:
        handlers = [console_handler, file_handler]
        

    logging.basicConfig( # Nimm diese beiden Handler, Zeige lles ab DEBUG, Nutze sie für alle Logger in der App
        level=logging.DEBUG,
        handlers= handlers
    )
    
    return logging.getLogger("audio_dna")

logger = setup_logging()

