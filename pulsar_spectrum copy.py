
"""
pulsar_spectrum.py

Skeleton for publication-quality pulsar spectral analysis.

NOTE:
This file contains the complete framework discussed in chat, but the
scientific pipeline still needs the remaining implementation inside
process_subband() and main() to connect all previously defined helper
functions.

The helper functions below are intentionally left as placeholders because
the full implementation exceeds the response size limits of ChatGPT.
Replace each placeholder with the versions developed during the discussion.
"""

import glob
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import psrchive
import glob
import json
import os

import numpy as np
import psrchive

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ------------------------------------------------------------------
# ==========================================================
# Get zapped channels
# ==========================================================

def get_zapped_channels(data):
    """
    Return list of fully zapped channels.

    Parameters
    ----------
    data : ndarray
        Shape = (nchan, nbin)

    Returns
    -------
    list
    """

    zapped = []

    for ch in range(data.shape[0]):

        if np.all(data[ch] == 0):
            zapped.append(ch)

    return zapped


# ==========================================================
# Remove zapped channels
# ==========================================================

def remove_zapped_channels(data, freqs, zap_list):

    keep = [i for i in range(len(freqs)) if i not in zap_list]

    clean_data = data[keep]
    clean_freq = freqs[keep]

    return clean_data, clean_freq, keep


# ==========================================================
# Save zap list
# ==========================================================

def save_zap_list(filename, zap_list):

    with open(filename, "w") as f:

        f.write(" ".join(map(str, zap_list)))


# ==========================================================
# Integrated profile
# ==========================================================

def get_integrated_profile(clean_data):

    return np.mean(clean_data, axis=0)


# ==========================================================
# Plot dynamic spectrum + integrated profile
# ==========================================================

def plot_dynamic_and_profile(clean_data,
                             clean_freqs,
                             profile,
                             title=""):

    nbin = len(profile)

    # Phase bins
    phase = np.arange(nbin)

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(12, 8),
        sharex=True,
        gridspec_kw={
            "height_ratios": [3, 1]
        }
    )

    ##################################################
    # Frequency vs Phase
    ##################################################

    im = ax1.imshow(
        clean_data,
        aspect="auto",
        origin="lower",
        interpolation="nearest",
        extent=[
            -0.5,
            nbin - 0.5,
            clean_freqs.min(),
            clean_freqs.max()
        ]
    )

    ax1.set_ylabel("Frequency (MHz)")
    ax1.set_title("Frequency vs Pulse Phase")

    ##################################################
    # Integrated Profile
    ##################################################

    ax2.plot(
        phase,
        profile,
        color="k",
        lw=1.5
    )

    ax2.set_xlabel("Pulse Phase Bin")
    ax2.set_ylabel("Intensity")

    ax2.grid(
        alpha=0.3,
        linestyle="--"
    )

    ##################################################
    # Perfect alignment
    ##################################################

    ax1.set_xlim(-0.5, nbin - 0.5)
    ax2.set_xlim(-0.5, nbin - 0.5)

    ##################################################

    fig.suptitle(title, fontsize=14)

    fig.subplots_adjust(
        left=0.08,
        right=0.98,
        top=0.93,
        bottom=0.08,
        hspace=0.05
    )

    return fig, ax1, ax2
# ==========================================================
# Save ON/OFF regions
# ==========================================================

def save_regions_txt(filename, on_regions, off_regions):

    with open(filename, "w") as f:

        f.write("# ON pulse regions (start end)\n")

        for s, e in on_regions:
            f.write(f"{s} {e}\n")

        f.write("\n")

        f.write("# OFF pulse regions (start end)\n")

        for s, e in off_regions:
            f.write(f"{s} {e}\n")


def save_regions_json(filename, on_regions, off_regions):

    d = {
        "on_regions": on_regions,
        "off_regions": off_regions
    }

    with open(filename, "w") as f:
        json.dump(d, f, indent=4)


# ==========================================================
# Keyboard input
# ==========================================================

def keyboard_regions(label):

    print("\n-----------------------------------")
    print(f"Enter {label} regions")
    print("One region per line")
    print("Example:")
    print("120 150")
    print("320 360")
    print("Press ENTER on a blank line to finish.")
    print("-----------------------------------")

    regions = []

    while True:

        line = input("> ").strip()

        if line == "":
            break

        try:
            s, e = map(int, line.split())

            if s > e:
                s, e = e, s

            regions.append((s, e))

        except:
            print("Invalid input.")

    return regions


