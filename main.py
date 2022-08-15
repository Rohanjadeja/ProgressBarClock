from machine import Pin
from ds1302 import DS1302
import array, time
import rp2


ds = DS1302(Pin(0),Pin(1),Pin(2))

ds.date_time() # returns the current datetime.

#ds.date_time([2022, 8, 10, 3, 19, 10, 10]) # set datetime.

print(ds.date_time())



# Configure the number of WHITES2812 LEDs.
NUM_LEDS = 24
Pin_NUM = 7

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(Pin_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGBLACK values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        time.sleep(wait)
        pixels_show()
    time.sleep(0.2)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(wait)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (50, 237, 50)
CYAN = (0, 255, 255)
BLUE = (39, 57, 187)
PURPLE = (113, 39, 230)
WHITE = (255, 255, 255)
ORANGE = (238, 186, 48)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)
'''
print("fills")
for color in COLORS:
    pixels_fill(color)
    pixels_show()
    time.sleep(0.2)

print("chases")
for color in COLORS:
    color_chase(color, 0.01)

print("rainbow")
rainbow_cycle(0.1)
'''

while True:
    (YELLOW,M,D,day,hr,m,s) = ds.date_time()

# Night time color settings
    if hr == 0:
        brightness = 0.1
        for a in range(11):
            pixels_set(a, BLACK)
            time.sleep(0.01)
            pixels_show()
            
        if m == 0:
            for b in range(12):
                pixels_set(b+12, BLACK)
                time.sleep(0.01)
                pixels_show()
    
        if m > 0:
            for b in range(int(m/5)):
                pixels_set(b+12, PURPLE)
                time.sleep(0.01)
                pixels_show()
    
    if hr > 0 and hr <= 7:
        brightness = 0.1
        for a in range(hr):
            pixels_set(a, BLUE)
            time.sleep(0.01)
            pixels_show()
            
        if m == 0:
            for b in range(12):
                pixels_set(b+12, BLACK)
                time.sleep(0.01)
                pixels_show()
    
        if m > 0:
            for b in range(int(m/5)):
                pixels_set(b+12, PURPLE)
                time.sleep(0.01)
                pixels_show()
                
    if hr > 19 and hr <=24:
        brightness = 0.1
        for a in range(hr-12):
            pixels_set(a, BLUE)
            time.sleep(0.01)
            pixels_show()
            
        if m == 0:
            for b in range(12):
                pixels_set(b+12, BLACK)
                time.sleep(0.01)
                pixels_show()
    
        if m > 0:
            for b in range(int(m/5)):
                pixels_set(b+12, PURPLE)
                time.sleep(0.01)
                pixels_show()

#End night time color
                
#Day time color settings

    if hr > 7 and hr <= 12:
        brightness = 0.5
        for a in range(hr):
            pixels_set(a, ORANGE)
            time.sleep(0.01)
            pixels_show()
            
        if m == 0:
            for b in range(12):
                pixels_set(b+12, BLACK)
                time.sleep(0.01)
                pixels_show()
    
        if m > 0:
            for b in range(int(m/5)):
                pixels_set(b+12, WHITE)
                time.sleep(0.01)
                pixels_show()
            
    if hr > 12 and hr <=19:
        brightness = 0.5
        for a in range(hr-12):
            pixels_set(a, ORANGE)
            time.sleep(0.01)
            pixels_show()
            
        if m == 0:
            for b in range(12):
                pixels_set(b+12, BLACK)
                time.sleep(0.01)
                pixels_show()
    
        if m > 0:
            for b in range(int(m/5)):
                pixels_set(b+12, WHITE)
                time.sleep(0.01)
                pixels_show()
            
            
    time.sleep(10)