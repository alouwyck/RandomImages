import numpy as np
from PIL import Image, ImageDraw


class Image:
    """
    Base class to create random image
    """
    def __init__(self, size, mode='RGB'):
        """
        :param size: image size (width, height) in pixels (see PILLOW documentation)
        :param mode: 'RGB' (default), 'L' (8 bit) or '1' (1 bit) (see PILLOW documentation)
        """
        self.size = tuple(size)
        self.mode = mode
        self.image = None
        self._dtype = 'bool' if self.mode == '1' else 'uint8'
        self._full_size = size + (3,) if mode.lower() == 'rgb' else size
        self._nchannels = 3 if mode.lower() == 'rgb' else 1
        self._max_value = 2 if self.mode == '1' else 256

    def create(self, color=None):
        """
        Create image with given background color

        :param color: image background color (see PILLOW documentation)
                    color is RGB tuple or color string if self.mode is 'RGB'
                    color is int otherwise
                    if color is None the background color is chosen randomly
        :return: PILLOW Image object
        """
        if color is not None:
            try:
                self.image = Image.new(self.mode, self.size, color)
            except:
                self.image = Image.new(self.mode, self.size, tuple(color))
        else:
            color_matrix = np.random.randint(0, self._max_value, self._full_size, dtype=self._dtype)
            self.image = Image.fromarray(color_matrix)
        return self.image

    def to_array(self):
        """
        Convert image into numpy array

        :return: numpy array
        """
        return np.array(self.image)

    def save(self, filename, format='PNG'):
        """
        Save image to given file

        :param filename: string
        :param format: default is 'PNG' (see PILLOW documentation)
        :return: None
        """
        self.image.save(filename, format)
