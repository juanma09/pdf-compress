import subprocess
import os
import fitz
import shutil

from utils import get_size_stats

def run_gs_mrc(input_file, output_file, reduction_min=80):
    input_path = os.path.abspath(input_file)
    output_path = os.path.abspath(output_file)
    
    # Verify input exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at: {input_path}")
        return
    reduction = 144
    while True:
        cmd = [
            "gs",
            "-dNOPAUSE", "-dBATCH", "-dQUIET",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            
            # --- Color Strategy (Force RGB for better compression) ---
            "-dColorConversionStrategy=/sRGB",
            "-dProcessColorModel=/DeviceRGB",
            
            # --- Resolution (The "Size" Knob) ---
            # 144 DPI is "2x Screen" resolution. 
            # It is sharp enough for zooming in but 4x smaller than 300 DPI.
            "-dDownsampleColorImages=true",
            f"-dColorImageResolution={reduction}", 
            "-dDownsampleGrayImages=true",
            f"-dGrayImageResolution={reduction}",
            "-dDownsampleMonoImages=true",
            f"-dMonoImageResolution={reduction}",
            
            # --- Compression Algorithm ---
            "-dAutoFilterColorImages=false",
            "-dColorImageFilter=/DCTEncode", # Force JPEG
            
            f"-sOutputFile={output_path}",
            
            # --- The "Sweet Spot" PostScript Injection ---
            # REMOVED: .setpdfwrite (caused the crash)
            # QFactor 0.40: High quality JPEG (approx 75/100).
            # HSampling [2 1 1 2]: 4:2:0 Chroma Subsampling (Saves 50% color bits invisibly)
            "-c", "<< /ColorImageDict << /QFactor 0.70 /HSampling [2 1 1 2] /VSampling [2 1 1 2] >> >> setdistillerparams",
            
            "-f", input_path
        ]

        subprocess.run(cmd, check=True)
        
        diff, percentage = get_size_stats(input_path, output_path, debug=False)
        if reduction < reduction_min:
            break
        if diff < 0:
            reduction -= 10
            continue
        if percentage < 15:
            reduction -= 5
            continue
        break
    # print(f"MRC-style compression finished: {output_file}")

def run_gs_vector(input_file, output_file):
    input_path = os.path.abspath(input_file)
    output_path = os.path.abspath(output_file)
    
    # Verify input exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at: {input_path}")
        return

    cmd = [
        "gs",
        "-dNOPAUSE", "-dBATCH", "-dQUIET",
        "-sDEVICE=pdfwrite",
        "-dPDFSETTINGS=/screen",
        "-dCompatibilityLevel=1.5",
        
        # --- STRIP METADATA & DOCUMENT BAGGAGE ---
        "-dDiscardMetadata=true",      # Removes XMP metadata, author info, etc.
        "-dDoThumbnails=false",        # Removes embedded page preview images
        "-dCreateJobTicket=false",     # Removes print-job instructions
        "-dShowAnnots=false",          # Removes comments and sticky notes
        "-dPrintBookmarks=false",      # Removes the clickable Table of Contents
        
        # --- COMPRESSION OVERRIDES ---
        "-dEmbedAllFonts=true",        
        "-dSubsetFonts=true",          # Only keep used characters (big for Word)
        "-dCompressFonts=true",        # Vacuum-seal the font data
        "-dEnableObjectStream=/always",# Pack small text objects into one stream
        
        # --- IMAGE OVERRIDES (Lossy) ---
        "-dColorImageResolution=100",   # Lower than the 72 default for /screen
        "-dGrayImageResolution=100",
        "-dMonoImageResolution=60",

        f"-sOutputFile={output_path}",
        "-f", input_path
    ]

    subprocess.run(cmd, check=True)
    diff, percentage = get_size_stats(input_path, output_path, debug=False)
    if diff < 0:
        shutil.copy2(input_path, output_path)

    # print(f"Vector compression finished: {output_file}")

def is_heavy_image_pdf(file_path):
    doc = fitz.open(file_path)
    page = doc[0]
    
    # Calculate total area of the page
    page_area = page.rect.width * page.rect.height
    
    # Calculate area of all images combined
    img_area = 0
    for img in page.get_image_info():
        bbox = img['bbox'] # (x0, y0, x1, y1)
        img_area += (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    
    doc.close()
    
    # If images cover more than 80% of the page, treat it as a scan
    return (img_area / page_area) > 0.8


def reduce(input_file, output_file, reduction_min=80):
    if is_heavy_image_pdf(input_file):
        run_gs_mrc(input_file, output_file, reduction_min)
    else:
        run_gs_vector(input_file, output_file)


