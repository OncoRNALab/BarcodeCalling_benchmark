#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 15:16:20 2022

@author: fpomasot
"""
from numpy import *
import pickle
import argparse
import torch
import re
import yaml
from RandomBar_Functions import decode, encode, seqtomer, mertobin, makeerrors

 # *or* Step 1b: load code from its pickle file

parser = argparse.ArgumentParser()
parser.add_argument('--config',required=True, help='path to yaml config file')
yaml_file = parser.parse_args()

with open(yaml_file.config, "r") as fp:
        args = yaml.safe_load(fp)

filename = args["filename_1"] # user to set
picklefilename = filename + ".pkl"
with open(picklefilename,'rb') as IN :
    pickledict = pickle.load(IN)
(N, M, allseqs, alltrimers, allbitmaps, coses, cosvecs) = \
    [pickledict[x] for x in ('N', 'M', 'allseqs', 'alltrimers', 'allbitmaps', 'coses', 'cosvecs')]
print(f"loaded code with {N} codewords of length {M} from {picklefilename}.")

# PRELIMINARIES Step 2: make simulated data, write "reads" to ascii file,
# "answers (indices of true codeword)" to another file. Assumes code is loaded by Step 1a or 1b.

Q = args["Q"] # user to set to desired number of simulated reads (10000 is a small value for demo purposes)
nave = args["nave"] # user to set (average Poisson number of reads from each randomly selected codeword)
(srate,irate,drate) = (args["srate"], args["irate"], args["drate"]) #(0.04, 0.05, 0.14)user to set (these are *very* large error rates)
#(srate,irate,drate) = (0.0333, 0.0333, 0.0333) # user to set (these are large error rates)
readsfilename = args["readsfilename"]#"/user/gent/446/vsc44685/randomBar/randomcode_42K_26_sim_reads" user set to output file path
answersfilename = args["answersfilename"]#"/user/gent/446/vsc44685/randomBar/randomcode_42K_26_sim_answers" user set to output file path

q = 0
reads = []
answers = []
while q < Q :
    ansindex = random.randint(low=0, high=N)
    ans = allseqs[ansindex]
    n = min(Q-q, random.poisson(lam=nave))
    for i in range(n) :
        reads.append(makeerrors(copy(ans),srate,irate,drate))
        answers.append(ansindex)
    q += n
with open(readsfilename, 'w') as OUT:
    for seq in reads :        
        OUT.write(decode(seq) + '\n')
with open(answersfilename, 'w') as OUT:
    for ans in answers :        
        OUT.write(str(ans) + '\n')
print(f"done creating {Q} simulated reads and writing to {readsfilename} \n(answers to {answersfilename})")

