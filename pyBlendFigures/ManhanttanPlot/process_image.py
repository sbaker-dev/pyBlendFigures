from imageObjects import ImageObject
from imageObjects.Support import load_image


a = ImageObject(load_image(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\ManhattanTests\untitled.png", 4))
print(a)


c = a.blank_like(True)
c.change_bgra_to_bgr()


b = a.mask_alpha(True)

b.change_bgra_to_bgr()
b.change_to_mono()

c.change_a_colour((0, 0, 0), (160, 80, 0))

c.mask_on_image(b)


a.change_bgra_to_bgr()

a.overlay_image(c, 0, 0)

a.change_bgr_to_bgra()

a.assign_alpha_channel(b)

# print(type(rgba))
#
# b.show()
#
# cv2.imwrite(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\ManhattanTests\Name2.png", rgba)

a.write_to_file(r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\ManhattanTests", "Plot2")