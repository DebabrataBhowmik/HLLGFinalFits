# Script to exrtract yields and some useful information for creating datacard
# * Uses Pandas dataframe to store all proc x cat yields
# * per category per dataframe

import os, sys
import ROOT
import pickle
import numpy as np
import pandas as pd
from glob import glob
from argparse import ArgumentParser
from collections import OrderedDict as od
from commonObjects import yearsStr, sqrts__, swd__, bwd__, massBaseList, productionModes, decayMode, procToDatacardNameMap, outputWSName__, lumiMap, lumiScaleFactor, category__
from commonTools import color

def main(cat):
    print(color.GREEN + "Make yield dataframe for {}".format(cat) + color.END)

    # Initiate pandas dataframe
    column_title = ["year", "type", "procOriginal", "proc", "cat", "mass", "modelWSOriginal", "modelWSFile", "model", "rate"]
    df_data = pd.DataFrame(columns=column_title)

    # FILL DATAFRAME: signal
    print("[INFO] Adding signal to dataFrame")
    mass_interp = np.linspace(massBaseList[0], massBaseList[-1], 11, endpoint=True).astype(int)
    for year in yearsStr:
        if "IsoMu" in cat and year != "2017":
            continue
        for mass in mass_interp:
            for proc in productionModes:
                _procOriginal = proc
                _proc = "{}_{}_{}".format(procToDatacardNameMap[proc], year, decayMode)
                _cat = cat

                sigWSDir = "{}/WS/Interpolation/{}".format(swd__, year)
                # _modelWSFile = "{}/CMS_HLLG_Interp_{}_{}_{}_{}.root".format(sigWSDir, mass, proc, year, cat)
                _modelWSOriginal = "{}/CMS_HLLG_Interp_{}_{}_{}_{}.root".format(sigWSDir, mass, proc, year, cat)
                # _modelWSFile = "{}/CMS_HLLG_Interp_{}_{}_{}_{}.root".format(smodel_prefix, mass, proc, year, cat)
                _modelWSFile = "CMS_HLLG_Interp_{}_{}_{}_{}.root".format(mass, proc, year, cat)
                
                NewSigPdf_name = "NewSigPdf_{}_{}_{}_{}".format(proc, mass, cat, year)
                # NewSigPdf_name = "SigPdf_{}_{}_{}_{}".format(proc, mass, cat, year)
                _model = "{}:{}".format(outputWSName__, NewSigPdf_name)
                _rate = float(lumiMap[year]) * lumiScaleFactor
                
                f = ROOT.TFile(_modelWSOriginal)
                w = f.Get(outputWSName__)
                sumw = w.var("ExpYield").getVal()
                if sumw <= 0.:
                    print(color.RED + "[INFO] cat: {}, proc: {}, mass: {}, year: {} has yields < 0, discarded.".format(cat, proc, mass, year)+color.END)
                    continue

                df_data.loc[len(df_data)] = [year, "sig", _procOriginal, _proc, _cat, mass, _modelWSOriginal, _modelWSFile, _model, _rate]

    # FILL DATAFRAME: background
    print("[INFO] Adding background/data to dataFrame")
    _proc_bkg = "bkg_mass"
    _proc_data = "data_obs"
    _cat = cat
    # _modelWSFile = "{}/multipdf/CMS_HLLG_multipdf_13TeV_{}.root".format(bwd__, _cat)
    mutilpdf_dir = "multipdf" if BLIND else "multipdf_unblind"
    _modelWSOriginal = "{}/{}/CMS_HLLG_multipdf_13TeV_{}.root".format(bwd__, mutilpdf_dir, _cat)
    # _modelWSFile = "{}/CMS_HLLG_multipdf_13TeV_{}.root".format(bmodel_prefix, _cat)
    _modelWSFile = "CMS_HLLG_multipdf_13TeV_{}.root".format(_cat)
    _model_bkg = "multipdf:CMS_higgs_{}_{}_bkgshape".format(_cat, sqrts__)
    _model_data = "multipdf:roohist_data_mass_{}".format(_cat)
    _mass = "-" # not needed for data/bkg
    df_data.loc[len(df_data)] = ["merged", "bkg", _proc_bkg, _proc_bkg, _cat, _mass, _modelWSOriginal, _modelWSFile, _model_bkg, 1] #!overall scaler for background = 1
    df_data.loc[len(df_data)] = ["merged", "data", _proc_data, _proc_data, _cat, _mass, _modelWSOriginal, _modelWSFile, _model_data, -1]

    # Yields: for each signal row in dataFrame extract the yield
    # Loop over signal rows in dataFrame: extract yields (nominal & systematic variations)
    df_data["nominal_yield"] = "-"
    for ir, r in df_data[df_data["type"] == "sig"].iterrows():
        # open input WS file and extract workspace
        fin = ROOT.TFile.Open(r["modelWSOriginal"])
        if not fin:
            sys.exit(1)
        inputWS = fin.Get(outputWSName__)

        # Extract nominal yield
        _yield = inputWS.var("ExpYield").getVal()
        df_data.at[ir, "nominal_yield"] = _yield

        # Remove the workspace and file from heap
        inputWS.Delete()
        fin.Close()

    # SAVE YIELDS DATAFRAME
    y_dir = "yields" if BLIND else "yields_unblind"
    print ("[INFO] Saving yields dataframe: ./{}/{}.pkl".format(y_dir, cat))
    if not os.path.isdir(y_dir):
        os.makedirs(y_dir)
    with open("./{}/{}.pkl".format(y_dir, cat), "wb") as fout:
        pickle.dump(df_data, fout)


if __name__ == "__main__":
    # cards_prefix = "./cards"
    # smodel_prefix = "./cards/s_models"
    # bmodel_prefix = "./cards/b_models"
    
    BLIND = True
    # BLIND = False
    for _c in category__.keys():
        main(_c)