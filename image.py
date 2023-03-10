from PIL import Image, ImageDraw, ImageFont
from random import randint

message = [' 1. shaked.dotan - 20',
           ' 2. Victor_Churikov - 20',
           ' 3. Barel_Elbaz - 15, Tie-breaker: Won by most posts (5)!',
           ' 4. Roy_Zohar - 15',
           ' 5. Micka_ra - 15',
           ' 6. omri_spector - 10',
           ' 7. ShemTov - 10',
           ' 8. Ester_Benedikt - 10',
           ' 9. Ido_Gada    - 10',
           '10. Oron_Cohen  - 5',
           '11. shai_hod    - 5',
           '12. Amir_Shalem - 5']

# make_color = lambda : (randint(50, 255), randint(50, 255), randint(50,255))
def fnt_color(i, tie_breaker):
    if i < 3:
        if tie_breaker:
            return (255, 255, 0)
        else:
            return (0, 255, 0)
    else:
        return (255, 255, 255)

img_hight = len(message)*45+20*2
img_width = 1000
img_background = (0, 0, 0) # black # (255, 255, 255) # white #
fnt_size = 35

img = Image.new('RGB', (img_width, img_hight), color=img_background)
draw = ImageDraw.Draw(img)
fnt = ImageFont.truetype('./monaco.ttf', fnt_size) # chars are differnat sizes

tie_breaker = False
for index, line in enumerate(message):
    if index == 2:
        tie_breaker = "Tie-breaker:" in message[index]
    draw.text((40,45*index+20), message[index], font=fnt, fill=fnt_color(index, tie_breaker))

img.save('pil_text_font.png')