import os

from PIL import Image


def create_save_path(image_path: str, save_path: str, size) -> str:
    image_name_list = os.path.basename(image_path).split('.')
    size_name = f'-{size[0]}x{size[1]}'
    name_before_extension = '.'.join(image_name_list[:-1]) + size_name
    # fname = '.'.join([name_before_extension, image_name_list[-1]])
    fname = '.'.join([name_before_extension, 'png'])
    return os.path.join(save_path, fname)


def resize(image_path, save_path: str, size, color):
    canvas = Image.new('RGBA', size, color)
    image = Image.open(image_path)
    if image.size == size:  # Dont do anything image is in proper size already
        return image_path
    image.thumbnail(size, Image.NEAREST)
    position = ((canvas.width - image.width)//2,
                (canvas.height - image.height)//2)
    canvas.paste(image, position, image)
    save_path = create_save_path(image_path, save_path, size)
    # Image.alpha_composite(canva, image).save(save)
    canvas.save(save_path)
    return save_path


if __name__ == '__main__':
    resize("C:\\Users\\tedla\Pictures\\ted.png", '', (640, 320), 'red')
