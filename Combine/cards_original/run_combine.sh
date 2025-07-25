# cd cards

# for mass in $(seq 120 1 130); do
#     echo "Create workspace for mass @"${mass} "GeV"
#     text2workspace.py datacard_hmmg_runII_comb_${mass}.txt -o datacard_hmmg_runII_comb_${mass}.root -m ${mass} -v 1
#     echo "---------------------------------------"
# done 


for mass in $(seq 120 1 130); do
    echo "Expected limit for mass @"${mass} "GeV"
    combine datacard_hmmg_runII_comb_${mass}.txt -M AsymptoticLimits -n _comb_${mass} -m ${mass} --run=blind 
    echo "---------------------------------------"
done 

# cd ../

# limit
# for mass in $(seq 120 1 130); do
#     echo "============================================="
#     echo "Expected limit for mass @"${mass} "GeV"
#     combine datacard_hmmg_runII_comb_${mass}.txt -M AsymptoticLimits -n _comb_${mass} -m ${mass} --run=blind --noFitAsimov
#     echo "============================================="
# done --cminDefaultMinimizerStrategy 0 

for mass in $(seq 120 1 130); do
    combine -M GenerateOnly datacard_hmmg_runII_comb_${mass}.txt -t -1 --saveToys --expectSignal=1 --expectSignalMass=${mass} -m ${mass}
done 

for mass in $(seq 120 1 130); do
    echo "============================================="
    echo "Expected significance for mass @"${mass} "GeV"
    combine datacard_hmmg_runII_comb_${mass}.txt -M Significance -n _comb_${mass}_expSignal1 -m ${mass} -t -1 --toysFile higgsCombineTest.GenerateOnly.mH${mass}.123456.root -v 1
    combine datacard_hmmg_runII_comb_${mass}.txt -M Significance -n _comb_${mass}_expectSignalMass125 -m ${mass} -t -1 --toysFile higgsCombineTest.GenerateOnly.mH125.123456.root -v 1 
    echo "============================================="
done 