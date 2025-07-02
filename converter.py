from PIL import Image, ImageOps

# Deine E-Ink-Farbpalette – maximal 256 Farben erlaubt
PALETTE = [
    (0, 0, 0),       # Schwarz
    (255, 255, 255), # Weiß
    (255, 0, 0),     # Rot
    (255, 255, 0),   # Gelb
    (0, 255, 0),     # Grün
    (0, 0, 255)      # Blau
]

def create_palette_image(palette):
    """Erzeugt ein Pillow-Bild im 'P'-Modus mit eigener Palette"""
    palette_img = Image.new("P", (1, 1))
    
    # Pillow erwartet eine Liste mit 768 Werten (256 Farben × 3)
    flat_palette = []
    for color in palette:
        flat_palette.extend(color)
    # Auffüllen bis 256 Farben
    while len(flat_palette) < 768:
        flat_palette.extend((0, 0, 0))
    
    palette_img.putpalette(flat_palette)
    return palette_img


def convert(path, conv_style, width = 800, height = 480):
    # Bild laden und ggf. skalieren
    # image = Image.open(path)
    image = path
    if (image.width < image.height):
        image = image.transpose(Image.ROTATE_270)

    if (conv_style == "fit"):
        image = ImageOps.pad(image, (width,height), color=(255, 255, 255))
    elif (conv_style == "fill"):
        image = ImageOps.fit(image, (width,height), centering=(0.5, 0.5))
    elif (conv_style == "stretch"):
        image = image.resize((width,height))
    else:
        image = ImageOps.pad(image, (width,height), color=(255, 255, 255))

    # Palette-Bild erzeugen
    palette_img = create_palette_image(PALETTE)

    # Jetzt das Bild in den P-Modus konvertieren mit Floyd-Steinberg-Dithering
    dithered = image.convert("RGB").quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG)

    # zurückgeben
    return dithered
