import os, sys
import ROOT
import numpy as np
from TdrStyle import setTDRStyle
from array import array
from collections import OrderedDict as od
from commonObjects import massBaseList, dwd__
from CMS_lumi import CMS_lumi
from pprint import pprint

def GetValuesFromFile(fname):
    fin = ROOT.TFile(fname, "READ")
    if fin.IsZombie():
        sys.exit(1)
    tin = fin.Get("limit")
    res = [ev.limit for ev in tin]
    return res


def LimitVsM():
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetOptStat(0)
    
    Limit = od([("2sigma_do", array("f", [])), ("1sigma_do", array("f", [])), ("mean", array("f", [])), ("1sigma_up", array("f", [])), ("2sigma_up", array("f", [])), ("mass", array("f", []))])
    mass_interp = np.linspace(massBaseList[0], massBaseList[-1], 11, endpoint=True).astype(int)
    for m in mass_interp:
        input_file = "./cards/higgsCombine_NoLoose_comb_{}.AsymptoticLimits.mH{}.root".format(m, m)
        _limit = GetValuesFromFile(input_file)
        Limit["2sigma_do"].append(_limit[0])
        Limit["1sigma_do"].append(_limit[1])
        Limit["mean"].append(_limit[2])
        Limit["1sigma_up"].append(_limit[3])
        Limit["2sigma_up"].append(_limit[4])
        Limit["mass"].append(m)

    npoints = len(Limit["mean"])
    xerr = array("f", [0] * npoints)
    sigma2_err_do = array("f", [abs(a - b) for a, b in zip(Limit["mean"], Limit["2sigma_do"])])
    sigma1_err_do = array("f", [abs(a - b) for a, b in zip(Limit["mean"], Limit["1sigma_do"])])
    sigma2_err_up = array("f", [abs(a - b) for a, b in zip(Limit["mean"], Limit["2sigma_up"])])
    sigma1_err_up = array("f", [abs(a - b) for a, b in zip(Limit["mean"], Limit["1sigma_up"])])
    expErr = ROOT.TGraphAsymmErrors(npoints, Limit["mass"], Limit["mean"])
    sigma2 = ROOT.TGraphAsymmErrors(npoints, Limit["mass"], Limit["mean"], xerr, xerr, sigma2_err_do, sigma2_err_up)
    sigma1 = ROOT.TGraphAsymmErrors(npoints, Limit["mass"], Limit["mean"], xerr, xerr, sigma1_err_do, sigma1_err_up)

    c1 = ROOT.TCanvas("c1", "c1", 700, 700)
    c1.SetRightMargin(0.05)
    c1.SetTopMargin(0.07)
    c1.SetBottomMargin(0.14)
    c1.SetLeftMargin(0.14)
    c1.cd()

    mg = ROOT.TMultiGraph()
    mg.SetTitle("")

    sigma2.SetFillColor(ROOT.kOrange)
    sigma1.SetFillColor(ROOT.kGreen+1)
    expErr.SetMarkerColor(ROOT.kBlack)
    expErr.SetLineColor(ROOT.kBlack)
    expErr.SetLineWidth(3)
    expErr.SetLineStyle(7)

    mg.Add(sigma2, "")
    mg.Add(sigma1, "")
    mg.Add(expErr, "")

    mg.Draw("AL3")

    max_element = max(Limit["2sigma_up"])
    mg.GetXaxis().SetTitle("m_{H} (GeV)")
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetXaxis().SetLabelSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetLabelSize(0.05)
    # mg.SetMinimum(0)
    # mg.SetMaximum(15)
    mg.GetXaxis().SetLimits(119.5, 130.5)
    mg.GetYaxis().SetTitle("95% CL limit on #sigma/#sigma_{SM}")
    mg.GetXaxis().SetTitleOffset(1.2)
    mg.GetYaxis().SetTitleOffset(1.2)
    mg.GetYaxis().SetRangeUser(0, max_element * 2.5)
    # mg.GetYaxis().SetRangeUser(0, 12)
    mg.Draw("zE2")
    mg.Draw("AL3")

    leg = ROOT.TLegend(0.6, 0.72, 0.9, 0.89)
    # leg.SetNColumns(2)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.AddEntry(expErr, "Expected", "l")
    leg.AddEntry(sigma1, "68% expected", "f")
    leg.AddEntry(sigma2, "95% expected", "f")
    leg.Draw()

    line = ROOT.TLine(119.5, 1, 130.5, 1)
    line.SetLineColor(ROOT.kRed)
    line.SetLineWidth(2)
    line.Draw()

    CMS_lumi(c1, 5, 0, "138 fb^{-1}", 0, True, "Preliminary", "", "")
    c1.RedrawAxis()
    
    # if not os.path.exists("./plots"):
    #     os.system("mkdir ./plots")
    c1.Print("LimitVSMass_ele.pdf")
    c1.Print("LimitVSMass_ele.png")
    c1.Close()


