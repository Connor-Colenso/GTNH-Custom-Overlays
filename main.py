import json

from PIL import Image, ImageEnhance
import os

from PIL.Image import Resampling


def scale_image(image, width, height):
    return image.resize((width, height), resample=Resampling.BOX)


def image_generator(
        background: Image.Image,
        overlay: Image.Image,
        animated: bool,
        texture_type: str,
        frametime: int = 1,
        alpha: int = 75,
        saturation: float = 1.5,
        glued_image=None
) -> None:
    """
    :param glued_image:
    :param texture_type: Item or Block. Determines where output will go.
    :param saturation: Saturation of the finished image to try remove some white washing from the overlay.
    :param background: Actual background image, can be singular 16x16 or 16x(16xn) where n is an integer.
    :param overlay:    Overlay image, i.e. ingot, screw etc. See shapes folder.
    :param animated:   Is the image animated? If so it will generate an associated mcmeta file.
    :param frametime:  Frametime of the mcmeta file. I.e. how long should each frame last (in ticks).
    :param alpha:      Alpha of the overlay, I suggest adjusting this to prevent white washing.
    :return:           None. Images are saved dynamically depending on name of overlay to output file.
    """

    # This script is not the best written but gets the job done.

    # Only get the name of the file, not the directory it is in.
    save_name = overlay.filename[7:]

    background_width, background_height = background.size
    overlay_width, overlay_height = overlay.size

    # Scale up overlay if needed.
    if background_width != 16:
        overlay = scale_image(overlay, background_width, background_width)

    overlay_copy = overlay.copy()
    overlay_copy = overlay_copy.convert("RGBA")

    overlay_width, overlay_height = overlay.size

    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    overlay.putalpha(alpha)
    # Iterate down image.
    for y in range(0, background_height, overlay_height):
        background.paste(overlay, (0, y), overlay)

    for x in range(overlay_width):
        for y in range(overlay_height):
            try:
                # if "turbineBlade" in save_name:
                #     None
                if overlay_copy.getpixel((x, y))[3] == 0:
                    for y_true in range(0, background_height, background_width):
                        background.putpixel((x, y + y_true), (0, 0, 0, 0))
            except:
                pass

    for x in range(background_width):
        for y in range(background_height):
            current_pixel = background.getpixel((x, y))
            if current_pixel[3] != 0:
                background.putpixel((x, y), (current_pixel[0], current_pixel[1], current_pixel[2], 255))

    # Enhances the colour to prevent white washing.
    background = ImageEnhance.Color(background).enhance(saturation).convert("RGBA")

    if glued_image is not None:
        for y in range(0, background_height, overlay_height):
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
        if ".png" in save_name:
            with open(f"output/{save_name}.mcmeta", "w") as f:
                json.dump(data, f)
        else:
            with open(f"output/{save_name}.png.mcmeta", "w") as f:
                json.dump(data, f)

    if (texture_type == "item") and save_name in os.listdir("shapes/output"):
        overlay_dump = Image.new("RGBA", size=(16, 16))
        overlay_dump.putalpha(0)
        overlay_dump.save(f"output/{save_name}_OVERLAY")


def main() -> None:
    # This is the base image you will be using to cut out your textures.
    background = Image.open("Trifecta_vertical.png")

    # Is texture animated. Creates associated mcmeta files with frametime defined below.
    animated = True
    # Ticks per frame of animation.
    frametime = 3
    # Saturation of the image. This can help bring back colour if it gets whitewashed by the overlays.
    saturation = 3
    # Intensity of the overlay. 0-255.
    alpha = 150
    # Scale up the background image.
    scaled_main = False

    if scaled_main:
        background = scale_image(background, 512, 57856)

    for filename in os.listdir("shapes/parts"):

        # Necessary for mac systems given they have hidden DS_Store files.
        if "DS_Store" not in filename:
            overlay = Image.open(f"shapes/parts/{filename}")
            print(filename)
            glued_image = Image.open(f"shapes/parts_overlay/{filename}")
            image_generator(background, overlay, animated, "blocks", frametime=frametime, alpha=alpha,
                            saturation=saturation,
                            glued_image=glued_image
                            )
            overlay.close()

    for filename in os.listdir("shapes/items"):

        # DS_Store check necessary for mac systems given they have hidden DS_Store files.
        if ("DS_Store" not in filename) and ("_OVERLAY" not in filename):
            overlay = Image.open(f"shapes/items/{filename}")
            print(filename)
            image_generator(background,
                            overlay,
                            animated,
                            "items",
                            frametime=frametime,
                            alpha=alpha,
                            saturation=saturation
                            )
            overlay.close()

    for filename in os.listdir("shapes/blocks"):

        # Necessary for mac systems given they have hidden DS_Store files.
        if "DS_Store" not in filename:
            overlay = Image.open(f"shapes/blocks/{filename}")
            try:
                glued_image = Image.open(f"shapes/blocks_overlay/{filename}")
            except Exception:
                glued_image = Image.new(mode="RGBA", size=overlay.size)
            print(filename)
            image_generator(background,
                            overlay,
                            animated,
                            "blocks",
                            frametime=frametime,
                            alpha=alpha,
                            saturation=saturation,
                            glued_image=glued_image
                            )
            overlay.close()

    for filename in os.listdir("shapes/fluids"):

        # Necessary for mac systems given they have hidden DS_Store files.
        if "DS_Store" not in filename:
            overlay = Image.open(f"shapes/fluids/{filename}")
            print(filename)
            image_generator(background,
                            overlay,
                            animated,
                            "blocks",
                            frametime=2,
                            alpha=alpha,
                            saturation=saturation
                            )
            overlay.close()


if __name__ == "__main__":
    main()
