# coding=utf-8

import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pilkit.processors import ResizeToFit

# def add_watermark(self, image):
#     # Code for adding the watermark goes here.
#     return self.watermark(image, "© 2016 Zoomdoggy Design", "arial black.ttf", None, 36)


def resize(image, *size):
    """
    size is a pair like 600, 600
    """
    processor = ResizeToFit(*size)
    return processor.process(image)


def reduce_opacity(image, opacity):
    """
    Returns an image with reduced opacity.
    Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/362879
    """
    assert opacity >= 0 and opacity <= 1
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    else:
        image = image.copy()
    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    image.putalpha(alpha)
    return image


def calculate_position(image, position, textsize, margin):
    if position == 0: # centered
        return [(image.size[i]/2)-(textsize[i]/2) for i in [0,1]]
    elif position == 1: # upper left
        return margin
    elif position == 2: # upper right
        return [image.size[0]-margin[0]-textsize[0], margin[1]]
    elif position == 3: # lower right
        # return [image.size[0]-margin[0]-textsize[0], image.size[1]-margin[1]-textsize[1]]
        return [image.size[i]-margin[i]-textsize[i] for i in [0,1]]
    elif position == 4: # lower left
        return [margin[0], image.size[1]-margin[1]-textsize[1]]


def add_watermark(image, text, font_path, position, font_scale=None, font_size=36, color=(255,255,255), opacity=0.6, margin=(30, 30)):
    """
    image - PIL Image instance
    text - text to add over image
    font_path - font that will be used
    font_scale - font size will be set as percent of image height
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    textlayer = Image.new("RGBA", image.size, (0,0,0,0))
    textdraw = ImageDraw.Draw(textlayer)

    if font_scale:
        width, height = image.size
        font_size = int(font_scale*height)

    while True:
        font=ImageFont.truetype(font_path, font_size)
        textsize = textdraw.textsize(text, font=font)
        if (textsize[0] + margin[0] * 2 < image.size[0]):
            break
        font_size -= 1

    textpos = calculate_position(image, position, textsize, margin)
    textdraw.text(textpos, text, font=font, fill=color)
    if opacity != 1:
        textlayer = reduce_opacity(textlayer,opacity)

    return Image.composite(textlayer, image, textlayer)
    # return imprint(image, text, font=font, position=position, opacity=opacity, color=color, margin=margin)


def main():
    if len(sys.argv) < 2:
        print("Image path is required")
        return

    if len(sys.argv) < 3:
        print("Watermark text is required")
        return

    processed_path = sys.argv[1] + "/processed"
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

    for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]):
        if not dirpath.endswith("processed"):
            for filename in filenames:
                try:
                    image = Image.open("%s/%s" % (dirpath, filename))
                    image = add_watermark(image, sys.argv[2], "arial.ttf", 0, font_scale=.08, margin=(30, 30))
                    image = resize(image, 400, 400)
                    # image = add_watermark(image, sys.argv[2], "arial.ttf", 0)
                    image.save("%s/%s" % (processed_path, filename), quality=80, optimize=True)
                except:
                    e = sys.exc_info()
                    print(e)
                    pass

if __name__ == "__main__":
    main()