def LimitSummary():
    cat_tag = od()
    cat_tag["comb"]                 = "#bf{H#rightarrow#gamma*#gamma#rightarrowll#gamma, Combined}"
    cat_tag["Mu"]                   = "H#rightarrow#gamma*#gamma#rightarrow#mu#mu#gamma, Combined"
    cat_tag["Ele"]                  = "H#rightarrow#gamma*#gamma#rightarrowee#gamma, Combined"
    
    cat_tag["diMu9.0MuPho_EBHR9"]   = "MuPho EB HR9 (0-9)"
    cat_tag["diMu9.0MuPho_EBLR9"]   = "MuPho EB LR9 (0-9)"
    cat_tag["diMu9.0MuPho_EE"]      = "MuPho EE (0-9)"
    cat_tag["diMu9.0MuPho_VBF"]     = "MuPho VBF (0-9)"
    cat_tag["diMu9.0MuPho_BST"]     = "MuPho BST (0-9)"

    cat_tag["diMu25MuPho_EBHR9"]    = "MuPho EB HR9 (9-25)"
    cat_tag["diMu25MuPho_EBLR9"]    = "MuPho EB LR9 (9-25)"
    cat_tag["diMu25MuPho_EE"]       = "MuPho EE (9-25)"
    cat_tag["diMu25MuPho_VBF"]      = "MuPho VBF (9-25)"
    cat_tag["diMu25MuPho_BST"]      = "MuPho BST (9-25)"
    cat_tag["diMu50MuPho"]          = "MuPho (25-50)"

    cat_tag["diMu9.0IsoMu_EBHR9"]   = "IsoMu EB HR9 (0-9)"
    cat_tag["diMu9.0IsoMu_EBLR9"]   = "IsoMu EB LR9 (0-9)"
    cat_tag["diMu9.0IsoMu_EE"]      = "IsoMu EE (0-9)"
    cat_tag["diMu9.0IsoMu_VBF"]     = "IsoMu VBF (0-9)"
    cat_tag["diMu9.0IsoMu_BST"]     = "IsoMu BST (0-9)"

    cat_tag["diMu50IsoMu_EBHR9"]    = "IsoMu EB HR9 (9-50)"
    cat_tag["diMu50IsoMu_EBLR9"]    = "IsoMu EB LR9 (9-50)"
    cat_tag["diMu50IsoMu_EE"]       = "IsoMu EE (9-50)"
    cat_tag["diMu50IsoMu_VBF"]      = "IsoMu VBF (9-50)"
    cat_tag["diMu50IsoMu_BST"]      = "IsoMu BST (9-50)"

    cat_tag["Merged2Gsf_EE"]        = "Merged2Gsf EE"
    cat_tag["Merged2Gsf_EBLR9"]     = "Merged2Gsf EB LR9"
    cat_tag["Merged2Gsf_EBHR9"]     = "Merged2Gsf EB HR9"
    cat_tag["Merged2Gsf_VBF"]       = "Merged2Gsf VBF"
    cat_tag["Merged2Gsf_BST"]       = "Merged2Gsf Boost"
    cat_tag["Merged2Gsf_Loose"]     = "Merged2Gsf WPLoose"
    cat_tag["Resolved"]             = "Resolved"
    
    # yhigh = [0, 2.4, 3.4, 4.4, 5.4, 7.4, 8.4, 9.4]
    # yhigh = [i+2 for i in range(len(cat_tag.keys()))]
    
    
    yhigh = []
    i = 0
    for key, value in cat_tag.items():
        if key == "diMu9.0MuPho_EBHR9":
            i = i+1
        if key == "diMu25MuPho_EBHR9":
            i = i+1
        if key == "diMu9.0IsoMu_EBHR9":
            i = i+1
        if key == "diMu50IsoMu_EBHR9":
            i = i+1
        if key == "Merged2Gsf_EE":
            i = i+1
        yhigh.append(i)
        i += 1.2
    
        
    Limit = od([("2sigma_do", array("f", [])), ("1sigma_do", array("f", [])), ("mean", array("f", [])), ("1sigma_up", array("f", [])), ("2sigma_up", array("f", [])), ("yaxis", array("f", yhigh))])
    for key, value in cat_tag.items():
        if key == "comb":
            input_file = "./cards/higgsCombine_hllg_runII_comb_125.AsymptoticLimits.mH125.root"
        elif key == "Mu":
            input_file = "./cards/higgsCombine_hmmg_runII_comb_125.AsymptoticLimits.mH125.root"
        elif key == "Ele":
            input_file = "./cards/higgsCombine_heeg_runII_comb_125.AsymptoticLimits.mH125.root"
        elif "Mu" in key: 
            input_file = "./cards/higgsCombine_hmmg_runII_{}_125.AsymptoticLimits.mH125.root".format(key)
        else:
            input_file = "./cards/higgsCombine_heeg_runII_{}_125.AsymptoticLimits.mH125.root".format(key)

        _limit = GetValuesFromFile(input_file)
        Limit["2sigma_do"].append(_limit[0])
        Limit["1sigma_do"].append(_limit[1])
        Limit["mean"].append(_limit[2])
        Limit["1sigma_up"].append(_limit[3])
        Limit["2sigma_up"].append(_limit[4])

    npoints = len(Limit["mean"])
    xerr = array("f", [0] * npoints)
    yerr = array("f", [0.1] * npoints)
    sigma2_err_do = array("f", [abs(a - b) for a, b in zip(Limit["mean"], Limit["2sigma_do"])])
    sigma1_err_do = array("f", [abs(a - b) for a, b in zip(Limit["mean"], Limit["1sigma_do"])])
    sigma2_err_up = array("f", [abs(a - b) for a, b in zip(Limit["mean"], Limit["2sigma_up"])])
    sigma1_err_up = array("f", [abs(a - b) for a, b in zip(Limit["mean"], Limit["1sigma_up"])])
    expErr = ROOT.TGraphAsymmErrors(npoints, Limit["mean"], Limit["yaxis"], xerr, xerr, xerr, xerr)
    sigma2 = ROOT.TGraphAsymmErrors(npoints, Limit["mean"], Limit["yaxis"], sigma2_err_do, sigma2_err_up, yerr, yerr)
    sigma1 = ROOT.TGraphAsymmErrors(npoints, Limit["mean"], Limit["yaxis"], sigma1_err_do, sigma1_err_up, yerr, yerr)

    xmin, xmax = 0.5, 5000
    mr = 0.04
    mt = 0.05
    mb = 0.1
    ml = 0.35

    c1 = ROOT.TCanvas("c1", "c1", 900, 1100)
    c1.cd()
    c1.SetRightMargin(mr)
    c1.SetLeftMargin(ml)
    c1.SetTopMargin(mt)
    c1.SetBottomMargin(mb)
    c1.SetLogx()
    c1.Modified()
    c1.Update()

    sigma1.SetFillColor(ROOT.kGreen+1)
    sigma2.SetFillColor(ROOT.kOrange)
    expErr.SetMarkerStyle(20)
    expErr.SetMarkerSize(1)
    expErr.SetMarkerColor(ROOT.kBlack)
    expErr.SetLineColor(ROOT.kBlack)

    mg = ROOT.TMultiGraph()
    mg.SetTitle("")
    mg.Add(sigma2, "2")
    mg.Add(sigma1, "2")
    mg.Add(expErr, "e1p")
    mg.Draw("ap")
    mg.SetMinimum(yhigh[0] - 1)
    mg.SetMaximum(yhigh[-1]+7)
    
    line = ROOT.TLine(1, yhigh[0] - 1, 1, yhigh[-1]+7)
    line.SetLineColor(ROOT.kRed+1)
    line.SetLineWidth(2)
    line.Draw()
    
    mg.GetYaxis().SetTickLength(0)
    mg.GetYaxis().SetTitleSize(0.01)
    mg.GetYaxis().SetLabelOffset(999)
    mg.GetXaxis().SetLabelOffset(0.001)
    mg.GetXaxis().SetLabelFont(42)
    mg.GetXaxis().SetLabelSize(0.035)
    mg.GetXaxis().SetTitleSize(0.035)
    # mg.GetXaxis().SetTitleOffset(0.2)
    mg.GetXaxis().SetLimits(xmin, xmax+70)
    mg.GetXaxis().SetTitle("95% CL upper limit on #sigma/#sigma_{SM}")
    mg.GetXaxis().SetTitleOffset(1.5)

    leg = ROOT.TLegend(0.7, 0.85, 0.92, 0.98*(1-mt))
    leg.SetTextFont(42)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.AddEntry(expErr, "Expected", "p")
    leg.AddEntry(sigma1, "68% expected", "f")
    leg.AddEntry(sigma2, "95% expected", "f")
    leg.Draw()

    latex = ROOT.TLatex()
    latex.SetTextColor(ROOT.kBlack)
    latex.SetTextSize(0.025)
    latex.SetTextAlign(32)
    i = 0
    for key, value in cat_tag.items():
        latex.SetTextSize(0.025)
        latex.SetTextColor(ROOT.kBlack)
        # latex.SetTextSize(0.028)
        # if value == "H#rightarrow#gamma*#gamma#rightarrowll#gamma, Combined":
        #     latex.SetTextFont(72)
        # else:
        latex.SetTextFont(42)
        latex.DrawLatex(xmin-0.1, Limit["yaxis"][i], value)
        
        i += 1

    latex.SetTextColor(ROOT.kBlack)
    latex.SetTextSize(0.028)
    latex.SetTextAlign(32)
    i = 0
    for i, exp in enumerate(Limit["mean"]):
        latex.DrawLatex(xmax*0.8, Limit["yaxis"][i], "{}".format(round(exp, 2)))
        i += 1

    CMS_lumi(c1, 5, 0, "138 fb^{-1}", 2017, True, "Preliminary", "", "")
    c1.RedrawAxis()
    c1.Update()

    if not os.path.exists("./plots"):
        os.system("mkdir ./plots")
    c1.Print("./LimitSummary.pdf")
    c1.Print("./LimitSummary.png")
    c1.Close()
    
