from PIL import Image
from io import BytesIO


def image_to_bytes(image_path):
    with open(image_path, "rb") as f:
        return f.read()


def bytes_to_qpixmap(image_bytes):
    from PyQt5.QtGui import QPixmap
    pixmap = QPixmap()
    pixmap.loadFromData(image_bytes)
    return pixmap


def resize_cover(image_bytes, size=(200, 200)):
    """
    Изменяет размер обложки и конвертирует её в RGB JPEG.
    Решает проблему с RGBA.
    """
    img = Image.open(BytesIO(image_bytes))
    img.thumbnail(size)

    # Если есть альфа-канал, конвертируем в RGB
    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (0, 0, 0))
        background.paste(img, mask=img.split()[3])  # 3 = альфа-канал
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()
