#!/usr/bin/env python

from gimpfu import *

def darkness_luminosity(image, drawable):

  # Create a desaturated layer
  desat_layer = pdb.gimp_layer_new_from_visible(image, image, "Desat")
  pdb.gimp_image_insert_layer(image, desat_layer, None, 0)

  desat_drawable = pdb.gimp_image_get_active_drawable(image)
  pdb.gimp_drawable_desaturate(desat_drawable, DESATURATE_LUMINANCE)

  # Make this the "Lights" channel
  lights_channel = pdb.gimp_channel_new_from_component(image, 0, "L")
  pdb.gimp_image_insert_channel(image, lights_channel, None, 0)

  # Select the Desat layer
  pdb.gimp_image_set_active_layer(image, desat_layer)

  # Select the whole image
  pdb.gimp_selection_all(image)

  # Subtract the Lights channel from the selection to get the Darks channel
  pdb.gimp_image_select_item(image, CHANNEL_OP_SUBTRACT, lights_channel)
  darks_channel = pdb.gimp_selection_save(image)
  darks_channel.name = 'D'

  # And repeat for the second Darks channel
  pdb.gimp_image_select_item(image, CHANNEL_OP_SUBTRACT, lights_channel)
  ddarks_channel = pdb.gimp_selection_save(image)
  ddarks_channel.name = 'DD'

  # Hide the desaturation layer and switch back to the base layer
  pdb.gimp_selection_none(image)
  pdb.gimp_layer_set_visible(desat_layer, False)

  # Add a D layer
  darks_layer = pdb.gimp_layer_new_from_visible(image, image, "D")
  pdb.gimp_image_insert_layer(image, darks_layer, None, 0)
  pdb.gimp_image_set_active_channel(image, darks_channel)
  darks_mask = pdb.gimp_layer_create_mask(darks_layer, ADD_MASK_CHANNEL)
  pdb.gimp_layer_add_mask(darks_layer, darks_mask)
  pdb.gimp_layer_set_mode(darks_layer, LAYER_MODE_ADDITION)
  pdb.gimp_layer_set_opacity(darks_layer, 50)

  pdb.gimp_layer_set_visible(darks_layer, False)

  # Add a DD layer
  ddarks_layer = pdb.gimp_layer_new_from_visible(image, image, "DD")
  pdb.gimp_image_insert_layer(image, ddarks_layer, None, 0)
  pdb.gimp_image_set_active_channel(image, ddarks_channel)
  ddarks_mask = pdb.gimp_layer_create_mask(ddarks_layer, ADD_MASK_CHANNEL)
  pdb.gimp_layer_add_mask(ddarks_layer, ddarks_mask)
  pdb.gimp_layer_set_mode(ddarks_layer, LAYER_MODE_ADDITION)
  pdb.gimp_layer_set_opacity(ddarks_layer, 50)

  pdb.gimp_layer_set_visible(darks_layer, True)


register(
  "python-fu-darkness_luminosity",
  "Luminosity masks for dark images",
  "Luminosity masks for dark images. Based on https://www.gimp.org/tutorials/Luminosity_Masks/",
  "Steve Jones", "Steve Jones", "2020",
  "Darkness Luminosity Masks",
  "RGB",
  [
    (PF_IMAGE, "image", "takes current image", None),
    (PF_DRAWABLE, "drawable", "input layer", None)
  ],
  [],
  darkness_luminosity, menu="<Image>/Filters/Light and Shadow"
  )

main()
