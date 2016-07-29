#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse

from traducteurAF_to_LogAF import TraductionAFLog

if __name__ == "__main__":
    text = """This process translates an SBGN-AF graph given in the 
    input file, in an SBGNLog-AF graph. This graph is stocked in an 
    text file (.txt)"""
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument("input_file", help="""name of the input file.
    Must end by .sbgn""")
    parser.add_argument("-o", "--output_file", help="""name of the output
    file.""")
    args = parser.parse_args()
    if args.output_file:
        fout = args.output_file
    else:
        fout = args.input_file[:args.input_file.find('.')] + '.txt'
    trad = TraductionAFLog(args.input_file, fout)
    trad.traduire()
