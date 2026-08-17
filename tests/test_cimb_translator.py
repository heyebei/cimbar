from os import path
from unittest import TestCase

from PIL import Image

from cimbar.encode.cimb_translator import CimbDecoder
from cimbar.resources import resource_path


class CimbDecoderTest(TestCase):
    def test_decode_dark(self):
        cimb = CimbDecoder(True, 4, 2)
        img = Image.open(resource_path(path.join('tests', 'sample', '15.png')))
        img = img.convert('RGB')
        decoded, error = cimb.decode_symbol(img)
        self.assertEqual(decoded, 5)
        self.assertEqual(error, 0)

        color = cimb.decode_color(img, 0)
        self.assertEqual(color, 1)

        img2 = Image.open(resource_path(path.join('tests', 'sample', '25.png')))
        img2 = img2.convert('RGB')
        decoded, error = cimb.decode_symbol(img2)
        self.assertEqual(decoded, 5)
        self.assertEqual(error, 0)

        color = cimb.decode_color(img2, 0)
        self.assertEqual(color, 2)
