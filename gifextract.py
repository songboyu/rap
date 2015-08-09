import io
from PIL import Image, ImageSequence

def processImage(r_data, path):
    """
    Iterate the GIF, extracting each frame.
    """
    stream = io.BytesIO(r_data)
    im = Image.open(stream)
    max_time = 0
    max_frame = None
    for frame in ImageSequence.Iterator(im):
        try:
            if frame.info['duration'] > max_time:
                max_time = frame.info['duration']
                max_frame = frame.convert('RGBA')
        except KeyError:
            # Ignore if there was no duration, we will not count that frame.
            pass
    # print max_time
    max_frame.save(path, format='PNG')
    output = io.BytesIO()
    max_frame.save(output, format='PNG')
    return output.getvalue()