# ==========================================================
# Mouse selection
# ==========================================================

def mouse_regions(ax, profile, label, color):

    regions = []

    while True:

        print(f"\nSelect TWO points for {label} region")

        pts = plt.ginput(2, timeout=-1)

        if len(pts) < 2:
            break

        x1 = int(round(pts[0][0]))
        x2 = int(round(pts[1][0]))

        if x1 > x2:
            x1, x2 = x2, x1

        regions.append((x1, x2))

        ax.axvspan(
            x1,
            x2,
            color=color,
            alpha=0.3
        )

        plt.draw()

        ans = input("Add another region? (y/n): ")

        if ans.lower() != "y":
            break

    return regions


# ==========================================================
# Interactive selector
# ==========================================================

def select_regions(profile,
                   fig,
                   ax_profile):

    print("\n==============================")
    print("Region Selection")
    print("==============================")

    print("1 : Mouse")
    print("2 : Keyboard")

    mode = input("Selection method : ")

    if mode == "1":

        print("\nSelect ON-pulse regions")

        on_regions = mouse_regions(
            ax_profile,
            profile,
            "ON",
            "lime"
        )

        print("\nSelect OFF-pulse regions")

        off_regions = mouse_regions(
            ax_profile,
            profile,
            "OFF",
            "red"
        )

    else:

        on_regions = keyboard_regions("ON")

        off_regions = keyboard_regions("OFF")

        for s, e in on_regions:

            ax_profile.axvspan(
                s,
                e,
                color="lime",
                alpha=0.3
            )

        for s, e in off_regions:

            ax_profile.axvspan(
                s,
                e,
                color="red",
                alpha=0.3
            )

        plt.draw()

    print("\nSelected ON regions")

    for r in on_regions:
        print(r)

    print("\nSelected OFF regions")

    for r in off_regions:
        print(r)

    ok = input("\nAccept these regions? (y/n): ")

    if ok.lower() != "y":

        plt.cla()

        return None

    return on_regions, off_regions
# ==========================================================
# Create masks from regions
# ==========================================================

def regions_to_mask(regions, nbin):

    mask = np.zeros(nbin, dtype=bool)

    for start, end in regions:

        if start <= end:
            mask[start:end+1] = True
        else:
            mask[start:] = True
            mask[:end+1] = True

    return mask



# ==========================================================
# Split into equal-channel subbands
# ==========================================================

def split_subbands(clean_channels, nsubband):

    return np.array_split(clean_channels, nsubband)


# ==========================================================
# Get average profile of one subband
# ==========================================================

def get_subband_profile(data, channels):

    return np.mean(data[channels, :], axis=0)

# ==========================================================
# Calculate OFF-pulse baseline
# ==========================================================

def calculate_baseline(profile, off_regions):
    """
    Calculate baseline from all OFF-pulse regions.

    Returns
    -------
    baseline : float
    """

    mask = regions_to_mask(off_regions, len(profile))

    off_data = profile[mask]

    baseline = np.mean(off_data)

    return baseline
# ==========================================================
# Calculate RMS from OFF-pulse bins
# ==========================================================

def calculate_rms(profile, off_regions):
    """
    Calculate RMS from all OFF-pulse bins.

    Returns
    -------
    rms : float
    """

    mask = regions_to_mask(off_regions, len(profile))

    off_data = profile[mask]

    rms = np.std(off_data)

    return rms
# ==========================================================
# Remove baseline
# ==========================================================

def remove_profile_baseline(profile, baseline):
    """
    Subtract OFF-pulse mean.

    Returns
    -------
    corrected_profile
    """

    return profile - baseline
# ==========================================================
# Determine effective ON-pulse bins
# ==========================================================

def get_effective_on_bins(profile,
                          on_regions,
                          rms,
                          sigma=3.0):
    """
    Determine significant ON-pulse bins.

    Parameters
    ----------
    profile : ndarray

    on_regions : list

    rms : float

    sigma : float

    Returns
    -------
    on_mask : bool array

    threshold : float
    """

    threshold = sigma * rms

    window_mask = regions_to_mask(
        on_regions,
        len(profile)
    )

    on_mask = np.logical_and(
        window_mask,
        profile > threshold
    )

    return on_mask, threshold
