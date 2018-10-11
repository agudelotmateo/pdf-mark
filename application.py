import subprocess
import random
import string
import ntpath
import time
import os

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route("/")
def form():
    return render_template("index.html")


@app.route("/remove", methods=["POST"])
def remove_watermark():
    # Get the input file
    file = request.files["data_file"]
    if not file:
        return ("No file was uploaded", 400)
    # Get the watermark text
    text = request.form.get("watermark")
    if not text:
        return ("No watermark text was provided", 400)

    # Appends a random string of length 10 and the current timestamp to the given string.
    # Used to create a unique folder in the file system.
    def randomName(s):

        timeStamp = "".join(time.strftime("%c").replace(":", "").split())
        randStr = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
        return f"{s}{timeStamp}{randStr}"

    # Create a name for a temporary folder that is not currently in use
    valid = False
    while not valid:
        tmpFolder = randomName("tmp")
        if not os.path.isdir(tmpFolder):
            valid = True

    # Create the temporary folder to hold all the temporary files
    params = ["mkdir", tmpFolder]
    if subprocess.call(params) != 0:
        return("Failed to create the temporary folder", 500)

    # Store the input file locally
    infile = f"{tmpFolder}/i.pdf"
    file.save(infile)

    # Define the temporary file paths
    uncompressed = f"{tmpFolder}/u.pdf"
    modified = f"{tmpFolder}/m.pdf"
    recompressed = f"{tmpFolder}/r.pdf"

    # Uncompress the PDF file using PDFtk
    params = ["pdftk", infile, "output", uncompressed, "uncompress"]
    if subprocess.call(params) != 0:
        return("Failed to uncompress the PDF", 500)

    # Replace the input text with nothing, effectively removing it
    params = ["sed", "-e", f"s/{text}//g", uncompressed]
    if subprocess.call(params, stdout=open(modified, "w")) != 0:
        return("Failed to remove the watermark text from the PDF", 500)

    # Compress the modified PDF file using PDFtk
    params = ["pdftk", modified, "output", recompressed, "compress"]
    if subprocess.call(params) != 0:
        return("Failed to compress the modified PDF", 500)

    # Gets the file name without extension from its path
    def getName(s):
        base = ntpath.basename(s)
        index = base.rfind(".")
        if index == -1:
            return base
        return base[:index]

    # Return the output file
    try:
        filename = f"{getName(secure_filename(file.filename))}_clean.pdf"
        response = send_file(recompressed, as_attachment=True, attachment_filename=filename)
        # Remove the temporary folder. Do nothing on failure.
        params = ["rm", "-rf", tmpFolder]
        subprocess.call(params)
        return response
    except:
        return("Failed to return the output file", 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ["PORT"])
