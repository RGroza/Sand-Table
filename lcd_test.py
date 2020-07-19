from utils import i2c_lcd_driver

lcd = i2c_lcd_driver.lcd()

lcd.lcd_display_string("Hello World!", 1)
