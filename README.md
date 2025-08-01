# HLLGFinalFits
FinalFits for HiggsDalitz


Log in to NCU cluster (Chip03) 
```ruby
ssh -Y dbhowmik@chip03.phy.ncu.edu.tw
```

Go to the working directory : (/home/dbhowmik/work/HiggsDalitz/HLLGFinalFits)

Install CMSSW

```ruby
cmsrel CMSSW_11_3_4
```

If cmsrel doesn't work, 

```ruby
source /cvmfs/cms.cern.ch/cmsset_default.sh
```
```ruby
cmssw-el7 --bind /data3:/data3
cd CMSSW_11_3_4/src/
cmsenv 
gitclone git@github.com:DebabrataBhowmik/HLLGFinalFits.git
cd HLLGFinalFits
source setup.sh

cd Tree2WS
python3 runTree2WS.py -s tree2ws -c config.py
python3 runTree2WS.py -s tree2ws_data -c config_data.py 
```
Go to $CMSSW_BASE (stay within singularity), and install CombinedLimit

```
cd CMSSW_11_3_4/src
cmsenv
git -c advice.detachedHead=false clone --depth 1 --branch v9.2.1 https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
scramv1 b clean; scramv1 b # always make a clean build
```
Go to background
```ruby
cd HLLGFinalFits/Background
make
```
```ruby
python3 runBackground.py
```
Go to Signal directory
```ruby
cd HLLGFinalFits/Signal

python3 runSignal.py -s calcShapeSyst
python3 runSignal.py -s calcYieldSyst

python3 runSignal.py -s signalFit
python3 runSignal.py -s makeModelPlot
```
Go to Datacard directory (to be confirmed)
```ruby
python3 makeYields.py
python3 makeDatacard.py
```


Go to Combine directory (to be confirmed)
Looks like we need to do the following :
Copy the cards directory from DataCard directory produced in the previous step
```ruby
python3 mergeCards.py
sh run_combine.sh

python3 makeLimitPlot.py
```

