#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in3e
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import converter

logging.basicConfig(level=logging.DEBUG)
def display(Himage):
    try:
        epd = epd7in3e.EPD()   
        logging.info("init")
        epd.init()
        #epd.Clear()
        time.sleep(1)
        # display image
        logging.info("display image")
        epd.display(epd.getbuffer(Himage))
        time.sleep(1)
        logging.info("Done! - Goto Sleep...")
        epd.sleep()
            
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in3e.epdconfig.module_exit(cleanup=True)
        exit()


#display("","")
