"""LHH Wayfiding Sign generator.

Takes a SVG template file and a CSV with trail sign descriptions.
Generates an SVG per trail sign.

SVG File should have arrows with labels like #ArrowLeft , hidden.
This tool will unhide the arrows indiciated.

CSV file must have headers with columns SignID, TrailName, Arrow
Arrow must match... whatever labels are used in the SVG template.
E.g. ArrowLeft, ArrowRight in template -> Left, Right in CSV.

Todo: Document the exact format.s!
Todo: Use Inkscape to generate the PDF files.
inkscape.exe INPUT.SVG --export-area-drawing  \
 --export-type=pdf  --export-filename=OUTPUT.pdf --batch-process 

Matthew Blain, 04jun2021
"""

import csv
import sys
import xml.etree.ElementTree as ET


def generate_files(template_filename, csv_data, output_base):
    seen_ids = set()
    svg_filenames = []
    for sign_info in csv_data:
        if sign_info["SignID"] in seen_ids:
            raise Exception("Sign ID seen more than once: " + sign_info["SignID"])
        tree = fill_template(template_filename, sign_info)
        sign_filename = output_base + sign_info["SignID"] + ".svg"
        tree.write(sign_filename)
        svg_filenames.append(sign_filename)
    return svg_filenames


def update_text_with_label(root, label, text):
    # Text is assumed to be a text node. If it's a flowRoot, use Text: Convert to Text in Inkscape.
    # Also make sure it has a single tspan child.
    xpath = (
        ".//{http://www.w3.org/2000/svg}text"
        "[@{http://www.inkscape.org/namespaces/inkscape}label='%s']" % label
    )
    trail_name_nodes = root.findall(xpath)
    for n in trail_name_nodes:
        # Assume a single child node, tspan.
        tspan = n[0]
        assert tspan.tag == "{http://www.w3.org/2000/svg}tspan"
        tspan.text = text


def fill_template(template_filename, sign_info):
    tree = ET.parse(template_filename)
    root = tree.getroot()
    update_text_with_label(root, "#TrailName", sign_info["TrailName"])
    update_text_with_label(root, "#SignInfo", sign_info["SignID"])

    # We will assume that every arrow is labeled with an appropriate label then hidden.
    # You can use object: unhide all to show them!
    arrowLabel = f'#Arrow{sign_info["Arrow"]}'

    arrow_nodes = root.findall(
        ".//{http://www.w3.org/2000/svg}g"
        "[@{http://www.inkscape.org/namespaces/inkscape}label='%s']" % arrowLabel
    )
    for n in arrow_nodes:
        if "style" in n.attrib:
            del n.attrib["style"]

    return tree


def template_to_svg(template_filename, csv_filename, output_path_base):
    with open(csv_filename, "r") as r:
        csv_data = csv.DictReader(r)
        svg_filenames = generate_files(template_filename, csv_data, output_path_base)
        return svg_filenames


def main(argv):
    svg_filenames = template_to_svg(argv[1], argv[2], argv[3])
    # Really crude 'ok here's how to generate pdfs' technique: print out the
    # command to do it. TODO: Actually call inkscape!
    for svg in svg_filenames:
        pdf = svg[:-3] + "pdf"
        print(
            "inkscape.exe  --export-area-drawing  --export-type=pdf  --batch-process  %s  --export-filename=%s"
            % (svg, pdf)
        )


if __name__ == "__main__":
    main(sys.argv)