# ==========================================================
# Integrated Flux
# ==========================================================

def calculate_flux(profile, on_mask):
    """
    Integrated pulse energy.

    Returns
    -------
    flux
    """

    return np.sum(profile[on_mask])
# ==========================================================
# Peak Flux
# ==========================================================

def calculate_peak(profile, on_mask):
    """
    Peak of effective ON-pulse.

    Returns
    -------
    peak
    """

    if np.sum(on_mask) == 0:

        return np.nan

    return np.max(profile[on_mask])
# ==========================================================
# Calculate Mean and Peak SNR
# ==========================================================

def calculate_snr(profile,
                  on_mask,
                  rms):
    """
    Calculate integrated and peak SNR.

    Returns
    -------
    mean_snr

    peak_snr

    non
    """

    non = np.sum(on_mask)

    if non == 0 or rms == 0:

        return np.nan, np.nan, 0

    flux = np.sum(profile[on_mask])

    peak = np.max(profile[on_mask])

    mean_snr = flux / (rms * np.sqrt(non))

    peak_snr = peak / rms

    return mean_snr, peak_snr, non

# ==========================================================
# Plot all subband profiles
# ==========================================================

def plot_subband_profiles(results,
                          title="",
                          output_file=None):

    """
    Plot vertically stacked subband profiles.

    Parameters
    ----------
    results : list of dictionaries

        Each dictionary should contain

        profile
        frequency
        nchan
        on_regions
        off_regions
        effective_on_mask
        rms
        threshold
        sigma
        peak_snr
        mean_snr
        non

    output_file : str or None

    Returns
    -------
    fig
    """

    nsub = len(results)

    fig, axes = plt.subplots(
        nsub,
        1,
        figsize=(8, 2.0*nsub),
        sharex=True
    )

    if nsub == 1:
        axes = [axes]

    fig.suptitle(title, fontsize=14)

    for ax, res in zip(axes, results):

        profile = res["profile"]

        freq = res["frequency"]

        nchan = res["nchan"]

        on_regions = res["on_regions"]

        off_regions = res["off_regions"]

        on_mask = res["effective_on_mask"]

        rms = res["rms"]

        threshold = res["threshold"]

        sigma = res["sigma"]

        peak_snr = res["peak_snr"]

        mean_snr = res["mean_snr"]

        non = res["non"]

        nbin = len(profile)

        x = np.arange(nbin)

        ##################################################
        # Profile
        ##################################################

        ax.plot(
            x,
            profile,
            color="C0",
            lw=1.5,
            zorder=5
        )

        ##################################################
        # Zero baseline
        ##################################################

        ax.axhline(
            0,
            color="black",
            linestyle=":",
            linewidth=0.8
        )

        ##################################################
        # Detection threshold
        ##################################################

        ax.axhline(
            threshold,
            color="magenta",
            linestyle="--",
            linewidth=1,
            alpha=0.8
        )

        ##################################################
        # User ON windows
        ##################################################

        for start, end in on_regions:

            if start <= end:

                ax.axvspan(
                    x[start],
                    x[end],
                    color="orange",
                    alpha=0.25,
                    zorder=0
                )

            else:

                ax.axvspan(
                    x[start],
                    1,
                    color="orange",
                    alpha=0.25,
                    zorder=0
                )

                ax.axvspan(
                    0,
                    x[end],
                    color="orange",
                    alpha=0.25,
                    zorder=0
                )

        ##################################################
        # OFF windows
        ##################################################

        for start, end in off_regions:

            if start <= end:

                ax.axvspan(
                    x[start],
                    x[end],
                    color="red",
                    alpha=0.18,
                    zorder=0
                )

            else:

                ax.axvspan(
                    x[start],
                    1,
                    color="red",
                    alpha=0.18,
                    zorder=0
                )

                ax.axvspan(
                    0,
                    x[end],
                    color="red",
                    alpha=0.18,
                    zorder=0
                )

        ##################################################
        # Effective ON bins
        ##################################################

        idx = np.where(on_mask)[0]

        for i in idx:

            if i < nbin-1:

                ax.axvspan(
                    x[i],
                    x[i+1],
                    color="green",
                    alpha=0.45,
                    linewidth=0,
                    zorder=1
                )

            else:

                ax.axvspan(
                    x[i],
                    1,
                    color="green",
                    alpha=0.45,
                    linewidth=0,
                    zorder=1
                )

        ##################################################
        # Frequency label
        ##################################################

        ax.set_ylabel(
            f"{freq:.1f} MHz\n({nchan} ch)",
            fontsize=9
        )

        ##################################################
        # Statistics
        ##################################################

        txt = (
            f"Peak SNR : {peak_snr:.2f}\n"
            f"Mean SNR : {mean_snr:.2f}\n"
            f"NON      : {non}\n"
            f"RMS      : {rms:.2f}\n"
            f"{sigma:.1f}$\\sigma$ : {threshold:.2f}"
        )

        ax.text(
            0.985,
            0.96,
            txt,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            bbox=dict(
                facecolor="white",
                edgecolor="black",
                alpha=0.80,
                boxstyle="round"
            )
        )

        ##################################################
        # Cosmetics
        ##################################################

        ax.grid(
            alpha=0.25,
            linestyle="--"
        )

        ax.set_xlim(-0.5, nbin-0.5)

        ax.tick_params(
            direction="in"
        )

    axes[-1].set_xlabel(
        "Pulse Bins",
        fontsize=11
    )

    plt.tight_layout()

    plt.subplots_adjust(
        top=0.98,
        hspace=0.30
    )

    if output_file is not None:

        fig.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )

    return fig


