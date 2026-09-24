#!/usr/bin/python3

import sys
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, GLib


PLUGIN_PROC = "darkness-luminosity"


def darkness_luminosity(procedure, run_mode, image, drawables, config, run_data):
    image.undo_group_start()

    try:
        # Create a desaturated layer from the visible image.
        desat_layer = Gimp.Layer.new_from_visible(image, image, "Desat")
        image.insert_layer(desat_layer, None, 0)

        # Desaturate the new layer using luminosity.
        desat_layer.desaturate(Gimp.DesaturateMode.LUMINANCE)

        # Create a grayscale channel from the luminosity component.
        lights_channel = Gimp.Channel.new_from_component(
            image,
            Gimp.ChannelType.GRAY,
            "L"
        )
        image.insert_channel(lights_channel, None, 0)

        # Start with a full-image selection.
        Gimp.Selection.all(image)

        # Subtract the luminosity channel: this produces the D mask.
        image.select_item(
            Gimp.ChannelOps.SUBTRACT,
            lights_channel
        )
        darks_channel = Gimp.Selection.save(image)
        darks_channel.set_name("D")

        # Subtract it again: this produces the DD mask.
        image.select_item(
            Gimp.ChannelOps.SUBTRACT,
            lights_channel
        )
        ddarks_channel = Gimp.Selection.save(image)
        ddarks_channel.set_name("DD")

        # Clear the selection and hide the temporary layer.
        Gimp.Selection.none(image)
        desat_layer.set_visible(False)

        # Create the D layer.
        darks_layer = Gimp.Layer.new_from_visible(image, image, "D")
        image.insert_layer(darks_layer, None, 0)

        # Use the D channel as the layer mask.
        image.set_selected_channels([darks_channel])
        darks_mask = darks_layer.create_mask(Gimp.AddMaskType.CHANNEL)
        darks_layer.add_mask(darks_mask)

        darks_layer.set_mode(Gimp.LayerMode.ADDITION)
        darks_layer.set_opacity(50.0)
        darks_layer.set_visible(False)

        # Create the DD layer.
        ddarks_layer = Gimp.Layer.new_from_visible(image, image, "DD")
        image.insert_layer(ddarks_layer, None, 0)

        # Use the DD channel as the layer mask.
        image.set_selected_channels([ddarks_channel])
        ddarks_mask = ddarks_layer.create_mask(Gimp.AddMaskType.CHANNEL)
        ddarks_layer.add_mask(ddarks_mask)

        ddarks_layer.set_mode(Gimp.LayerMode.ADDITION)
        ddarks_layer.set_opacity(50.0)

        # Match the original script: show D, leave DD visible.
        darks_layer.set_visible(True)

        Gimp.Selection.none(image)
        image.undo_group_end()

        return procedure.new_return_values(
            Gimp.PDBStatusType.SUCCESS,
            GLib.Error()
        )

    except Exception as error:
        image.undo_group_end()
        Gimp.message(f"Darkness Luminosity failed: {error}")

        return procedure.new_return_values(
            Gimp.PDBStatusType.EXECUTION_ERROR,
            GLib.Error()
        )


class DarknessLuminosityPlugin(Gimp.PlugIn):

    def do_query_procedures(self):
        return [PLUGIN_PROC]

    def do_set_i18n(self, name):
        return False

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            darkness_luminosity,
            None
        )

        procedure.set_image_types("*")
        procedure.set_menu_label("Darkness Luminosity Masks")
        procedure.add_menu_path("<Image>/Filters/Light and Shadow")

        procedure.set_documentation(
            "Luminosity masks for dark images",
            "Creates D and DD luminosity-mask layers for dark images.",
            name
        )

        procedure.set_attribution(
            "Steve Jones",
            "Steve Jones",
            "2026"
        )

        return procedure


Gimp.main(DarknessLuminosityPlugin.__gtype__, sys.argv)
