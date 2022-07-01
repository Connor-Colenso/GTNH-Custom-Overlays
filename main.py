import json
import os

from PIL import Image, ImageEnhance


def image_generator(
    background: Image.Image, overlay: Image.Image, animated: bool, texture_type: str, frametime: int = 1, alpha: int = 75, saturation: float = 1.5, glued_image=None
) -> None:
    """
    :param background: Actual background image, can be singular 16x16 or 16x(16xn) where n is an integer.
    :param overlay:    Overlay image, i.e. ingot, screw etc. See shapes folder.
    :param animated:   Is the image animated? If so it will generate an associated mcmeta file.
    :param frametime:  Frametime of the mcmeta file. I.e. how long should each frame last (in ticks).
    :param alpha:      Alpha of the overlay, I suggest adjusting this to prevent white washing.
    :return:           None. Images are saved dynamically depending on name of overlay to output file.
    """

    # This script is not the best written but gets the job done.

    save_name = overlay.filename[7:]

    overlay_copy = overlay.copy()
    overlay_copy = overlay_copy.convert("RGBA")

    overlay_width, overlay_height = overlay.size

    true_image_width, true_image_height = background.size
    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    overlay.putalpha(alpha)
    for y in range(0, true_image_height, 16):
        background.paste(overlay, (0, y), overlay)

    for x in range(overlay_width):
        for y in range(overlay_height):
            try:
                if "turbineBlade" in save_name:
                    print(overlay_copy.getpixel((x, y)))
                if overlay_copy.getpixel((x, y))[3] == 0:
                    for y_true in range(0, true_image_height, 16):
                        background.putpixel((x, y + y_true), (0, 0, 0, 0))
            except BaseException:
                None

    for x in range(true_image_width):
        for y in range(true_image_height):
            current_pixel = background.getpixel((x, y))
            if current_pixel[3] != 0:
                background.putpixel((x, y), (current_pixel[0], current_pixel[1], current_pixel[2], 255))

    # Enhances the colour to prevent white washing.
    background = ImageEnhance.Color(background).enhance(saturation).convert("RGBA")

    if (glued_image != None):
        for y in range(0, true_image_height, 16):
            background.paste(glued_image, (0, y), glued_image)

    background.save(f"output/{save_name}")
    background.close()
    overlay.close()

    # Json that will be saved as a .mcmeta file for each associated item. If it is animated.
    if animated:
        # Frametime determines amount of ticks spent on each frame. 20 ticks per second.
        data = {
            "animation": {
                "frametime": frametime,
            }
        }
        with open(f"output/{save_name}.mcmeta", "w") as f:
            json.dump(data, f)

    if (texture_type == "item") and save_name in os.listdir("shapes/output"):
        overlay_dump = Image.new("RGBA", size=(16, 16))
        overlay_dump.putalpha(0)
        overlay_dump.save(f"output/{save_name}_OVERLAY")


def main() -> None:
    # This is the base image you will be using to cut out your textures.
    background = Image.open("background.png")
    animated = True  # Is texture animated.
    frametime = 1  # Ticks per frame of animation.

    for filename in os.listdir("shapes/items"):

        # DS_Store check necessary for mac systems given they have hidden DS_Store files.
        if ("DS_Store" not in filename) and ("_OVERLAY" not in filename):
            overlay = Image.open(f"shapes/items/{filename}")
            print(filename)
            image_generator(background, overlay, animated, "items", frametime=frametime, alpha=125, saturation=1.5)
            overlay.close()

    for filename in os.listdir("shapes/blocks"):

        # Necessary for mac systems given they have hidden DS_Store files.
        if "DS_Store" not in filename:
            overlay = Image.open(f"shapes/blocks/{filename}")
            image_generator(background, overlay, animated, "blocks", frametime=3, alpha=75, saturation=1.5)
            overlay.close()

    for filename in os.listdir("shapes/parts"):

        # Necessary for mac systems given they have hidden DS_Store files.
        if "DS_Store" not in filename:
            overlay = Image.open(f"shapes/parts/{filename}")
            glued_image = Image.open(f"shapes/parts_overlay/{filename}")
            image_generator(background, overlay, animated, "blocks", frametime=3, alpha=75, saturation=1.5, glued_image=glued_image)
            overlay.close()


if __name__ == "__main__":
    main()
