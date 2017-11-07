import logging, time
import settings

class CustomLogger:
    """
    CustomLogger appends status information of each website url to logfile which 
    also includes time taken to complete the request and other information
    """
    logging.basicConfig(filename=settings.log_file, level=logging.INFO,)
    def write_to_log(self, message):
        logging.info("\t" + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                          + "\t"+  message)
