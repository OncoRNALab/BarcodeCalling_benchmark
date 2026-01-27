#!/bin/bash
# Master script to submit all decoy jobs for all tools

echo "========================================="
echo "Submitting ALL DECOY JOBS"
echo "========================================="
echo ""

# RandomBarcodes
echo "--- RandomBarcodes Decoy Jobs ---"
cd randombarcodes
bash submit_decoy_jobs.sh
cd ..
echo ""

# QUIK
echo "--- QUIK Decoy Jobs ---"
cd quik
bash submit_decoy_jobs.sh
cd ..
echo ""

# Columba
echo "--- Columba Decoy Jobs ---"
cd columba
bash submit_decoy_jobs.sh
cd ..
echo ""

echo "========================================="
echo "All decoy jobs submitted successfully!"
echo "========================================="
echo ""
echo "Monitor jobs with: qstat"
echo "Check logs in:"
echo "  - randombarcodes/logs/"
echo "  - quik/logs/"
echo "  - columba/logs/"
