import os

from PIL import Image


def create_save_path(image_path: str, size) -> str:
    basedir = os.path.dirname(image_path)
    image_name_list = os.path.basename(image_path).split('.')
    size_name = f'-{size[0]}x{size[1]}'
    name_before_extension = '.'.join(image_name_list[:-1]) + size_name
    fname = '.'.join([name_before_extension, image_name_list[-1]])
    return os.path.join(basedir, fname)


def resize(image_path, size, color):
    canvas = Image.new('RGB', size, color)
    # img_draw = ImageDraw.Draw(canvas)
    image = Image.open(image_path)
    if image.size == size:  # Dont do anything image is in proper size already
        return image_path
    image.thumbnail(size)
    position = ((canvas.width - image.width)//2,
                (canvas.height - image.height)//2)
    canvas.paste(image, position)
    save_path = create_save_path(image_path, size)
    canvas.save(save_path)
    return save_path


if __name__ == '__main__':
    resize('ted.jpg', (640, 320), 'red')
