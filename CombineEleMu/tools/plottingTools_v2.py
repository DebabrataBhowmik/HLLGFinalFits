import ROOT
import json
import math
import pandas
import numpy as np
import re
from CMS_lumi import CMS_lumi


# Function to extract the sigma effective of a histogram
def effSigma(_h):
    nbins, binw, xmin = (
        _h.GetXaxis().GetNbins(),
        _h.GetXaxis().GetBinWidth(1),
        _h.GetXaxis().GetXmin(),
    )
    mu, rms, total = _h.GetMean(), _h.GetRMS(), _h.Integral()
    if (total <= 0.):
        print("effsigma: Too few entries to compute it: {}. Returning 0 for effSigma".format(total), flush=True)
        return 0.
    
    # Scan round window of mean: window RMS/binWidth (cannot be bigger than 0.1*number of bins)
    nWindow = int(rms / binw) if (rms / binw) < 0.1 * nbins else int(0.1 * nbins)
    
    # Determine minimum width of distribution which holds 0.693 of total
    rlim = 0.683 * total
    wmin = 9999999
    
    # iscanmin = -999
    for iscan in range(-1 * nWindow, nWindow + 1):
        # Find bin idx in scan: iscan from mean
        i_centre = int((mu - xmin) / binw + 1 + iscan)
        x_centre = (i_centre - 0.5) * binw + xmin  # * 0.5 for bin centre
        x_up, x_down = x_centre, x_centre
        i_up, i_down = i_centre, i_centre
        
        # Define counter for yield in bins: stop when counter > rlim
        y = _h.GetBinContent(i_centre)  # Central bin height
        r = y
        reachedLimit = False
        for j in range(1, nbins):
            if reachedLimit:
                continue
            
            # Up:
            if (i_up < nbins) & (not reachedLimit):
                i_up += 1
                x_up += binw
                y = _h.GetBinContent(i_up)  # Current bin height
                r += y
                if r > rlim:
                    reachedLimit = True
            else:
                print(" --> Reach nBins in effSigma calc: {}. Returning 0 for effSigma".format(_h.GetName()), flush=True)
                return 0.
            
            # Down:
            if not reachedLimit:
                if i_down > 0:
                    i_down -= 1
                    x_down -= binw
                    y = _h.GetBinContent(i_down)  # Current bin height
                    r += y
                    if r > rlim:
                        reachedLimit = True
                else:
                    print(" --> Reach 0 in effSigma calc: {}. Returning 0 for effSigma".format(_h.GetName()), flush=True)
                    return 0.
    
        # Calculate fractional width in bin takes above limt (assume linear)
        if y == 0.0:
            dx = 0.0
        else:
            dx = (r - rlim) * (binw / y)
        
        # Total width: half of peak
        w = (x_up - x_down + binw - dx) * 0.5
        if w < wmin:
            wmin = w
            iscanmin = iscan
            
        return wmin


def extractBandProperties(data, bidx):
    props = {}
    props["median"] = np.median(data["{}".format(bidx)].values)
    props["up1sigma"] = np.percentile(data["{}".format(bidx)].values, 50*(1+math.erf(1./math.sqrt(2))))
    props["down1sigma"] = np.percentile(data["{}".format(bidx)].values, 50*(1+math.erf(-1./math.sqrt(2))))
    props["up2sigma"] = np.percentile(data["{}".format(bidx)].values, 50*(1+math.erf(2./math.sqrt(2))))
    props["down2sigma"] = np.percentile(data["{}".format(bidx)].values, 50*(1+math.erf(-2./math.sqrt(2))))
    return props

