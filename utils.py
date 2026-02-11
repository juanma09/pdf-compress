import os
import time

def check_ttl(folder, ttl=86400):
    current_time = time.time()
    
    # Ensure the folder exists to avoid errors
    if not os.path.exists(folder):
        print(f"Folder '{folder}' not found.")
        return

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        
        # Only process files, skip sub-directories
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > ttl:
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error deleting {filename}: {e}")

def get_size_stats(original_path, reduced_path, debug=False):
    try:
        # Get sizes in bytes
        size_orig = os.path.getsize(original_path)
        size_new = os.path.getsize(reduced_path)

        # Convert to bits (1 byte = 8 bits)
        bits_orig = size_orig * 8
        bits_new = size_new * 8
        
        # Calculate differences
        diff_bits = bits_orig - bits_new
        
        if size_orig > 0:
            percentage = (diff_bits / bits_orig) * 100
        else:
            percentage = 0

        # Output report
        if debug:
            print(f"--- Bitwise Comparison ---")
            print(f"Original:   {bits_orig:,} bits")
            print(f"Reduced:    {bits_new:,} bits")
            print(f"Difference: {diff_bits:,} bits saved")
            print(f"Percentage: {percentage:.2f}% reduction")
        return diff_bits, percentage
    except FileNotFoundError:
        print("Error: One of the files could not be found. Check your paths.")
    except Exception as e:
        print(f"An error occurred: {e}")