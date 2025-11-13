"""
Fast parallel download of WorldPop data using Python
"""
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def download_chunk(url, start, end, chunk_num, output_file):
    """Download a specific byte range of the file"""
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code in [200, 206]:
        chunk_file = f"{output_file}.part{chunk_num}"
        with open(chunk_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return chunk_num, True
    return chunk_num, False

def parallel_download(url, output_file, num_threads=16):
    """Download file in parallel chunks"""
    print(f"Fetching file info from {url}")

    # Get file size
    response = requests.head(url)
    file_size = int(response.headers.get('content-length', 0))

    if file_size == 0:
        print("Could not determine file size, falling back to regular download")
        return False

    print(f"File size: {file_size / (1024**3):.2f} GB")
    print(f"Downloading with {num_threads} parallel connections...")

    # Check if server supports range requests
    if response.headers.get('accept-ranges') != 'bytes':
        print("Server doesn't support range requests, falling back to regular download")
        return False

    # Calculate chunk sizes
    chunk_size = file_size // num_threads

    # Download chunks in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < num_threads - 1 else file_size - 1
            future = executor.submit(download_chunk, url, start, end, i, output_file)
            futures.append(future)

        # Wait for all chunks with progress bar
        completed = 0
        for future in tqdm(as_completed(futures), total=num_threads, desc="Downloading chunks"):
            chunk_num, success = future.result()
            if success:
                completed += 1

    if completed == num_threads:
        print("\nMerging chunks...")
        # Merge all chunks
        with open(output_file, 'wb') as outfile:
            for i in range(num_threads):
                chunk_file = f"{output_file}.part{i}"
                with open(chunk_file, 'rb') as infile:
                    outfile.write(infile.read())
                os.remove(chunk_file)

        print(f"Download complete: {output_file}")
        return True
    else:
        print(f"Download failed: only {completed}/{num_threads} chunks completed")
        return False

if __name__ == "__main__":
    # WorldPop India 2020 population data (1.7 GB)
    url = "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/IND/ind_ppp_2020.tif"
    output_file = "ind_ppp_2020.tif"

    # Alternative: Download smaller constrained data (100m resolution, ~200MB)
    # This is population counts adjusted to UN estimates
    url_constrained = "https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/IND/ind_ppp_2020_UNadj.tif"
    output_constrained = "ind_ppp_2020_constrained.tif"

    print("=" * 60)
    print("WorldPop India Population Data Downloader")
    print("=" * 60)
    print("\nOptions:")
    print("1. Full resolution data (1.7 GB) - ind_ppp_2020.tif")
    print("2. UN-adjusted constrained data (~200 MB) - recommended")
    print("\nStarting download of constrained data (smaller, faster)...")
    print("=" * 60)

    # Try parallel download of constrained version first (smaller and faster)
    success = parallel_download(url_constrained, output_constrained, num_threads=16)

    if not success:
        print("\nParallel download failed, trying regular download...")
        print("This may take a while...")
        response = requests.get(url_constrained, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(output_constrained, 'wb') as f, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc="Downloading"
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        print(f"\nDownload complete: {output_constrained}")

    print("\nTo download the full resolution data (1.7 GB), run:")
    print(f"  parallel_download('{url}', '{output_file}', num_threads=16)")