def SigVsM():
    mass_interp = np.linspace(massBaseList[0], massBaseList[-1], 11, endpoint=True).astype(int)
    
    pvalue = []
    significance = []
    pvalue_inj = []
    significance_inj = []
    for m in mass_interp:
        input_file = "./cards/higgsCombine_comb_NoLoose_{}_expSignal1.Significance.mH{}.root".format(m, m)
        input_file_inj = "./cards/higgsCombine_comb_NoLoose_{}_expectSignalMass125.Significance.mH{}.root".format(m, m)
        
        _p = GetValuesFromFile(input_file)[0]
        _p_inj = GetValuesFromFile(input_file_inj)[0]
        
        # pvalue.append(_p)
        # significance.append(ROOT.Math.normal_quantile_c(_p, 1))
        # pvalue_inj.append(_p_inj)
        # significance_inj.append(ROOT.Math.normal_quantile_c(_p_inj, 1))
        
        pvalue.append(ROOT.Math.normal_cdf_c(_p))
        significance.append(_p)
        pvalue_inj.append(ROOT.Math.normal_cdf_c(_p_inj))
        significance_inj.append(_p_inj)
    
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetOptStat(0)
    
    c1 = ROOT.TCanvas("c1", "c1", 700, 700)
    c1.SetRightMargin(0.05)
    c1.SetTopMargin(0.07)
    c1.SetBottomMargin(0.14)
    c1.SetLeftMargin(0.145)
    c1.cd()
    c1.SetLogy()
    gL = ROOT.TGraph(len(mass_interp), mass_interp.astype(np.float64), np.array(pvalue, dtype=np.float64))
    gL_inj = ROOT.TGraph(len(mass_interp), mass_interp.astype(np.float64), np.array(pvalue_inj, dtype=np.float64))
    # gL.Print("v")
    
    gL.GetYaxis().SetRangeUser(5*1e-4, 1)
    gL.GetYaxis().SetTickSize(0.03)
    gL.GetYaxis().SetTitleSize(0.04)
    gL.GetYaxis().SetLabelSize(0.04)
    # gL.GetYaxis().SetMoreLogLabels()
    gL.GetYaxis().SetTitleOffset(1.5)
    gL.GetYaxis().SetTitle("Local p-value")
    # gL.GetXaxis().SetRangeUser(118, 135)
    
    gL.GetXaxis().SetLimits(119, 132.5)
    gL.GetXaxis().SetTitle("m_{H} (GeV)")
    gL.GetXaxis().SetTickSize(0.03)
    gL.GetXaxis().SetTitleSize(0.04)
    gL.GetXaxis().SetLabelSize(0.04)
    gL.GetXaxis().SetTitleOffset(1.5)
    
    gL.SetLineColor(ROOT.kBlue+2)
    gL.SetLineWidth(3)
    gL.SetMarkerColor(ROOT.kBlue+2)
    gL.SetMarkerSize(1.2)
    gL.Draw("APL")
    
    gL_inj.SetLineColor(ROOT.kRed)
    gL_inj.SetLineWidth(3)
    gL_inj.SetMarkerColor(ROOT.kRed)
    gL_inj.SetMarkerSize(1.2)
    gL_inj.Draw("PL same")

    latex = ROOT.TLatex()
    latex.SetTextColor(13)
    latex.SetTextSize(0.04)
    latex.SetTextAlign(32)
    latex.DrawLatex(131.8, ROOT.Math.normal_cdf_c(1), "1 #sigma")
    
    line = ROOT.TLine(120, ROOT.Math.normal_cdf_c(1), 130, ROOT.Math.normal_cdf_c(1))
    line.SetLineColor(13)
    line.SetLineStyle(7)
    line.SetLineWidth(3)
    line.Draw("same")
    
    latex.DrawLatex(131.8, ROOT.Math.normal_cdf_c(0.5), "0.5 #sigma")
    line2 = ROOT.TLine(120, ROOT.Math.normal_cdf_c(0.5), 130, ROOT.Math.normal_cdf_c(0.5))
    line2.SetLineColor(13)
    line2.SetLineStyle(7)
    line2.SetLineWidth(3)
    line2.Draw("same")
    
    latex.DrawLatex(131.8, ROOT.Math.normal_cdf_c(2), "2 #sigma")
    line1 = ROOT.TLine(120, ROOT.Math.normal_cdf_c(2), 130, ROOT.Math.normal_cdf_c(2))
    line1.SetLineColor(13)
    line1.SetLineStyle(7)
    line1.SetLineWidth(3)
    line1.Draw("same")
    
    latex.DrawLatex(131.8, ROOT.Math.normal_cdf_c(3), "3 #sigma")
    line3 = ROOT.TLine(120, ROOT.Math.normal_cdf_c(3), 130, ROOT.Math.normal_cdf_c(3))
    line3.SetLineColor(13)
    line3.SetLineStyle(7)
    line3.SetLineWidth(3)
    line3.Draw("same")
    
    gL.Draw("PL same")
    gL_inj.Draw("PL same")
    
    leg = ROOT.TLegend(0.2, 0.33, 0.77, 0.45)
    leg.SetTextSize(0.04)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    leg.AddEntry(gL, "expected", "L")
    leg.AddEntry(gL_inj, "expected @ m_{H} = 125 GeV: "+"%.2f#sigma"%(significance[5]), "L")
    leg.Draw()
    
    CMS_lumi(c1, 5, 0, "138 fb^{-1}", 2017, True, "Preliminary", "", "")
    c1.RedrawAxis()
    c1.Update()
    
    # if not os.path.exists("./plots"):
    #     os.system("mkdir ./plots")
    c1.Print("./pvalue.pdf")
    c1.Print("./pvalue.png")
    c1.Close()
    
if __name__ == "__main__" :
    setTDRStyle()
    LimitVsM()
    # LimitSummary()
    # SigVsM()