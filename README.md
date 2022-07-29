# GTNH-Custom-Overlays

Allows the creation of custom overlay textures for GT materials inside of GT. To use this simply download the repo, swap out the background.png file for your textures and then run the program. This will produce all the block and item cut outs in the associated shapes/blocks or shapes/items directory. Simply copy these into the CUSTOM/material_name directory inside of GT. Remember you *must* include the overlay images or the textures will not load in.

To define a material as custom inside of GTNH you just replace the TextureSet.xxx inside of each Materials constructor with TextureSet(directory_name, true). See SpaceTime for an example.

You may need to adjust the alpha or the saturation of the image to get a good colour. Ask Colen#6943 on Discord if you are stuck.
