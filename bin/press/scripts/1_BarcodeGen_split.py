#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 14:57:30 2022

@author: fpomasot
"""
from numpy import *
import pickle
import argparse
import torch
import re
import yaml
import networkx as nx
from RandomBar_Functions import chemfilter, decode, encode, seqtomer, mertobin, count_cycles, make_adjmatrix
# Step 1a: create to a set of random codewords (do just once)
# writes to 2 files: ascii acgt strings, and (with auxilliary tables) Python pickle  

parser = argparse.ArgumentParser()
parser.add_argument('--config',required=True, help='path to yaml config file')
yaml_file = parser.parse_args()

with open(yaml_file.config, "r") as fp:
    args = yaml.safe_load(fp)
#Parameters
N = args["N"] # user to set to number of codewords (this is a small value for demo purposes, 1000000 is feasible)
M = args["M"] # user to set to length of a codeword (nt)
filename_1 = args["filename_1"]#user set to output subset_1 file path (produces file length ~ M*N)
filename_2 = args["filename_2"] #user to set to output subset_2 file path
Ncos = 4 # user set to number of cosine templates (usually 4)
DoChemFilter = True # filter for homopolymer runs, AT and CG content?
homomax = args["homomax"]
gmax = int(args["gmax"]*M)
cyclemax = int(args["cyclemax"]*M)# user to set if DoChemFilter is True
N_2 = int(N*2)
# generate and write the codes
torch.set_grad_enabled(False)
if DoChemFilter :
    fac = args["fac"] # should work in all expected cases
    G = make_adjmatrix()
    Ntrial = int(fac*N_2)
    allcands = random.randint(low=0,high=4,size=(Ntrial,M))
    goodcands = array([chemfilter(x, G, homomax,gmax,cyclemax) for x in allcands], dtype=bool)
    allcodes = allcands[goodcands][:N_2] # if this or next throws an error, increase fac, but shouldn't happen
    if allcodes.shape != (N_2,M) : raise RuntimeError("see code, increase fac (this shouldn\'t happen')")
else :
    allcodes = random.randint(low=0,high=4,size=(N_2,M))

# Randomly splitting the list of barcodes
random.shuffle(allcodes)
subset_1 = allcodes[:N]
subset_2 = allcodes[N:]
#Save both lists of barcodes
with open(filename_1, 'w') as OUT:
  for code in subset_1 :        
    OUT.write(decode(code) + '\n')
print(f"wrote {N} codewords of length {M} in ascii to {filename_1}, now computing auxilliary tables")

with open(filename_2, 'w') as OUT:
  for code in subset_2 :        
    OUT.write(decode(code) + '\n')
print(f"wrote {N} codewords of length {M} in ascii to {filename_2}, now computing auxilliary tables")
# re-read codes to be sure that the pickle file matches the ascii file!
files = [filename_1, filename_2]
for filename in files:
  with open(filename) as IN: 
      codes=IN.readlines() # have \n EOL
  assert N == len(codes)
  assert M == len(codes[0][:-1])
  allseqs = []
  alltrimers = []
  allbitmaps = zeros(N, dtype=uint64)
  cosvecs = torch.zeros((Ncos,N,64),dtype=torch.float)
  coses = zeros((Ncos,M)) 
  for k in range(Ncos) :
      coses[k,:] = cos(pi*arange(M)*(k+1.)/(M-1.))
  tcoses = torch.tensor(coses, dtype=torch.float)
  for i,code in enumerate(codes) :
      seq = encode(code[:-1])
      allseqs.append(seq)
      mer = seqtomer(seq)
      mmer = torch.LongTensor(mer)
      alltrimers.append(mer)
      allbitmaps[i] = mertobin(mer)
      for k in range(Ncos):
          source = tcoses[k,arange(M-2)]
          cosvecs[k,i,:].index_add_(0,mmer,source)
  print("finished making code auxilliary tables, now pickling")        
  pickledict = {"N" : N, "M" : M, "allseqs" : allseqs,
      "alltrimers" : alltrimers, "allbitmaps" : allbitmaps, "coses" : coses, "cosvecs" : cosvecs}
  picklefilename = filename + ".pkl"
  with open(picklefilename,'wb') as OUT :
      pickle.dump(pickledict,OUT)
  print(f"finished pickling code with {N} codewords of length {M} to {picklefilename}")