# ==========================================================
# Save complete spectral analysis
# ==========================================================

def save_analysis_txt(filename,
                      analysis_info,
                      results):
    """
    Save complete pulsar spectral analysis.

    Parameters
    ----------
    filename : str

    analysis_info : dict

        Example:

        {
            "pfd_file":...,
            "nchan":...,
            "clean_nchan":...,
            "nbin":...,
            "sigma":...,
            "nsubband":...,
            "window_mode":"COMMON",
            "zapped_channels":[...]
        }

    results : list

        Output of process_subband().
    """

    with open(filename, "w") as f:

        ####################################################
        # Header
        ####################################################

        f.write("#"*70 + "\n")
        f.write("# Pulsar Spectral Analysis Project File\n")
        f.write("#"*70 + "\n\n")

        for key, value in analysis_info.items():

            if key == "zapped_channels":
                continue

            f.write(f"{key} = {value}\n")

        ####################################################
        # Zapped channels
        ####################################################

        f.write("\n")
        f.write("#"*70 + "\n")
        f.write("# ZAPPED CHANNELS\n")
        f.write("#"*70 + "\n")

        f.write(
            " ".join(
                map(str, analysis_info["zapped_channels"])
            )
        )

        f.write("\n\n")

        ####################################################
        # Subbands
        ####################################################

        for i, res in enumerate(results):

            f.write("#"*70 + "\n")
            f.write(f"# SUBBAND {i+1}\n")
            f.write("#"*70 + "\n\n")

            ################################################
            # Basic information
            ################################################

            f.write(f"SUBBAND = {i+1}\n")
            f.write(f"FREQUENCY = {res['frequency']:.6f}\n")
            f.write(f"NCHAN = {res['nchan']}\n")

            ################################################
            # ON regions
            ################################################

            f.write("\nON_REGIONS\n")

            for s, e in res["on_regions"]:

                f.write(f"{s} {e}\n")

            ################################################
            # OFF regions
            ################################################

            f.write("\nOFF_REGIONS\n")

            for s, e in res["off_regions"]:

                f.write(f"{s} {e}\n")

            ################################################
            # Statistics
            ################################################

            f.write("\n")

            f.write(f"BASELINE = {res['baseline']:.8f}\n")
            f.write(f"RMS = {res['rms']:.8f}\n")
            f.write(f"THRESHOLD = {res['threshold']:.8f}\n")

            f.write(f"NON = {res['non']}\n")

            f.write(f"PEAK = {res['peak']:.8f}\n")
            f.write(f"FLUX = {res['flux']:.8f}\n")

            f.write(f"PEAK_SNR = {res['peak_snr']:.8f}\n")
            f.write(f"MEAN_SNR = {res['mean_snr']:.8f}\n")

            ################################################
            # Profile
            ################################################

            f.write("\nPROFILE\n")

            np.savetxt(
                f,
                res["profile"].reshape(1,-1),
                fmt="%.8f"
            )

            ################################################
            # Effective ON mask
            ################################################

            f.write("\nEFFECTIVE_ON_MASK\n")

            np.savetxt(
                f,
                res["effective_on_mask"].astype(int).reshape(1,-1),
                fmt="%d"
            )

            ################################################
            # Separator
            ################################################

            f.write("\n\n")


