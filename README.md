# HLLGFinalFits
FinalFits for HiggsDalitz


Log in to Chip03 (ssh -Y dbhowmik@chip03.phy.ncu.edu.tw)

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
