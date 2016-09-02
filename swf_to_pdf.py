# Argument reading
import argparse
# Time measurement
import time
# SWF reading
from pathlib import Path
from subprocess import call
# PDF export from PNGs
from fpdf import FPDF


"""
 Converts multiple swf files to images and then to a pdf.
 Requires: swfrender (operating system level) - swf to image conversion
           FPDF - image to pdf conversion
"""


def swf_to_images(image_suffix,
                  x_size,
                  y_size,
                  source_suffix="swf",
                  verbose=True):
    """
    Converts multiple swf files into multiple images
    :type source_suffix: 'swf',
          image_suffix: str, e.g. 'png', and supported types by swfrender
          x_size: size in pixels,
          y_size: size in pixels,
          verbose: print execution information
    """
    time_function_start = time.time()
    if verbose:
        print("\n* Generating images *")

    paths = [path for path in Path.cwd().iterdir()
             if path.suffix == ("." + source_suffix)]
    number_of_paths = len(paths)
    if number_of_paths:
        counter = 1

        for path in paths:
            time_iteration_start = time.time()
            result = call(["swfrender", path.name,
                           "-X", str(x_size),
                           "-Y", str(y_size),
                           "-o", path.name[:-3] + image_suffix])
            if verbose:
                time_current = time.time()
                if result == 0:
                    msg = ("{:04d}/{:04d}: {}png created. " +
                          "{:03.1f}s {:6d}m").format(number_of_paths,
                                                     counter,
                                                     path.name[:-3],
                                                     (time_current - time_iteration_start),
                                                     int((time_current - time_function_start) / 60))
                else:
                    msg = ("{:04d}/{:04d}: {}png could not be created. " + \
                          "{:03.1f}s {:6d}m").format(number_of_paths,
                                                     counter,
                                                     path.name[:-3],
                                                     (time_current - time_iteration_start),
                                                     int((time_current - time_function_start) / 60))
                counter += 1
                print(msg)
    else:
        if verbose:
            print("No " + source_suffix + " files were found.")


def images_to_pdf(image_suffix: str,
                  x_size,
                  y_size,
                  verbose=True):
    """
    Converts images supported by the FPDF library into a single pdf.
    :type image_suffix: str, e.g. 'png'
          x_size: size in pixels,
          y_size: size in pixels,
          verbose: print execution information
    :return fpdf object
    """
    time_function_start = time.time()
    if verbose:
        print("\n* Generating pdf from images *")

    imagepaths = [path for path in Path.cwd().iterdir()
                  if path.suffix == ("." + image_suffix)]
    number_of_paths = len(imagepaths)
    if number_of_paths:
        counter = 1
        pdf = FPDF(unit="pt",
                   format=[int(x_size), int(y_size)])

        for imagepath in imagepaths:
            time_iteration_start = time.time()
            pdf.add_page()
            pdf.image(imagepath.name, 0, 0)
            if verbose:
                time_current = time.time()
                print(str(counter) + "/" + str(number_of_paths) + ":" + imagepath.name +
                      " {:19.1f}s".format(int(time_current - time_iteration_start)) +
                      " {:6d}m".format(int((time_current - time_function_start) / 60)))
                counter += 1
    else:
        if verbose:
            print("No images were found.")
        pdf = None
    return pdf


def pdf_export_to_disk(pdf: FPDF):
    """
    Saves an FPDF object to the current working directory,
    named after the current directory.
    :type pdf: FPDF
    """
    if pdf:
        pdf_filename = Path.cwd().parts[-1] + ".pdf"
        pdf.output(pdf_filename, dest="F")
    else:
        pass


def parse_args():
    """
    Adds possible command line arguments.
    :return: parsed arguments by ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",
                        help="1 - Images generation, 2 - PDF from existing images, 3 - Images and PDF",
                        type=int)
    parser.add_argument("--x_size",
                        help="X size of images and pdf in pixels",
                        type=int)
    parser.add_argument("--y_size",
                        help="Y size of images and pdf in pixels",
                        type=int)
    parser.add_argument("--image_format",
                        help="png|jpeg")
    args = parser.parse_args()
    return args


def process_with_args(args,
                      default_x_size,
                      default_y_size,
                      default_image_suffix):
    """
    Calls the processing functions with the parsed and default arguments, if parsed
    arguments are missing.
    :type args: arguments parsed by ArgumentParser
          default_x_size: default size to use if none is parsed
          default_y_size: default size to use if none is parsed
          default_image_suffix: default suffix to use if none is parsed
    """
    if args.x_size:
        x_size = args.x_size
    else:
        x_size = default_x_size
    if args.y_size:
        y_size = args.y_size
    else:
        y_size = default_y_size
    if args.image_format:
        print("Due to swftools currently only supporting png, image format is reset to png.")
        #image_suffix = args.image_format
        image_suffix = default_image_suffix
    else:
        image_suffix = default_image_suffix

    if args.mode:
        if args.mode == 1:
            swf_to_images(image_suffix=image_suffix,
                          source_suffix=source_suffix,
                          x_size=x_size,
                          y_size=y_size)
        elif args.mode == 2:
            pdf = images_to_pdf(image_suffix=image_suffix,
                                x_size=x_size,
                                y_size=y_size)
            pdf_export_to_disk(pdf=pdf)
        elif args.mode == 3:
            swf_to_images(image_suffix=image_suffix,
                          source_suffix=source_suffix,
                          x_size=x_size,
                          y_size=y_size)
            pdf = images_to_pdf(image_suffix=image_suffix,
                                x_size=x_size,
                                y_size=y_size)
            pdf_export_to_disk(pdf=pdf)
        else:
            pass
    else:
        swf_to_images(image_suffix=image_suffix,
                      source_suffix=source_suffix,
                      x_size=x_size,
                      y_size=y_size)
        pdf = images_to_pdf(image_suffix=image_suffix,
                            x_size=x_size,
                            y_size=y_size)
        pdf_export_to_disk(pdf=pdf)


if __name__ == "__main__":
    source_suffix = "swf"
    default_image_suffix = "png"
    default_x_size = 2480
    default_y_size = 3508

    args = parse_args()
    if args:
        process_with_args(args,
                          default_x_size=default_x_size,
                          default_y_size=default_y_size,
                          default_image_suffix=default_image_suffix)
    else:
        swf_to_images(image_suffix=default_image_suffix,
                      source_suffix=source_suffix,
                      x_size=default_x_size,
                      y_size=default_y_size)
        pdf = images_to_pdf(image_suffix=image_suffix,
                            x_size=default_x_size,
                            y_size=default_y_size)
        pdf_export_to_disk(pdf=pdf)