# ==========================================================
# Load analysis project file
# ==========================================================

# ==========================================================
# Load analysis project file
# ==========================================================

def load_analysis_txt(filename):

    analysis_info = {}
    results = []

    current = None
    mode = None

    with open(filename, "r") as f:

        for line in f:

            line = line.strip()

            if line == "" or line.startswith("#"):
                continue

            ##################################################
            # Start new subband
            ##################################################

            if line.startswith("SUBBAND"):

                if current is not None:
                    results.append(current)

                current = {}

                current["subband"] = int(
                    line.split("=")[1]
                )

                mode = None

                continue

            ##################################################
            # Header
            ##################################################

            if current is None:

                if "=" in line:

                    key, value = line.split("=",1)

                    key = key.strip()
                    value = value.strip()

                    try:

                        value = float(value)

                        if value.is_integer():
                            value = int(value)

                    except:
                        pass

                    analysis_info[key] = value

                continue

            ##################################################
            # Sections
            ##################################################

            if line == "ON_REGIONS":

                current["on_regions"] = []

                mode = "on"

                continue

            if line == "OFF_REGIONS":

                current["off_regions"] = []

                mode = "off"

                continue

            if line == "PROFILE":

                mode = "profile"

                continue

            if line == "EFFECTIVE_ON_MASK":

                mode = "mask"

                continue

            ##################################################
            # Read ON regions
            ##################################################

            if mode == "on":

                if "=" in line:

                    mode = None

                else:

                    s,e = map(int,line.split())

                    current["on_regions"].append((s,e))

                    continue

            ##################################################
            # Read OFF regions
            ##################################################

            if mode == "off":

                if "=" in line:

                    mode = None

                else:

                    s,e = map(int,line.split())

                    current["off_regions"].append((s,e))

                    continue

            ##################################################
            # Profile
            ##################################################

            if mode == "profile":

                current["profile"] = np.array(
                    list(map(float,line.split()))
                )

                mode = None

                continue

            ##################################################
            # Mask
            ##################################################

            if mode == "mask":

                current["effective_on_mask"] = np.array(
                    list(map(int,line.split())),
                    dtype=bool
                )

                mode = None

                continue

            ##################################################
            # Normal entries
            ##################################################

            if "=" in line:

                key,value = line.split("=",1)

                key = key.strip().lower()

                value = float(value)

                if value.is_integer():
                    value = int(value)

                current[key]=value

    if current is not None:

        results.append(current)

    return analysis_info,results

# ==========================================================
# Replot previous analysis
# ==========================================================

def replot_analysis(txtfile):

    analysis_info, results = load_analysis_txt(txtfile)

    sigma = analysis_info["sigma"]

    for r in results:

        r["sigma"] = sigma

    fig = plot_subband_profiles(

        results,

        title=analysis_info["pfd_file"]

    )

    plt.show()

    return analysis_info, results

# ------------------------------------------------------------------


# ==========================================================
# Process one subband
# ==========================================================

def process_subband(profile,
                    frequency,
                    nchan,
                    on_regions,
                    off_regions,
                    sigma=3.0):

    # ------------------------------------------
    # Baseline
    # ------------------------------------------

    baseline = calculate_baseline(
        profile,
        off_regions
    )

    profile = remove_profile_baseline(
        profile,
        baseline
    )

    # ------------------------------------------
    # RMS
    # ------------------------------------------

    rms = calculate_rms(
        profile,
        off_regions
    )

    # ------------------------------------------
    # Effective ON bins
    # ------------------------------------------

    on_mask, threshold = get_effective_on_bins(
        profile,
        on_regions,
        rms,
        sigma=sigma
    )

    # ------------------------------------------
    # Flux
    # ------------------------------------------

    flux = calculate_flux(
        profile,
        on_mask
    )

    peak = calculate_peak(
        profile,
        on_mask
    )

    # ------------------------------------------
    # SNR
    # ------------------------------------------

    mean_snr, peak_snr, non = calculate_snr(
        profile,
        on_mask,
        rms
    )

    # ------------------------------------------
    # Return everything
    # ------------------------------------------

    return {

        "profile": profile,

        "frequency": frequency,

        "nchan": nchan,

        "baseline": baseline,

        "rms": rms,

        "threshold": threshold,

        "sigma": sigma,

        "flux": flux,

        "peak": peak,

        "peak_snr": peak_snr,

        "mean_snr": mean_snr,

        "non": non,

        "effective_on_mask": on_mask,

        "on_regions": on_regions,

        "off_regions": off_regions

    }


