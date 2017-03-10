# Argument reading
import argparse
# Time measurement
import time
# Path sorting
from functools import cmp_to_key
# SVG reading
import cairosvg
from PIL import Image
from io import BytesIO
# SWF reading
from pathlib import Path
from subprocess import call
# PDF export from PNGs
from fpdf import FPDF


def convert_transparency_to_color(png_bytes_file,
                                  background_color):
    """
    Removing transparency from PNG files for a faster pdf conversion

    Source: http://stackoverflow.com/questions/9166400/convert-rgba-png-to-rgb-with-pil
    Source: http://stackoverflow.com/a/9459208/284318

    :type png_bytes_file -- PIL RGBA Image object
          background_color -- Tuple r, g, b (default 255, 255, 255 = white)
    """
    png_file = Image.open(BytesIO(png_bytes_file))
    png_file.load()  # needed for split()
    image_without_alpha = Image.new('RGB',
                                    png_file.size,
                                    background_color)
    image_without_alpha.paste(png_file,
                              mask=png_file.split()[3])  # 3 is the alpha channel
    return image_without_alpha


def path_sorter(a, b):
    """
    Sorting paths to fix default sort order. This function
    first respects the length and then the values to fix the order.
    :return: -1 is a < b, 0 if a == b, 1 if a > b
    :type: a PosixPath
           b PosixPath
    """
    if len(a.stem) < len(b.stem):
        return -1
    elif len(a.stem) > len(b.stem):
        return 1
    elif len(a.stem) == len(b.stem):
        if a.stem < b.stem:
            return -1
        elif a.stem > b.stem:
            return 1
        else:
            return 0


def raw_to_images(image_suffix,
                  x_size,
                  y_size,
                  source_suffix,
                  background_color,
                  verbose=True):
    """
    Converts multiple swf files into multiple images
    :type source_suffix: 'swf', or 'svg'
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
    paths.sort(key=cmp_to_key(path_sorter))
    number_of_paths = len(paths)
    if number_of_paths:
        counter = 1

        for path in paths:
            time_iteration_start = time.time()
            result = 0
            if source_suffix == "svg":
                try:
                    png_file = cairosvg.svg2png(url=str(path),
                                                parent_height=y_size,  # 1682
                                                parent_width=x_size)   # 1190
                    png_file = convert_transparency_to_color(png_bytes_file=png_file,
                                                             background_color=background_color)
                    filename = str(path)[:-3] + image_suffix
                    png_file.save(fp=filename)

                    result = 0
                except Exception as e:
                    print(str(e))
                    result = 1
            elif source_suffix == "swf":
                result = call(["swfrender", path.name,
                               "-X", str(x_size),
                               "-Y", str(y_size),
                               "-o", path.name[:-3] + image_suffix])
            if verbose:
                time_current = time.time()
                if result == 0:
                    msg = ("{:04d}/{:04d}: {}{} created. " +
                          "{:03.1f}s {:6d}m").format(number_of_paths,
                                                     counter,
                                                     path.name[:-3],
                                                     image_suffix,
                                                     (time_current - time_iteration_start),
                                                     int((time_current - time_function_start) / 60))
                else:
                    msg = ("{:04d}/{:04d}: {}{} could not be created. " +
                          "{:03.1f}s {:6d}m").format(number_of_paths,
                                                     counter,
                                                     path.name[:-3],
                                                     image_suffix,
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
    imagepaths.sort(key=cmp_to_key(path_sorter))
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
                        help="1 - Generate images only, 2 - Generate PDF from existing images,"
                             "3 - Generate images and PDF",
                        type=int)
    parser.add_argument("--x_size",
                        help="X size of images and pdf in pixels",
                        type=int)
    parser.add_argument("--y_size",
                        help="Y size of images and pdf in pixels",
                        type=int)
    parser.add_argument("--image_format",
                        help="png|jpeg")
    parser.add_argument("--source_format",
                        help="swf|svg")
    parser.add_argument("--background_color",
                        help="255.255.255")
    args = parser.parse_args()
    return args


def process_with_args(args,
                      default_x_size,
                      default_y_size,
                      default_source_suffix,
                      default_image_suffix,
                      default_background_color):
    """
    Calls the processing functions with the parsed and default arguments, if parsed
    arguments are missing.
    :type args: arguments parsed by ArgumentParser
          default_x_size: default size to use if none is parsed
          default_y_size: default size to use if none is parsed
          default_source_suffix: default suffix to use if none is parsed
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
        image_suffix = default_image_suffix
    else:
        image_suffix = default_image_suffix
    if args.source_format:
        if args.source_format in ("swf", "svg"):
            source_suffix = args.source_format
        else:
            print("Only swf or svg is supported, trying {} as default.".format(default_source_suffix))
            source_suffix = default_source_suffix
    else:
        source_suffix = default_source_suffix
    if args.background_color:
        background_color = tuple(args.background_color.split("."))
    else:
        background_color = default_background_color

    if args.mode:
        if args.mode == 1:
            raw_to_images(image_suffix=image_suffix,
                          source_suffix=source_suffix,
                          x_size=x_size,
                          y_size=y_size,
                          background_color=background_color)
        elif args.mode == 2:
            pdf = images_to_pdf(image_suffix=image_suffix,
                                x_size=x_size,
                                y_size=y_size)
            pdf_export_to_disk(pdf=pdf)
        elif args.mode == 3:
            raw_to_images(image_suffix=image_suffix,
                          source_suffix=source_suffix,
                          x_size=x_size,
                          y_size=y_size,
                          background_color=background_color)
            pdf = images_to_pdf(image_suffix=image_suffix,
                                x_size=x_size,
                                y_size=y_size)
            pdf_export_to_disk(pdf=pdf)
        else:
            pass
    else:
        raw_to_images(image_suffix=image_suffix,
                      source_suffix=source_suffix,
                      x_size=x_size,
                      y_size=y_size,
                      background_color=background_color)
        pdf = images_to_pdf(image_suffix=image_suffix,
                            x_size=x_size,
                            y_size=y_size)
        pdf_export_to_disk(pdf=pdf)


if __name__ == "__main__":
    default_source_suffix = "svg"
    default_image_suffix = "png"
    default_x_size = 2480
    default_y_size = 3508
    default_background_color = (255, 255, 255)

    args = parse_args()
    if args:
        process_with_args(args,
                          default_x_size=default_x_size,
                          default_y_size=default_y_size,
                          default_image_suffix=default_image_suffix,
                          default_source_suffix=default_source_suffix,
                          default_background_color=default_background_color)
    else:
        raw_to_images(image_suffix=default_image_suffix,
                      source_suffix=default_source_suffix,
                      x_size=default_x_size,
                      y_size=default_y_size,
                      background_color=default_background_color)
        pdf = images_to_pdf(image_suffix=default_image_suffix,
                            x_size=default_x_size,
                            y_size=default_y_size)
        pdf_export_to_disk(pdf=pdf)
