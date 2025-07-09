import ROOT
import os
import re
from pprint import pprint
import uproot as up
import uproot4 as up4
from argparse import ArgumentParser
from collections import OrderedDict as od
from importlib import import_module
from commonObjects import inputWSName__, category__, productionModes
from commonTools import cprint

def get_parser():
    parser = ArgumentParser(description="Script to convert data trees to RooWorkspace (compatible for finalFits)")
    parser.add_argument("-c", "--config", help="Input config: specify list of variables/analysis categories", default=None, type=str)
    parser.add_argument("-v",  "--verbose",         help="verbose message",                                             default=False,action="store_true")
    return parser


def main():
    # Read the input ROOT files
    cprint("[INFO] Read file:", colorStr="green")
    pprint(inputTreeFiles)
    
    # cmd = f"hadd -f tmp_data.root "
    # for f2merged in inputTreeFiles:
    #     cmd += f"{f2merged} "
    # ROOT.gSystem.Exec(cmd)
    
    # fin = ROOT.TFile("tmp_data.root", "READ")
    # intree = fin.Get(inputTreeName)
    # ROOT.gROOT.cd() # https://root-forum.cern.ch/t/copytree-with-a-selection/12908/3
    files_with_tree = []
    for f in inputTreeFiles: 
        files_with_tree.append(f + ":" + inputTreeName)
    
    # create work space
    ws_dir_name = inputWSName__.split("/")
    ws = ROOT.RooWorkspace(ws_dir_name[1], ws_dir_name[1])
    
    # create variables
    CMS_higgs_mass = ROOT.RooRealVar("CMS_higgs_mass", "CMS_higgs_mass", 125, 110, 170, "GeV") # initial, lower bound, upper bound
    weight = ROOT.RooRealVar("weight", "weight", 1., "")
    ws.Import(CMS_higgs_mass)
    ws.Import(weight)
    
    # convert tree to dataset 
    for cat_name, cat_cut in category__.items():
        # outtree = intree.CopyTree(cat_cut)
        incolumns = ["CMS_higgs_mass", "category"]
        arr = up4.concatenate(files_with_tree, incolumns, library="np", cut=cat_cut)
        aset = ROOT.RooArgSet(CMS_higgs_mass, weight)
        
        # nominal dataset
        # dname = f"data_obs_{cat_name}"
        # dset = ROOT.RooDataSet(dname, dname, outtree, aset, "", "weight")
        # ws.Import(dset)
        
        # nominal dataset
        dname = f"data_obs_{cat_name}"
        dset = ROOT.RooDataSet(dname, dname, aset, ROOT.RooFit.WeightVar("weight"))
        
        # Loop over events in tree and add to dataset with weight 1
        for i in range(len(arr["CMS_higgs_mass"])):
            weight.setVal(1.)
            CMS_higgs_mass.setVal(arr["CMS_higgs_mass"][i])
            dset.add(aset, 1.)
        ws.Import(dset)
        if (args.verbose):
            cprint("     - dataset entries: {}".format(dset.sumEntries()))
            
    
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
    # Extract information from config file:
    parser = get_parser()
    args = parser.parse_args()

    if args.config is None:
        print("Please specify the config file! eg. config_data")
        parser.print_help()
        sys.exit(1)

    # Import config options
    cfg = import_module(re.sub(".py","", args.config)).trees2ws_cfg
    inputTreeFiles   = cfg["inputTreeFiles"]
    inputTreeName    = cfg["inputTreeName"]
    outputWSFile     = cfg["outputWSFile"]

    main()
