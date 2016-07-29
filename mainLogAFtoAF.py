#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse

from traducteurLogAF_to_AF import TraductionAF

if __name__ == "__main__":
    text = """This process translates an SBGNLog-AF graph given in the 
    input file, in an SBGN-AF graph. This graph is stocked in an 
    XML file (.sbgn)"""
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument("input_file", help="name of the input file")
    parser.add_argument("-o", "--output_file", help="name of the output \
    file. Must end by .sbgn")
    args = parser.parse_args()
    if args.output_file:
        if '.sbgn' in args.output_file:
            fout = args.output_file
        else:
            fout = args.input_file[:args.input_file.find('.')] + '.sbgn'
            print "The output file must end by .sbgn \n \
            Your results have been saved in the file 'input_file'.sbgn."
    else:
        fout = args.input_file[:args.input_file.find('.')] + '.sbgn'
    trad = TraductionAF(args.input_file, fout)
    trad.translation()