def makeSplusBPlot(workspace, hD, hSB, hB, hS, hDr, hBr, hSr, cat, args, dB=None):
    ROOT.gStyle.SetErrorX(0.00005)
    blindingRegion = [float(args.blindingRegion.split(",")[0]), float(args.blindingRegion.split(",")[1])]
    
    canv = ROOT.TCanvas("canv_{}".format(cat), "canv_{}".format(cat), 800, 800)
    pad1 = ROOT.TPad("pad1_{}".format(cat), "pad1_{}".format(cat), 0, 0.3, 1, 1.0)
    pad1.SetTickx()
    pad1.SetTicky()
    pad1.SetBottomMargin(0.05)
    pad1.SetTopMargin(0.09)
    pad1.SetRightMargin(0.05)
    pad1.SetLeftMargin(0.13)
    pad1.SetBottomMargin(0.03)
    pad1.Draw()
    pad2 = ROOT.TPad("pad2_{}".format(cat), "pad2_{}".format(cat), 0, 0, 1, 0.3)
    pad2.SetTickx()
    pad2.SetTicky()
    pad2.SetTopMargin(0.03)
    pad2.SetBottomMargin(0.28)
    pad2.SetLeftMargin(0.13)
    pad2.SetRightMargin(0.05)

    pad2.Draw()
    padSizeRatio = 0.75/0.35

    # Axis options 
    ROOT.TGaxis.SetMaxDigits(4)
    ROOT.TGaxis.SetExponentOffset(-0.05, 0.00, "y")
    
    # Nominal plot
    pad1.cd()
    h_axes = hD.Clone()
    h_axes.Reset()
    if args.doBands: 
        h_axes.SetMaximum((hD.GetMaximum()+hD.GetBinError(hD.GetMaximumBin()))*1.5)
    else: 
        h_axes.SetMaximum((hD.GetMaximum()+hD.GetBinError(hD.GetMaximumBin()))*1.5)
    h_axes.SetMinimum(0.)
    h_axes.SetTitle("")
    h_axes.GetXaxis().SetTitle("")
    h_axes.GetXaxis().SetLabelSize(0)
    h_axes.GetYaxis().SetTitleSize(0.06)
    h_axes.GetYaxis().SetTitle("Events / GeV")
    h_axes.GetYaxis().SetTitleOffset(1.1)
    h_axes.GetYaxis().SetLabelSize(0.045)
    h_axes.GetYaxis().SetLabelOffset(0.007)
    h_axes.Draw()
    
    # Add bands
    if args.doBands:
        gr_1sig, gr_1sig_r = ROOT.TGraphAsymmErrors(), ROOT.TGraphAsymmErrors()
        gr_2sig, gr_2sig_r = ROOT.TGraphAsymmErrors(), ROOT.TGraphAsymmErrors()
        gr_i = 0
        # Loop over bins and extract median and +-1/2sigma bands
        for ibin in range(h_axes.GetXaxis().GetFirst(), h_axes.GetNbinsX()+1):
            xval = h_axes.GetXaxis().GetBinCenter(ibin)
            xerr = 0.5*(h_axes.GetXaxis().GetBinWidth(ibin))
            bkgval = hB["nBins"].GetBinContent(ibin)
            properties = extractBandProperties(dB, ibin)
            gr_1sig.SetPoint(gr_i,xval,properties["median"])
            gr_2sig.SetPoint(gr_i,xval,properties["median"])
            gr_1sig_r.SetPoint(gr_i,xval,properties["median"]-bkgval)
            gr_2sig_r.SetPoint(gr_i,xval,properties["median"]-bkgval)
            gr_1sig.SetPointError(gr_i,xerr,xerr,properties["median"]-properties["down1sigma"],properties["up1sigma"]-properties["median"])
            gr_2sig.SetPointError(gr_i,xerr,xerr,properties["median"]-properties["down2sigma"],properties["up2sigma"]-properties["median"])
            gr_1sig_r.SetPointError(gr_i,xerr,xerr,properties["median"]-properties["down1sigma"],properties["up1sigma"]-properties["median"])
            gr_2sig_r.SetPointError(gr_i,xerr,xerr,properties["median"]-properties["down2sigma"],properties["up2sigma"]-properties["median"])
            gr_i += 1
        gr_1sig.SetFillColor(ROOT.kGreen)
        gr_1sig.SetFillStyle(1001)
        gr_2sig.SetFillColor(ROOT.kYellow)
        gr_2sig.SetFillStyle(1001)
        gr_1sig_r.SetFillColor(ROOT.kGreen)
        gr_1sig_r.SetFillStyle(1001)
        gr_2sig_r.SetFillColor(ROOT.kYellow)
        gr_2sig_r.SetFillStyle(1001)
        gr_2sig.Draw("LE3SAME")
        gr_1sig.Draw("LE3SAME")
    
    # Add legend
    if args.doBands: 
        leg = ROOT.TLegend(0.58, 0.46, 0.86, 0.76)
    else: 
        leg = ROOT.TLegend(0.58, 0.56, 0.86, 0.76)
    leg.SetFillStyle(0)
    leg.SetLineColor(0)
    leg.SetTextSize(0.045)
    leg.AddEntry(hD, "Data", "ep")
    
    if args.unblind:
        leg.AddEntry(hSB["pdfNBins"], "S+B fit", "l")
        leg.AddEntry(hB["pdfNBins"], "Background component", "l")
    else:
        leg.AddEntry(hB["pdfNBins"], "Background Fit", "l")
        leg.AddEntry(hS["pdfNBins"], "Signal Model #times {}".format(args.signalScaler), "fl")
    if args.doBands:
        leg.AddEntry(gr_1sig,"#pm1 #sigma","F")
        leg.AddEntry(gr_2sig,"#pm2 #sigma","F")
    leg.Draw("Same")
    
    # Set pdf style
    if args.unblind:
        hSB["pdfNBins"].SetLineWidth(3)
        hSB["pdfNBins"].SetLineColor(2)
        hSB["pdfNBins"].Draw("Hist same c")
        hB["pdfNBins"].SetLineWidth(3)
        hB["pdfNBins"].SetLineColor(2)
        hB["pdfNBins"].SetLineStyle(2)
        hB["pdfNBins"].Draw("Hist same c")
    else:
        hS["pdfNBins"].SetLineWidth(3)
        hS["pdfNBins"].SetLineColor(9)
        hS["pdfNBins"].SetFillColor(38)
        hS["pdfNBins"].SetFillStyle(1001)
        # hS["pdfNBins"].GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
        hS["pdfNBins"].Scale(float(args.signalScaler))
        hS["pdfNBins"].Draw("Hist same cf")
        hB["pdfNBins"].SetLineWidth(3)
        hB["pdfNBins"].SetLineColor(2)
        hB["pdfNBins"].Draw("Hist same c")
    
    # Set data style
    hD.SetMarkerStyle(20)
    # hD.SetMarkerSize(1.5)
    hD.SetMarkerColor(1)
    hD.SetLineColor(1)
    hD.Draw("Same PE")
    # Add TLatex to plot
    lat0 = ROOT.TLatex()
    lat0.SetTextFont(42)
    lat0.SetTextAlign(11)
    lat0.SetNDC()
    lat0.SetTextSize(0.06)
    #lat0.DrawLatex(0.12,0.92,"#bf{CMS} #it{Preliminary}")
    #lat0.DrawLatex(0.12,0.92,"#bf{CMS}")
    # lat0.DrawLatex(0.6,0.92,"137 fb^{-1} (13 TeV)")
    lat0.DrawLatex(0.6, 0.8, "#scale[0.75]{%s}"%cat)
    #lat0.DrawLatex(0.15,0.83,"#scale[0.75]{H#rightarrow#gamma#gamma}")
    lat0.DrawLatex(0.17, 0.83, "#scale[0.85]{H #rightarrow #gamma*#gamma #rightarrow ee#gamma}")
    
    CMS_lumi(pad1, 5, 0, "138 fb^{-1}", 2017, True, "Preliminary", "", "")
    canv.Update()
    pad1.RedrawAxis()

    # Ratio plot
    pad2.cd()
    h_axes_ratio = hDr.Clone()
    h_axes_ratio.Reset()
    h_axes_ratio.SetMaximum(max((hDr.GetMaximum()+hDr.GetBinError(hDr.GetMaximumBin()))*1.7,hSr.GetMaximum()*1.1))
    h_axes_ratio.SetMinimum((hDr.GetMinimum()-hDr.GetBinError(hDr.GetMinimumBin()))*1.2)
    h_axes_ratio.SetTitle("")
    h_axes_ratio.GetXaxis().SetTitleSize(0.06*padSizeRatio)
    h_axes_ratio.GetXaxis().SetLabelSize(0.05*padSizeRatio)
    h_axes_ratio.GetXaxis().SetLabelOffset(0.007)
    h_axes_ratio.GetXaxis().SetTickLength(0.03*padSizeRatio)
    h_axes_ratio.GetYaxis().SetLabelSize(0.05*padSizeRatio)
    h_axes_ratio.GetYaxis().SetLabelOffset(0.006)
    # h_axes_ratio.GetYaxis().SetNdivisions(506)
    h_axes_ratio.GetYaxis().SetTitle("")
    # h_axes_ratio.GetYaxis().SetTitleSize(0.05*padSizeRatio)
    h_axes_ratio.Draw()
    
    # Draw bands 
    if args.doBands:
        gr_2sig_r.Draw("LE3SAME")
        gr_1sig_r.Draw("LE3SAME")
    # Set pdf style
    if args.unblind:
        hSr.SetLineWidth(3)
        hSr.SetLineColor(2)
        hSr.Draw("Hist same c")
        hBr.SetLineWidth(3)
        hBr.SetLineStyle(2)
        hBr.SetLineColor(2)
        hBr.Draw("Hist same c")
    else:
        hSr.SetLineWidth(3)
        hSr.SetLineColor(9)
        hSr.SetFillColor(38)
        hSr.SetFillStyle(1001)
        hSr.GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
        hSr.Scale(float(args.signalScaler)*padSizeRatio)
        # hSr.Draw("Hist same cf") #!FIXEDME
        hBr.SetLineWidth(3)
        hBr.SetLineColor(2)
        hBr.Draw("Hist same c")
        
    # Set data style
    hDr.SetMarkerStyle(20)
    hDr.SetMarkerColor(1)
    # hDr.SetMarkerSize(1.5)
    hDr.SetLineColor(1)
    hDr.Draw("Same PE")
    
    # Add TLatex to ratio plot
    lat1 = ROOT.TLatex()
    lat1.SetTextFont(42)
    lat1.SetTextAlign(33)
    lat1.SetNDC(1)
    lat1.SetTextSize(0.045*padSizeRatio)
    lat1.DrawLatex(0.87, 0.91, "Background Component Subtracted")

    # Save canvas
    canv.Update()
    canv.SaveAs("./SplusBModels_%s/%s_%s.png"%(cat, cat, args.xvar.split(",")[0]))
    canv.SaveAs("./SplusBModels_%s/%s_%s.pdf"%(cat, cat, args.xvar.split(",")[0]))
    #raw_input("Press any key to continue...")