import io


def image_to_bytesio(img):
    """Converts PIL.Image to io.BytesIO of a PNG."""
    bytes_output = io.BytesIO()
    img.save(bytes_output, format='PNG')
    bytes_output = bytes_output.getvalue()

    return bytes_output
