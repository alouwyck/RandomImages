import numpy as np
from PIL import Image, ImageDraw


class RandomImage:
    """
    Base class to generate random image
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
                    color is an integer otherwise
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


class Ellipse(RandomImage):
    """
    Class to generate image with randomly drawn ellipse
    """

    def __init__(self, size, mode='RGB'):
        """
        :param size: image size (width, height) in pixels (see PILLOW documentation)
        :param mode: 'RGB' (default), 'L' (8 bit) or '1' (1 bit) (see PILLOW documentation)
        """
        super().__init__(size, mode)
        self.min_width = 0.1  # minimum width of bounding box (percentage of image width)
        self.min_height = 0.1  # minimum height of bounding box (percentage of image height)
        self.box = None  # bounding box (x_llc, y_llc, x_urc, y_urc)

    def _random_box(self):
        """
        Create bounding box of ellipse randomly
        The box is defined by the coordinates of lower left corner (llc) and upper right corner (urc)
        The coordinates are expressed in pixels

        :return: tuple (x_llc, y_llc, x_urc, y_urc)
        """
        box = np.zeros((2, 2))  # [[x_llc, x_urc], [y_llc, y_urc]]
        min_ = [self.min_width, self.min_height]
        for i in range(2):
            while np.diff(box[i]) < min_[i]:
                box[i] = np.sort(np.random.rand(1, 2))
        box[:, 0], box[:, 1] = box[:, 0] * self.size[0], box[:, 1] * self.size[1]
        return tuple(box[:, 0].astype(int)) + tuple(box[:, 1].astype(int))

    def draw(self, box=None, color=None):
        """
        Draw ellipse on the image

        :param box: bounding box (x_llc, y_llc, x_urc, y_urc)
                    if box is None, then a random box is created
        :param color: color of ellipse
                    color is an RGB tuple or color string if self.mode is 'RGB'
                    color is an integer otherwise
                    if color is None, then the color is chosen randomly
        :return: PILLOW image object
        """
        self.box = self._random_box() if box is None else tuple(box)
        image_draw = ImageDraw.Draw(self.image)
        if color is None:
            color = tuple(np.random.randint(0, self._max_value, self._nchannels, self._dtype))
            self._draw(image_draw, color)
        else:
            try:
                self._draw(image_draw, color)
            except:
                self._draw(image_draw, tuple(color))
        return self.image

    def _draw(self, image_draw, color):
        """
        Protected method that calls the right PILLOW method

        :param image_draw: PILLOW ImageDraw.Draw object
        :param color: ellipse color (see PILLOW documentation)
        :return:
        """
        image_draw.ellipse(self.box, fill=color, outline=color)

    def box_to_coord(self):
        """
        Converts self into coordinate arrays x and y

        :return: numpy arrays x and y
        """
        # returns coordinates (x, y) of bounding box vertices
        box = np.array(self.box)
        return box[[0, 0, 2, 2, 0]], box[[1, 3, 3, 1, 1]]


class Circle(Ellipse):
    """
    Class to generate image with randomly drawn circle
    """

    def __init__(self, size, mode='RGB'):
        """
        :param size: image size (width, height) in pixels (see PILLOW documentation)
        :param mode: 'RGB' (default), 'L' (8 bit) or '1' (1 bit) (see PILLOW documentation)
        """
        super().__init__(size, mode)

    def _random_box(self):
        """
        Create bounding square of circle randomly
        The square is defined by the coordinates of lower left corner (llc) and upper right corner (urc)
        The coordinates are expressed in pixels

        :return: tuple (x_llc, y_llc, x_urc, y_urc)
        """
        p = np.random.rand(2, 1)
        s = np.random.rand(1)
        while (s < self.min_width) or np.any(p + s > 1):
            p = np.random.rand(2, 1)
            s = np.random.rand(1)
        box = np.hstack((p, p + s))
        box[:, 0], box[:, 1] = box[:, 0] * self.size[0], box[:, 1] * self.size[1]
        return tuple(box[:, 0].astype(int)) + tuple(box[:, 1].astype(int))