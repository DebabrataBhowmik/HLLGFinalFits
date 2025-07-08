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
cd CMSSW_11_3_4/src/
cmsenv 
gitclone 
cd HLLGFinalFits
source setup.sh
```
