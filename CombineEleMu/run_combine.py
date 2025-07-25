import os
import numpy as np
from ROOT import gSystem
from glob import glob
from contextlib import contextmanager
from multiprocessing import Pool
from tqdm import tqdm


# https://stackoverflow.com/a/24176022
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        
mu_cats = [
    "diMu9.0MuPho_EBHR9",
    "diMu9.0MuPho_EBLR9",
    "diMu9.0MuPho_EE",
    "diMu9.0MuPho_VBF",
    "diMu9.0MuPho_BST",

    "diMu25MuPho_EBHR9",
    "diMu25MuPho_EBLR9",
    "diMu25MuPho_EE",
    "diMu25MuPho_VBF",
    "diMu25MuPho_BST",
    "diMu50MuPho",

    "diMu9.0IsoMu_EBHR9",
    "diMu9.0IsoMu_EBLR9",
    "diMu9.0IsoMu_EE",
    "diMu9.0IsoMu_VBF",
    "diMu9.0IsoMu_BST",

    "diMu50IsoMu_EBHR9",
    "diMu50IsoMu_EBLR9",
    "diMu50IsoMu_EE",
    "diMu50IsoMu_VBF",
    "diMu50IsoMu_BST"
]

ele_cats = [
    # "Merged2Gsf_Loose",
    "Merged2Gsf_VBF",
    "Merged2Gsf_BST",
    "Merged2Gsf_EBHR9",
    "Merged2Gsf_EBLR9",
    "Merged2Gsf_EE",
    "Resolved"
]

cats = ele_cats + mu_cats

def execute(cmd):
    gSystem.Exec(cmd)
    
def submit(_q):
    pool = Pool(30)
    for i in tqdm(pool.imap_unordered(execute, _q), total=len(_q)):
        pass
    pool.close()
    pool.join()
    
    
# text to ws
# task = []    
# with cd("./cards"):
#     all_cards = glob("*.txt")
#     for card in all_cards:
#         card2root = card.replace(".txt", ".root")
#         mass = card2root.split("_")[-1].replace(".root", "")
#         task.append(f"text2workspace.py {card} -c {card2root} -m {mass}")
#     submit(task)   
        
    #     "text2workspace.py {} -c {}"
    # combineTool.py datacard_hmmg_runII_comb_${mass}.txt -M AsymptoticLimits -n _comb_${mass} -m ${mass} --run=blind --cminDefaultMinimizerStrategy 0
    
# limit     
# task = []    
# with cd("./cards"):
#     all_cards = glob("*.txt")
#     for card in all_cards:
#         card2root = card.replace(".txt", ".root")
#         ext = "_" + card2root.replace("datacard_", "").replace(".root", "")
#         mass = card2root.split("_")[-1].replace(".root", "")
#         task.append(f"combine {card2root} -M AsymptoticLimits -n {ext} -m {mass} --run=blind --cminDefaultMinimizerStrategy 0 &> ../logger/AsymptoticLimits{ext}.txt")
#     submit(task)
 
# task = []    
# with cd("./cards"):
#     mass_interp = np.linspace(120, 130, 11, endpoint=True).astype(int)
#     for mass in  mass_interp:
#         card2root = f"datacard_hllg_runII_comb_NoLoose_{mass}.txt"
#         ext = "_" + card2root.replace("datacard_", "").replace(".txt", "")
#         task.append(f"combine {card2root} -M AsymptoticLimits -n {ext} -m {mass} --run=blind --cminDefaultMinimizerStrategy 0 &> ../logger/AsymptoticLimits{ext}.txt")
#     submit(task)
   

# with cd("./cards"):
#     mass_interp = np.linspace(120, 130, 11, endpoint=True).astype(int)
#     for mass in  mass_interp:
#         execute(f"combine -M GenerateOnly datacard_hllg_runII_comb_NoLoose_{mass}.txt -t -1 --saveToys --expectSignal=1 --expectSignalMass={mass} -m {mass}")

# task = []    
# with cd("./cards"):
#     mass_interp = np.linspace(120, 130, 11, endpoint=True).astype(int)
#     for mass in  mass_interp:
#         task.append(f"combine datacard_hllg_runII_comb_NoLoose_{mass}.txt -M Significance -n _comb_NoLoose_{mass}_expSignal1 -m {mass} -t -1 --toysFile higgsCombineTest.GenerateOnly.mH{mass}.123456.root &> ../logger/Significance_comb_{mass}_expSignal1.txt")
#         task.append(f"combine datacard_hllg_runII_comb_NoLoose_{mass}.txt -M Significance -n _comb_NoLoose_{mass}_expectSignalMass125 -m {mass} -t -1 --toysFile higgsCombineTest.GenerateOnly.mH125.123456.root &> ../logger/Significance_comb_{mass}.txt")
        
#     submit(task)
    # --freezeParameters allConstrainedNuisances
    
# task = []    
# with cd("./cards"):

# task = []    
# for cat in mu_cats:
#     card = "./cards/datacard_hmmg_runII_{}_125.root".format(cat)
#     task.append("python makeToys.py -e {} -i {} &> ./logger/maketoys_{}.txt".format(cat, card, cat))
# for cat in ele_cats:
#     card = "./cards/datacard_heeg_runII_{}_125.root".format(cat)
#     task.append("python3 makeToys.py -e {} -i {} &> ./logger/maketoys_{}.txt".format(cat, card, cat))
# submit(task)    


# for cat in mu_cats:
#     execute("python makeSplusBModelPlot_old.py --inputWSFile ./cards/datacard_hmmg_runII_%s_125.root --cats %s --ext %s --doBands --doToyVeto --xvar CMS_higgs_mass,m_{#mu#mu#gamma},GeV --sigScaler 5 --channelText H#rightarrow#gamma*#gamma#rightarrow#mu#mu#gamma" %(cat, cat, cat)) 
    
# for cat in ele_cats:
#     execute("python makeSplusBModelPlot_old.py --inputWSFile ./cards/datacard_heeg_runII_%s_125.root --cats %s --ext %s --doBands --doToyVeto --xvar CMS_higgs_mass,m_{ee#gamma},GeV --sigScaler 20 --channelText H#rightarrow#gamma*#gamma#rightarrowee#gamma" %(cat, cat, cat)) 