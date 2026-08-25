import urllib.request
import gzip
import shutil
from pathlib import Path

def download_fasttext_model():
    """
    Downloads and extracts the FastText cc.en.100.bin model.
    This is a ~650MB download that will be extracted to ~958MB.
    """
    base_dir = Path(__file__).parent.parent
    fasttext_dir = base_dir / "models" / "fasttext"
    fasttext_dir.mkdir(parents=True, exist_ok=True)

    model_url = "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.100.bin.gz"
    gz_path = fasttext_dir / "cc.en.100.bin.gz"
    bin_path = fasttext_dir / "cc.en.100.bin"

    # Check if already downloaded
    if bin_path.exists():
        print(f"✓ FastText model already exists at {bin_path}")
        return

    print("=" * 70)
    print("FASTTEXT MODEL DOWNLOAD")
    print("=" * 70)
    print(f"\nDownloading from: {model_url}")
    print(f"Download size: ~650MB")
    print(f"Extracted size: ~958MB")
    print(f"Destination: {bin_path}")
    print("\nThis may take several minutes depending on your internet connection...")

    # Download
    print("\nDownloading...")
    urllib.request.urlretrieve(model_url, gz_path)
    print(f"✓ Downloaded to {gz_path}")

    # Extract
    print("\nExtracting gzip archive...")
    with gzip.open(gz_path, 'rb') as f_in:
        with open(bin_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"✓ Extracted to {bin_path}")

    # Clean up
    print("\nCleaning up compressed file...")
    gz_path.unlink()
    print(f"✓ Removed {gz_path}")

    print("\n" + "=" * 70)
    print("DOWNLOAD COMPLETE")
    print("=" * 70)
    print(f"\nFastText model ready at: {bin_path}")
    print("\nNext step: Run python scripts/train_ml_models.py")

if __name__ == "__main__":
    try:
        download_fasttext_model()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nIf download fails, you can manually download from:")
        print("https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.100.bin.gz")
        print("Extract and place at: models/fasttext/cc.en.100.bin")
