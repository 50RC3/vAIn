import zlib
import logging

# Set up logging for compression/decompression processes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('vAIn.Compression')

def compress_memory(data, level=3):
    """Compress the encrypted data using zlib with enhanced error handling."""
    try:
        # Ensure data is in bytes (if it's a string, encode it)
        if isinstance(data, str):
            data = data.encode('utf-8')

        # Perform compression with the given compression level (1-9)
        compressed_data = zlib.compress(data, level)
        logger.debug("Data successfully compressed.")
        return compressed_data
    except Exception as e:
        logger.error(f"Error compressing data: {e}")
        raise RuntimeError("Compression failed") from e

def decompress_memory(compressed_data):
    """Decompress the data with robust error handling."""
    try:
        # Decompress the data
        decompressed_data = zlib.decompress(compressed_data)
        logger.debug("Data successfully decompressed.")
        return decompressed_data
    except Exception as e:
        logger.error(f"Error decompressing data: {e}")
        raise RuntimeError("Decompression failed") from e
