# Script to convert HDalitz trees to RooWorkspace (compatible for finalFits)
# Assumes tree names of the format:
#  * miniTree
# For systematics: requires hist of the format or trees of the format:
#  * cat1_<syst> e.g. cat1_JERUp, cat1_PhoScaleStatDo
#  * miniTree_<syst> e.g. miniTree_JERUp, miniTree_PhoScaleStatDo


import ROOT
import os
import re
import pandas as pd
import uproot as up
import uproot4 as up4
import numpy as np
from pprint import pprint
from argparse import ArgumentParser
from collections import OrderedDict as od
from importlib import import_module
from commonObjects import inputWSName__, category__, productionModes
from commonTools import cprint

def get_parser():
    parser = ArgumentParser(description="Script to convert data trees to RooWorkspace (compatible for finalFits)")
    parser.add_argument("-c",  "--config",          help="Input config: specify list of variables/analysis categories", default=None, type=str)
    parser.add_argument("-y",  "--year",            help="Year",                                                        default=2017, type=int)
    parser.add_argument("-m",  "--mass",            help="mass point",                                                  default=125,  type=int)
    parser.add_argument("-p",  "--productionMode",  help="Production mode [ggH, VBF, WH, ZH, ttH, bbH]",                default="ggH",type=str)
    parser.add_argument("-ds", "--doSystematics",   help="Add systematics datasets to output WS",                       default=True,action="store_true")
    parser.add_argument("-uh", "--useSystHist",     help="load the systematic histograms else minitrees",               default=False,action="store_true")
    parser.add_argument("-v",  "--verbose",         help="verbose message",                                             default=False,action="store_true")
    parser.add_argument("-pn", "--preventNegative", help="set the negative bin content of mass histograms to 0.",       default=False,action="store_true")
    return parser


