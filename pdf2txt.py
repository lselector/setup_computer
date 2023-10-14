
"""
# pdf2txt.py
# script goes recursively through directory and subdirectories
# and extracts text from all PDF files
# and saves to a text file 
# It looks either in current directory
# or in directories provided on command line (space-separaed)
#
# This script uses binary "pdftotext"
# You can install it on Mac using brew.
# First install poppler - a PDF rendering libary
#     brew install poppler 
# This adds this executable:
#     /usr/local/bin/pdftotext@ -> ../Cellar/poppler/21.03.0_1/bin/pdftotext
# So now you can use it from cmd prompt:
#     pdftotext --help
#
# To use from Python, install wrapper:
#     pip install xpdf_python
#
# Then:
#     import xpdf_python
#     txt_arr = xpdf_python.to_text("myfile.pdf")
#     for txt in txt_arr:
#         print(txt)
#
# Example of usage:
# in ml_ai_doc directory:
#     python pdf2txt.py
# in other directory:
#     python  ../setup_computer/pdf2txt.py ./
#
"""
# --------------------------------------------------------------
import os, sys, glob
import datetime as dt
from pathlib import Path
import xpdf_python

# --------------------------------------------------------------
def print_date_time():
    print (dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

print_date_time()

# --------------------------------------------------------------
if len(sys.argv) <= 1:
    mypath = os.path.dirname(os.path.realpath(__file__))
    mydirs = [mypath]
    print("looking for pdf files in script directory: ", mypath)
else:
    mydirs = []
    for argpath in sys.argv[1:]:
        if not os.path.isdir(argpath):
            print(f"{argpath} is not a directory, exiting ...")
            sys.exit()
        mypath = os.path.realpath(argpath)
        print(argpath, "   =>  ", mypath)
        mydirs += [mypath]

# --------------------------------------------------------------
for dir_path in mydirs:
    print_date_time()
    print(dir_path)
    basedir = dir_path.split("/")[-1]
    fname_out = dir_path + "/" + basedir+"_pdf.txt"

    # get paths recursively 
    myfiles = list(Path(dir_path).rglob("*.[pP][dD][fF]"))

    # convert from posix path to string
    myfiles = [str(x) for x in myfiles]

    counter = 0
    ss = ""

    for myfile in sorted(myfiles):
        if "~$" in myfile:
            continue
        if "OLD/" in myfile:
            continue
        counter += 1
        if counter > 3:
            pass # break
        print_date_time()
        print("-"*20, myfile)
        myfile_short = myfile.split(dir_path)[1][1:]
        # print(myfile_short,"\n")
        # print("----------------------")
        txt = xpdf_python.to_text(myfile)[0]
        txt_arr = txt.strip().split("\n")
        txt_arr = [x.strip() for x in txt_arr]
        txt_arr = [x.replace("\r"," ") for x in txt_arr]
        txt_arr = [myfile_short+" : " + x + "\n" for x in txt_arr]
        txt = "".join(txt_arr)
        ss += txt
        print(txt)

    print("----------------------")
    print("writing to file ", fname_out)
    fh = open(fname_out, "w")
    fh.write(ss)
    fh.close()
    print_date_time()
    print("----------------------")
