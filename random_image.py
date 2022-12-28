import numpy as np
from PIL import Image, ImageDraw
from polygenerator import random_convex_polygon


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
        :return: self
        """
        if color is not None:
            try:
                self.image = Image.new(self.mode, self.size, color)
            except:
                self.image = Image.new(self.mode, self.size, tuple(color))
        else:
            color_matrix = np.random.randint(0, self._max_value, self._full_size, dtype=self._dtype)
            self.image = Image.fromarray(color_matrix)
        return self

    def to_array(self, normalize=True):
        """
        Convert image into numpy array

        :param normalize: boolean indicating whether uint8 values must be normalized (default) or not
        :return: numpy array
        """
        arr = np.array(self.image)
        if not normalize or self.mode == '1':
            return arr
        else:
            return arr / (self._max_value - 1)

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
        :return: self
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
        return self

    def _draw(self, image_draw, color):
        """
        Protected method that calls PILLOW method ImageDraw.Draw.ellipse

        :param image_draw: PILLOW ImageDraw.Draw object
        :param color: ellipse color (see PILLOW documentation)
        :return: None
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


class Rectangle(Ellipse):
    """
    Class to generate image with randomly drawn rectangle
    """

    def __init__(self, size, mode='RGB'):
        """
        :param size: image size (width, height) in pixels (see PILLOW documentation)
        :param mode: 'RGB' (default), 'L' (8 bit) or '1' (1 bit) (see PILLOW documentation)
        """
        super().__init__(size, mode)
        self.vertices = None  # coordinates of vertices

    def _draw(self, image_draw, color):
        """
        Protected method that calls PILLOW method ImageDraw.Draw.polygon

        :param image_draw: PILLOW ImageDraw.Draw object
        :param color: rectangle color (see PILLOW documentation)
        :return: None
        """
        self.vertices = list(zip(*self.box_to_coord()))
        image_draw.polygon(self.vertices, fill=color, outline=color)


class Square(Rectangle, Circle):
    """
    Class to generate image with randomly drawn square
    """

    def __init__(self, size, mode='RGB'):
        """
        :param size: image size (width, height) in pixels (see PILLOW documentation)
        :param mode: 'RGB' (default), 'L' (8 bit) or '1' (1 bit) (see PILLOW documentation)
        """
        super().__init__(size, mode)

    def _random_box(self):
        """
        Create square randomly
        The square is defined by the coordinates of lower left corner (llc) and upper right corner (urc)
        The coordinates are expressed in pixels

        :return: tuple (x_llc, y_llc, x_urc, y_urc)
        """
        return Circle._random_box(self)

    def _draw(self, image_draw, color):
        """
        Protected method that calls PILLOW method ImageDraw.Draw.polygon

        :param image_draw: PILLOW ImageDraw.Draw object
        :param color: square color (see PILLOW documentation)
        :return: None
        """
        Rectangle._draw(self, image_draw, color)


class Polygon(Rectangle):
    """
    Class to generate image with randomly drawn convex polygon
    """

    def __init__(self, size, n, mode='RGB'):
        """
        :param size: image size (width, height) in pixels (see PILLOW documentation)
        :param n: integer indicating the number of vertices
        :param mode: 'RGB' (default), 'L' (8 bit) or '1' (1 bit) (see PILLOW documentation)
        """
        super().__init__(size, mode)
        self.n = n

    def _draw(self, image_draw, color):
        """
        Protected method that calls PILLOW method ImageDraw.Draw.polygon
        and uses function polygenerator.random_convex_polygon to create a random polygon

        :param image_draw: PILLOW ImageDraw.Draw object
        :param color: square color (see PILLOW documentation)
        :return: None
        """
        if self.vertices is None:
            p = random_convex_polygon(self.n)
            p.append(p[0])
            scale_x = lambda x: self.box[0] + x * (self.box[2] - self.box[0])
            scale_y = lambda y: self.box[1] + y * (self.box[3] - self.box[1])
            self.vertices = [(scale_x(x), scale_y(y)) for (x, y) in p]
        image_draw.polygon(self.vertices, fill=color, outline=color)

