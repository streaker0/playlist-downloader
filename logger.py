import os
import logging
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        
        return super().format(record)

def setup_logging(logs_folder: str = "logs") -> logging.Logger:
    """Setup logging configuration"""
    
    # Create logs directory
    os.makedirs(logs_folder, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("playlist_downloader")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler for all logs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_folder, f"download_session_{timestamp}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pytube").setLevel(logging.WARNING)
    logging.getLogger("spotipy").setLevel(logging.WARNING)
    
    logger.info(f"Logging initialized. Session log: {log_file}")
    return logger