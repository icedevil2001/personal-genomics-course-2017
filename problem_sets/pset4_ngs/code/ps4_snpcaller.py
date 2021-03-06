#!/usr/bin/env python

"""
CSE291 SNP calling execise - problem set 4

Usage:
cat pileup | ./ps4_snpcaller.py - snpcalls.tab

or

./ps4_snpcaller.py <pileup> <outfile>
"""

import numpy as np
import sys

try:
    infile = sys.argv[1]
    outfile = sys.argv[2]
except:
    sys.stderr.write(__doc__)
    sys.exit(1)

if infile == "-":
    inF = sys.stdin
else: inF = open(infile, "r")
outF = open(outfile, "w")

PROB_ERROR = 0.02 # Assume probability of a sequencing error. You may want to tweak this

def GetSnpCall(ref, bases):
    """
    Inputs:
      ref (string): character representing the reference allele
      bases (string): string of characters from the samtools pileup representing observed bases

    Outputs:
      [genotype1, genotype2]: 2 element list with the inferred genotype. e.g. ["A", "G"]
      score (float): score indicating confidence in the returned snp call
      alt (string): character representing the alternate (non-reference) allele
      afreq (float): frequency of the alternate allele
    """
    basecounts = {ref: 0}
    for i in range(len(bases)):
        b = bases[i].upper()
        if bases[i] == "." or bases[i] == ",":
            basecounts[ref] += 1
        elif b in ["A","C","G","T"]:
            basecounts[b] = basecounts.get(b, 0) + 1
        else:
            continue
    if len(basecounts.keys()) > 2:
        return [-1, -1], -1, "N", -1
    if len(basecounts.keys()) == 1:
        alt = "."
        basecounts[alt] = 0
    else:
        alt = [item for item in basecounts.keys() if item != ref][0]
    refcount = basecounts[ref]
    altcount = sum(basecounts.values()) - refcount
    if refcount + altcount == 0: return [-1, -1], -1, "N", -1
    afreq = altcount*1.0/(refcount+altcount)
    ##########################
    # FILL THIS PART IN!
    score = 0
    genotype1 = ref
    genotype2 = ref
    ##########################
    # MGYMREK answer
    # Calculate probabilities
    p_ref_given_AA = 1-PROB_ERROR
    p_alt_given_AA = PROB_ERROR
    p_ref_given_BB = PROB_ERROR
    p_alt_given_BB = 1-PROB_ERROR
    p_ref_given_AB = 0.5*p_ref_given_AA + 0.5*p_ref_given_BB
    p_alt_given_AB = 0.5*p_alt_given_AA + 0.5*p_alt_given_BB
    log_pAA = basecounts[ref]*np.log(p_ref_given_AA) + basecounts[alt]*np.log(p_alt_given_AA)
    log_pAB = basecounts[ref]*np.log(p_ref_given_AB) + basecounts[alt]*np.log(p_alt_given_AB)
    log_pBB = basecounts[ref]*np.log(p_ref_given_BB) + basecounts[alt]*np.log(p_alt_given_BB)
    # Get max score and genotype
    genotypes = [(ref, ref), (ref, alt), (alt, alt)]
    scores = [log_pAA, log_pAB, log_pBB]
    genotype1, genotype2 = genotypes[scores.index(max(scores))]
    best_score = max(scores)
    score = -1*np.log10((1-np.exp(best_score)/np.sum(np.exp(scores))))
    ##########################
    return [genotype1, genotype2], score, alt, afreq

# Output header
outF = open(outfile, "w")
outF.write("\t".join(["chrom", "pos", "ref", "alt", "coverage", "score", "afreq", "gt1", "gt2"])+"\n")
line = inF.readline()
while line != "":
    if len(line.strip().split()) < 5:  # 0 coverage
        line = inF.readline()
        continue
    chrom, pos, ref, coverage, bases = line.strip().split()[0:5]
    gt, score, alt, afreq = GetSnpCall(ref, bases)
    if score == -1:
        line = inF.readline()
        continue
    outF.write("\t".join(map(str, [chrom, pos, ref, alt, coverage, score, afreq]+gt))+"\n")
    outF.flush()
    line = inF.readline()
