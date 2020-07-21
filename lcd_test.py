from utils import i2c_lcd_driver
from time import sleep

lcd = i2c_lcd_driver.lcd()

lcd.lcd_display_string("Hello World!", 1)
lcd.lcd_display_string("Hello World!", 2)

sleep(1)

lcd.lcd_display_string("World Hello!", 1)
lcd.lcd_display_string("World Hello!", 2)
