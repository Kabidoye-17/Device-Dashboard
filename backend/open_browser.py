import webbrowser

from utils.logger import get_logger

logger = get_logger(__name__)

def open_trading_site(site_url):
    try:
        webbrowser.open(site_url)
        logger.info(f"Opened {site_url} in browser")
        return {"status": "success", "message": f"Opened {site_url} in browser"}
    except Exception as e:
        logger.info(f"Error opening site: {str(e)}")
        return {"status": "error", "message": str(e)}