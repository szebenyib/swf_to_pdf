# swf_to_pdf

Converts swf to png while also merging png files into a single pdf.

# Installation
`pip3 -r requirements.txt`

# Usage
Copy the .py file to the folder with svg files, then:

* simply run it
`python3 swf_to_pdf.py`

* ask for help
`python3 swf_to_pdf.py --help`

* add some parameters
`python3 swf_to_pdf.py --x_size 1536 --y_size 2048`

* for cropping
`python3 swf_to_pdf.py --x_size=1536 --y_size 2048 --crop_top=140 --crop_left=200 --crop_bottom=1900 --crop_right=1436`