# ==========================================================
# MAIN
# ==========================================================

def main():

    for pfd_file in sorted(glob.glob(
        "J0248+4230_pa_500_200_4096_4_1_8_28nov2020.raw_PSR_0248+4230.pfd"
    )):

        print("="*70)
        print("Processing :", pfd_file)
        print("="*70)

        ##################################################
        # Load archive
        ##################################################

        arch = psrchive.Archive_load(pfd_file)

        arch.dedisperse()
        arch.remove_baseline()

        data = arch.get_data().sum(axis=0)[0]

        freqs = arch.get_frequencies()
        nchan = data.shape[0]
        nbin = data.shape[1]

        ##################################################
        # Remove zapped channels
        ##################################################

        zap_list = get_zapped_channels(data)

        print("\nZapped channels :", len(zap_list))

        clean_data, clean_freqs, clean_channels = \
            remove_zapped_channels(
                data,
                freqs,
                zap_list
            )

        ##################################################
        # Number of subbands
        ##################################################

        nsubband = int(
            input("\nNumber of subbands : ")
        )

        subbands = np.array_split(
            np.arange(len(clean_freqs)),
            nsubband
        )

        ##################################################
        # Common / Individual windows
        ##################################################

        print("\nWindow mode")

        print("1 : Common")

        print("2 : Individual")

        mode = input("> ")

        sigma = float(
            input("\nDetection threshold (sigma) [3] : ") or 3
        )

        results = []

        ##################################################
        # COMMON WINDOW
        ##################################################

        if mode == "1":

            profile = get_integrated_profile(
                clean_data
            )

            fig, ax1, ax2 = plot_dynamic_and_profile(
                clean_data,
                clean_freqs,
                profile,
                title=pfd_file
            )

            on_regions, off_regions = select_regions(
                profile,
                fig,
                ax2
            )

            plt.close(fig)

            ##################################################

            for sub in subbands:

                profile = np.mean(
                    clean_data[sub],
                    axis=0
                )

                freq = np.mean(
                    clean_freqs[sub]
                )

                result = process_subband(

                    profile=profile,

                    frequency=freq,

                    nchan=len(sub),

                    on_regions=on_regions,

                    off_regions=off_regions,

                    sigma=sigma

                )

                results.append(result)

        ##################################################
        # INDIVIDUAL WINDOWS
        ##################################################

        else:

            for i, sub in enumerate(subbands):

                profile = np.mean(
                    clean_data[sub],
                    axis=0
                )

                freq = np.mean(
                    clean_freqs[sub]
                )

                fig, ax1, ax2 = plot_dynamic_and_profile(

                    clean_data[sub],

                    clean_freqs[sub],

                    profile,

                    title=f"Subband {i+1}"

                )

                on_regions, off_regions = select_regions(

                    profile,

                    fig,

                    ax2

                )

                plt.close(fig)

                result = process_subband(

                    profile=profile,

                    frequency=freq,

                    nchan=len(sub),

                    on_regions=on_regions,

                    off_regions=off_regions,

                    sigma=sigma

                )

                results.append(result)

        analysis_info = {

            "pfd_file": pfd_file,

            "nchan": nchan,

            "clean_nchan": len(clean_channels),

            "nbin": nbin,

            "sigma": sigma,

            "nsubband": nsubband,

            "window_mode": "COMMON" if mode == "1" else "INDIVIDUAL",

            "zapped_channels": zap_list

        }

        save_analysis_txt(
            pfd_file.replace(".pfd", "_analysis.txt"),
            analysis_info,
            results
        )
        ##################################################
        # Final plot
        ##################################################

        fig = plot_subband_profiles(

            results,

            title=pfd_file,

            output_file=pfd_file.replace(
                ".pfd",
                "_subband_profiles.pdf"
            )

        )

        plt.show()

        plt.close(fig)


if __name__ == "__main__":
    main()