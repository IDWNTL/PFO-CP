import io
from typing import List
import uuid


class Paragraph:
    """
    Класс, представляющий параграф документа.
    """

    def __init__(
        self,
        name: str,
        text: str,
        num: str,
        image_binaries: List[io.BytesIO] = None,
        image_paths: List[str] = None,
        image_texts: List[str] = None,
    ):
        self.id = uuid.uuid4()
        self.name = name
        self.text = text
        self.num = num
        self.image_binaries = image_binaries if image_binaries else []
        self.image_paths = image_paths if image_paths else []
        self.image_texts = image_texts if image_texts else []


class Chunk:
    """
    Класс, представляющий чанк текста или изображения.
    """

    def __init__(
        self,
        text: str = None,
        emb: List[float] = None,
        paragraph_uuid: uuid.UUID = None,
        image: bool = False,
        binary: io.BytesIO = None,
    ):
        self.id = uuid.uuid4()
        self.text = text
        self.emb = emb if emb else []
        self.image = image
        self.binary = binary
        self.paragraph_uuid = paragraph_uuid