def main():
    cprint("[INFO] Read file:", colorStr="green")
    print(inputTreeFile)
    
    files_with_tree = []
    for f in inputTreeFile: 
        files_with_tree.append(f + ":" + inputTreeName)
    
    # create work space
    ws_dir_name = inputWSName__.split("/")
    ws = ROOT.RooWorkspace(ws_dir_name[1], ws_dir_name[1])
    
    # create variables
    CMS_higgs_mass = ROOT.RooRealVar("CMS_higgs_mass", "CMS_higgs_mass", mass, 110, 170, "GeV") # initial, lower bound, upper bound
    weight = ROOT.RooRealVar("weight", "weight", -100, 100, "")
    ws.Import(CMS_higgs_mass)
    ws.Import(weight)
    
    # convert tree to dataset 
    for cat_name, cat_cut in category__.items():
        if year != 2017 and "IsoMu" in cat_name:
            continue
        
        # hadd fails to merge tree with different branches, so I use uproot to convert the common branches to array
        incolumns = ["CMS_higgs_mass", "weight", "category"]
        if doSystematics:
            incolumns = incolumns + sysWeis
        arr = up4.concatenate(files_with_tree, incolumns, library="np", cut=cat_cut)
        # nominal dataset
        aset = ROOT.RooArgSet(CMS_higgs_mass, weight)
        dname = f"set_{mass}_{cat_name}"
        dset = ROOT.RooDataSet(dname, dname, aset, ROOT.RooFit.WeightVar("weight"))
        
        # Loop over events in tree and add to dataset with weight 1
        for i in range(len(arr["CMS_higgs_mass"])):
            weight.setVal(arr["weight"][i])
            CMS_higgs_mass.setVal(arr["CMS_higgs_mass"][i])
            dset.add(aset, arr["weight"][i])
        ws.Import(dset)
        if (args.verbose):
            cprint("     - dataset entries: {}".format(dset.sumEntries()))

        if doSystematics:
            for sw in sysWeis: # affect rate 
                hname = f"hist_{mass}_{cat_name}_{sw}"
                dhname = f"dh_{mass}_{cat_name}_{sw}"
                hist_sys = ROOT.TH1F(hname, hname, 60, 110, 170)
                for i in range(len(arr["CMS_higgs_mass"])):
                    hist_sys.Fill(arr["CMS_higgs_mass"][i], arr[sw][i])
                if args.preventNegative: # set the negative bin content to 0.
                    for b in range(hist_sys.GetNbinsX()+1): 
                        if hist_sys.GetBinContent(b+1) < 0:
                            hist_sys.SetBinContent(b+1, 0)
                dh = ROOT.RooDataHist(dhname, dhname, CMS_higgs_mass, ROOT.RooFit.Import(hist_sys))
                ws.Import(dh)
                if (args.verbose):
                    cprint("     - datahist entries: {}".format(dh.sumEntries()))
                hist_sys.Delete()
                
            if args.useSystHist: # for electron channel analysis
                for sh in sysHists: # affect shape 
                    cat_prefix = cat_cut.replace("category == ", "cat") #! FIXEDME: better way to extract the hist?   
                    if ("Merged" in cat_name) and ("EleScale" not in sh) and ("EleSigma" not in sh):
                        sysFileNames = [sf for sf in inputTreeFile if "merged" in sf]
                        hist_sys = ROOT.TH1F(f"{cat_prefix}_{sh}", "", 60, 110, 170)
                        for fn in sysFileNames:
                            infile = ROOT.TFile(fn, "READ")
                            hist_tmp = infile.Get(f"{cat_prefix}_{sh}")
                            hist_tmp.SetDirectory(0)
                            if (hist_tmp):
                                hist_sys.Add(hist_tmp) 
                            infile.Close()
                        if args.preventNegative: # set the negative bin content to 0.
                            for b in range(hist_sys.GetNbinsX()+1): 
                                if hist_sys.GetBinContent(b+1) < 0:
                                    hist_sys.SetBinContent(b+1, 0)
                        dhname = f"dh_{mass}_{cat_name}_{sh}"
                        dh = ROOT.RooDataHist(dhname, dhname, CMS_higgs_mass, ROOT.RooFit.Import(hist_sys))
                        ws.Import(dh)
                        if (args.verbose):
                            cprint("     - datahist entries: {}".format(dh.sumEntries()))
                        hist_sys.Delete()
                        
                    if ("Resolved" in cat_name) and ("EleHDAL" not in sh) and ("JER" not in sh) and ("JEC" not in sh): 
                        sysFileNames = [sf for sf in inputTreeFile if "resolved" in sf]
                        hist_sys = ROOT.TH1F(f"{cat_prefix}_{sh}", "", 60, 110, 170)
                        for fn in sysFileNames:
                            infile = ROOT.TFile(fn, "READ")
                            hist_tmp = infile.Get(f"{cat_prefix}_{sh}")
                            hist_tmp.SetDirectory(0)
                            if (hist_tmp):
                                hist_sys.Add(hist_tmp) 
                            infile.Close()
                        if args.preventNegative: # set the negative bin content to 0.
                            for b in range(hist_sys.GetNbinsX()+1): 
                                if hist_sys.GetBinContent(b+1) < 0:
                                    hist_sys.SetBinContent(b+1, 0)
                        dhname = f"dh_{mass}_{cat_name}_{sh}"
                        dh = ROOT.RooDataHist(dhname, dhname, CMS_higgs_mass, ROOT.RooFit.Import(hist_sys))
                        ws.Import(dh)
                        if (args.verbose):
                            cprint("     - datahist entries: {}".format(dh.sumEntries()))
                        hist_sys.Delete()
                    
    if (not args.useSystHist) and doSystematics:   # for muon channel analysis
        for sh in sysHists:
            # systematic tree name
            syst_treeName = f"{inputTreeName}_{sh}"
            for cat_name, cat_cut in category__.items():
                if year != 2017 and "IsoMu" in cat_name:
                    continue
                files_with_syst_tree = [f + ":" + syst_treeName for f in inputTreeFile]
                arr = up4.concatenate(files_with_syst_tree, ["CMS_higgs_mass", "weight", "category"], library="np", cut=cat_cut)
                
                hname = f"hist_{mass}_{cat_name}_{sh}"
                hist_sys = ROOT.TH1F(hname, hname, 60, 110, 170)   
        
                # Loop over events in tree and fill histogram
                for i in range(len(arr["CMS_higgs_mass"])):
                    hist_sys.Fill(arr["CMS_higgs_mass"][i], arr["weight"][i])
                if args.preventNegative: # set the negative bin content to 0.
                    for b in range(hist_sys.GetNbinsX()+1): # prevent negative bin
                        if hist_sys.GetBinContent(b+1) < 0:
                            hist_sys.SetBinContent(b+1, 0)
        
                # import into WS
                dhname = f"dh_{mass}_{cat_name}_{sh}"
                dh = ROOT.RooDataHist(dhname, dhname, CMS_higgs_mass, ROOT.RooFit.Import(hist_sys))
                ws.Import(dh)
        
                if (args.verbose):
                    cprint("     - dataset entries: {}".format(dh.sumEntries()))
                hist_sys.Delete()
        
    cprint("[INFO] Save WS in :", colorStr="green")
    pprint(outputWSFile) 
    outputWSDir = ROOT.gSystem.DirName(outputWSFile)
    os.makedirs(outputWSDir, exist_ok=True)
    
    fout = ROOT.TFile(outputWSFile, "RECREATE")
    foutdir = fout.mkdir(ws_dir_name[0])
    foutdir.cd()
                
    ws.Write()
    fout.Close()
    

if __name__ == "__main__" :
    parser = get_parser()
    args = parser.parse_args()

    if args.config is None:
        print("Please specify the config file! eg. config")
        parser.print_help()
        sys.exit(1)

    # Extract arguments
    mass            = args.mass
    year            = args.year
    productionMode  = args.productionMode
    doSystematics   = args.doSystematics
    if productionMode not in productionModes:
        print("Available modes: {}".format(productionModes))
        sys.exit(1)
    
    print(mass, year, productionMode)
    # Import config options
    cfg = import_module(re.sub(".py", "", args.config)).trees2ws_cfg[mass][year]
    print(cfg)
    inputTreeFiles   = cfg["inputTreeFiles"]
    inDir            = cfg["inDir"]
    print(inDir)
    inputTreeFile    = cfg["inputTreeFiles"][productionMode]
    inputTreeName    = cfg["inputTreeName"]
    outputWSFile     = cfg["outputWSFiles"][productionMode]
    sysWeis          = cfg["sysWeis"]
    sysHists         = cfg["sysHists"]

    # PyROOT does not display any graphics(root "-b" option)
    ROOT.gROOT.SetBatch()
    ROOT.gErrorIgnoreLevel = ROOT.kWarning
    
    main()
