import os
import numpy as np
from ROOT import gSystem
from contextlib import contextmanager
from commonObjects import category__
from commonTools import color

# https://stackoverflow.com/a/24176022
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

outdir = "./cards"
with cd(outdir):
    opt = "comb"
    mass_interp = np.linspace(120, 130, 11, endpoint=True).astype(int)
    for mass in mass_interp:
        cards = ""
        for cat in category__.keys():
            cards += "{}=datacard_hmmg_runII_{}_{}.txt ".format(cat, cat, mass)
            # cards += "datacard_hmmg_runII_{}_{}.txt ".format(cat, mass)
            
        card_comb = "datacard_hmmg_runII_comb_{}.txt".format(mass)
        # print("---> merged card: ./cards/{}".format(card_comb))
        cmd = "combineCards.py {} > {} ".format(cards, card_comb)
        print(color.GREEN+"Execution: "+color.END+cmd)
        print(color.GREEN+"---> merged card: {}/{}".format(outdir, card_comb)+color.END)
        gSystem.Exec("combineCards.py {} > {} ".format(cards, card_comb))
        print(" ")

        
        
# # categoryTag = od()
# # categoryTag["diMu9.0MuPhoTag"] = ["diMu9.0MuPho_EBHR9", "diMu9.0MuPho_EBLR9", "diMu9.0MuPho_EE", "diMu9.0MuPho_VBF", "diMu9.0MuPho_BST"]
# # categoryTag["diMu25MuPhoTag"]  = ["diMu25MuPho_EBHR9", "diMu25MuPho_EBLR9", "diMu25MuPho_EE", "diMu25MuPho_VBF", "diMu25MuPho_BST"]
# # categoryTag["diMu50MuPhoTag"]  = ["diMu50MuPho"]
# # categoryTag["diMu9.0IsoMuTag"] = ["diMu9.0IsoMu_EBHR9", "diMu9.0IsoMu_EBLR9", "diMu9.0IsoMu_EE", "diMu9.0IsoMu_VBF", "diMu9.0IsoMu_BST"]
# # categoryTag["diMu50IsoMuTag"]  = ["diMu50IsoMu_EBHR9", "diMu50IsoMu_EBLR9", "diMu50IsoMu_EE", "diMu50IsoMu_VBF", "diMu50IsoMu_BST"]



# # categoryTag["diMu50IsoMuTag"]

# cats = [
#     "diMu0.7MuPho_EBHR9",
#     "diMu0.7MuPho_EBLR9",
#     "diMu0.7MuPho_EE",
#     "diMu0.7MuPho_VBF",
#     "diMu0.7MuPho_BST",
    
#     "diMu9.0MuPho_EBHR9",
#     "diMu9.0MuPho_EBLR9",
#     "diMu9.0MuPho_EE",
#     "diMu9.0MuPho_VBF",
#     "diMu9.0MuPho_BST",

#     "diMu25MuPho_EBHR9",
#     "diMu25MuPho_EBLR9",
#     "diMu25MuPho_EE",
#     "diMu25MuPho_VBF",
#     "diMu25MuPho_BST",
#     "diMu50MuPho",

#     "diMu9.0IsoMu_EBHR9",
#     "diMu9.0IsoMu_EBLR9",
#     "diMu9.0IsoMu_EE",
#     "diMu9.0IsoMu_VBF",
#     "diMu9.0IsoMu_BST",

#     "diMu50IsoMu_EBHR9",
#     "diMu50IsoMu_EBLR9",
#     "diMu50IsoMu_EE",
#     "diMu50IsoMu_VBF",
#     "diMu50IsoMu_BST",
    
#     "Merged2Gsf_VBF",
#     "Merged2Gsf_BST",
#     "Merged2Gsf_EBHR9",
#     "Merged2Gsf_EBLR9",
#     "Merged2Gsf_EE",
#     "Resolved",
# ]

# with cd("./cards"):
#     opt = "comb"
#     mass_interp = np.linspace(120, 130, 11, endpoint=True).astype(int)
    
#     # all 
#     # for mass in mass_interp:
#     #     cards = ""
#     #     for cat in cats:
#     #         for ch in ["heeg", "hmmg"]:
#     #             if (ch == "heeg" and "Mu" in cat):
#     #                 continue
#     #             if (ch == "hmmg" and "Mu" not in cat):
#     #                 continue 
#     #             cards += "{}=datacard_{}_runII_{}_{}.txt ".format(cat, ch, cat, mass)
            
#     #     card_comb = "datacard_hllg_runII_comb_{}.txt".format(mass)
#     #     print("---> merged card: ./cards/{}".format(card_comb))
#     #     gSystem.Exec("combineCards.py {} > {} ".format(cards, card_comb))
        
#     # ele
#     # for mass in mass_interp:
#     #     cards = ""
#     #     for cat in cats:
#     #         for ch in ["heeg"]:
#     #             if (ch == "heeg" and "Mu" in cat):
#     #                 continue
#     #             if (ch == "hmmg" and "Mu" not in cat):
#     #                 continue 
#     #             cards += "{}=datacard_{}_runII_{}_{}.txt ".format(cat, ch, cat, mass)
            
#     #     card_comb = "datacard_{}_runII_comb_{}.txt".format(ch, mass)
#     #     print("---> merged card: ./cards/{}".format(card_comb))
#     #     gSystem.Exec("combineCards.py {} > {} ".format(cards, card_comb))
        
#     # mu
#     for mass in mass_interp:
#         cards = ""
#         for cat in cats:
#             for ch in ["hmmg"]:
#                 if (ch == "heeg" and "Mu" in cat):
#                     continue
#                 if (ch == "hmmg" and "Mu" not in cat):
#                     continue 
#                 cards += "{}=datacard_{}_runII_{}_{}.txt ".format(cat, ch, cat, mass)
            
#         card_comb = "datacard_{}_runII_comb_{}.txt".format(ch, mass)
#         print("---> merged card: ./cards/{}".format(card_comb))
#         gSystem.Exec("combineCards.py {} > {} ".format(cards, card_comb))