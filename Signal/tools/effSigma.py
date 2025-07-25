
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
