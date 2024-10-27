from typing import List
from docx import Document

from ml.documents import Document as Doc
from PIL import Image
from io import BytesIO
import zipfile
from loguru import logger
from ml.embedders import EmbeddingGenerator
from ml.models import Paragraph, Chunk
from repositories.clickhouse import ClickhouseRepository
from ml.chunkers import RecursiveChunker
from schemas.clickhouse import CreateChunkOpts, CreateParagraphOpts
import os

from services.minio import MinioService
from utils.types import MinioContentType


def extract_images_to_memory(docx_path: str) -> List[BytesIO]:
    """
    Извлекает изображения из файла .docx и сохраняет их в памяти в виде объектов BytesIO.

    - docx_path (str): Путь к файлу .docx.

    - List[BytesIO]: Список изображений в памяти (объекты BytesIO).
    """
    image_files = []
    with zipfile.ZipFile(docx_path, "r") as docx_zip:
        for file in docx_zip.namelist():
            if file.startswith("word/media/"):
                image_data = BytesIO(docx_zip.read(file))
                image_files.append(image_data)
    return image_files


def parse_docx(
    repo: ClickhouseRepository, static_storage: MinioService, docx_path: str
) -> List[Paragraph]:
    """
    Парсит документ .docx и извлекает параграфы, а также сохраняет их в ClickhouseRepository.

    Параметры:
    - repo (ClickhouseRepository): Репозиторий для сохранения объектов Paragraph.
    - docx_path (str): Путь к файлу .docx.

    Возвращает:
    - List[Paragraph]: Список объектов Paragraph.
    """
    document = Document(docx_path)
    paragraphs = []
    current_section_num = 0
    current_section_name = None
    current_section_text = []
    current_section_images = []

    image_files = extract_images_to_memory(docx_path)
    image_counter = 0

    for para in document.paragraphs:
        style_name = para.style.name
        text = para.text.strip()

        if style_name == "Heading 2":
            if current_section_name:
                section_text_combined = "\n".join(current_section_text).strip()
                paragraph_obj = Paragraph(
                    name=current_section_name,
                    text=section_text_combined,
                    num=str(current_section_num),
                    image_binaries=current_section_images,
                )
                paragraphs.append(paragraph_obj)

            current_section_num += 1
            current_section_name = text
            current_section_text = []
            current_section_images = []

        elif style_name != "Heading 2" and text:
            if current_section_name:
                current_section_text.append(text)

        # Associate images with paragraphs
        if "Рисунок".lower() in text.lower():
            if image_counter < len(image_files):
                current_section_images.append(image_files[image_counter])
                image_counter += 1

    if current_section_name:
        section_text_combined = "\n".join(current_section_text).strip()
        paragraph_obj = Paragraph(
            name=current_section_name,
            text=section_text_combined,
            num=str(current_section_num),
            image_binaries=current_section_images,
        )
        paragraphs.append(paragraph_obj)

    for paragraph in paragraphs:
        for index, image in enumerate(paragraph.image_binaries):
            path = static_storage.create_object_from_byte(
                object_path=f"images/{paragraph.id}/{index}",
                file=image,
                content_type=MinioContentType.PNG,
            )

            paragraph.image_paths.append(path)

        repo.create_paragraph(
            CreateParagraphOpts(
                id=paragraph.id,
                name=paragraph.name,
                text=paragraph.text,
                num=paragraph.num,
                images={
                    f"Image_{i+1}": image
                    for i, image in enumerate(paragraph.image_paths)
                },
            )
        )

    return paragraphs


def append_to_clickhouse(repo: ClickhouseRepository, chunks: List[Chunk]):
    """
    Сохраняет данные в ClickHouse.

    Параметры:
    - chunks (List[Chunk]): Список чанков для сохранения.
    """
    # Мокированная функция - требуется реализация пользователем
    logger.info("Сохранение данных в ClickHouse.")

    for chunk in chunks:
        repo.create_chunk(
            CreateChunkOpts(
                id=chunk.id,
                emb=chunk.emb,
                text=chunk.text,
                paragraph_id=chunk.paragraph_uuid,
            )
        )


def chunk_paragraphs(paragraphs: List[Paragraph]) -> List[Chunk]:
    """
    Разбивает параграфы на чанки с помощью RecursiveChunker и добавляет UUID параграфа в метаданные.

    Параметры:
    - paragraphs (List[Paragraph]): Список параграфов для обработки.

    Возвращает:
    - List[Chunk]: Список созданных чанков.
    """
    if not paragraphs:
        logger.error("Список параграфов пуст.")
        raise ValueError("Список параграфов пуст.")

    chunks = []

    # Инициализируем RecursiveChunker
    try:
        recursive_splitter = RecursiveChunker(chunk_overlap=32, chunk_size=256)
        logger.info("RecursiveChunker успешно инициализирован.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации RecursiveChunker: {e}")
        raise RuntimeError(f"Не удалось инициализировать RecursiveChunker: {e}")

    for paragraph in paragraphs:
        if not paragraph.text:
            logger.warning(f"Параграф с UUID {paragraph.id} не содержит текста.")
            continue

        # Создаем документ для параграфа
        doc = Doc(
            page_content=paragraph.text,
            metadata={
                "paragraph_uuid": str(paragraph.id),
                "name_paragraph": paragraph.name,
                "num_paragraph": paragraph.num,
            },
        )

        # Разбиваем документ на чанки
        try:
            paragraph_chunks = recursive_splitter.split_documents([doc])
            logger.debug(
                f"Параграф {paragraph.id} разбит на {len(paragraph_chunks)} чанков."
            )
        except Exception as e:
            logger.error(f"Ошибка при разбиении параграфа {paragraph.id} на чанки: {e}")
            continue

        # Создаем объекты Chunk из полученных чанков
        for chunk_doc in paragraph_chunks:
            chunk = Chunk(text=chunk_doc.page_content, paragraph_uuid=paragraph.id)
            chunks.append(chunk)

        logger.debug(f"Создан текстовый чанк для параграфа {paragraph.id}")

        # Обрабатываем изображения в параграфе
        for idx, image_bin in enumerate(paragraph.image_binaries):
            chunk = Chunk(image=True, binary=image_bin, paragraph_uuid=paragraph.id)

            chunks.append(chunk)

        logger.debug(f"Создан визуальный чанк для параграфа {paragraph.id}")

    if not chunks:
        logger.error("Не удалось создать чанки из предоставленных параграфов.")
        raise RuntimeError("Чанки не были созданы из параграфов.")

    logger.info(f"Всего создано {len(chunks)} чанков из параграфов.")
    return chunks


def generate_embeddings_for_chunks(
    chunks: List[Chunk], embedding_generator: EmbeddingGenerator
) -> None:
    """
    Генерирует эмбеддинги для каждого чанка (текст или изображение) и сохраняет их в объекте Chunk.

    Параметры:
    - chunks (List[Chunk]): Список чанков.
    - embedding_generator (EmbeddingGenerator): Экземпляр класса для генерации эмбеддингов.
    """
    if not chunks:
        logger.error("Список чанков пуст.")
        raise ValueError("Chunk list is empty.")

    text_chunks = []
    image_chunks = []
    for chunk in chunks:
        if chunk.image:
            image_chunks.append(chunk)
        else:
            text_chunks.append(chunk)

    # Генерируем эмбеддинги для текстовых чанков
    if text_chunks:
        texts = [chunk.text for chunk in text_chunks]
        try:
            embeddings = embedding_generator.get_text_embedding(texts)
            for idx, chunk in enumerate(text_chunks):
                chunk.emb = embeddings[idx].tolist()
            logger.info(
                f"Эмбеддинги для {len(text_chunks)} текстовых чанков сгенерированы."
            )
        except Exception as e:
            logger.error(f"Ошибка при генерации эмбеддингов текстовых чанков: {e}")
            raise

    # Генерируем эмбеддинги для чанков изображений
    if image_chunks:
        for idx, chunk in enumerate(image_chunks):
            image = Image.open(chunk.binary)
            embeddings = embedding_generator.get_image_embedding([image])
            embeddings = embeddings.squeeze().tolist()

            chunk.emb = embeddings
            chunk.text = "image"

        logger.info(
            f"Эмбеддинги для {len(image_chunks)} визуальных чанков сгенерированы."
        )


def docs2clickhouse(
    repo: ClickhouseRepository, static_storage: MinioService, docx_path: str
):
    """
    Основная функция для обработки документа .docx и сохранения данных в ClickHouse.

    Параметры:
    - docx_path (str): Путь к файлу .docx.
    """
    if not os.path.exists(docx_path):
        logger.error(f"Файл документа '{docx_path}' не найден.")
        raise FileNotFoundError(f"Document file '{docx_path}' not found.")

    # Шаг 1: Парсинг документа
    try:
        paragraphs = parse_docx(repo, static_storage, docx_path)
        logger.info(
            f"Парсинг документа завершен. Найдено {len(paragraphs)} параграфов."
        )
    except Exception as e:
        logger.error(f"Ошибка при парсинге документа: {e}")
        raise RuntimeError(f"Error parsing document: {e}")

    if not paragraphs:
        logger.error("Парсинг документа не вернул ни одного параграфа.")
        raise RuntimeError("No paragraphs were parsed from the document.")

    # Шаг 2: Разбиваем параграфы на чанки и добавляем UUID параграфа в метаданные
    try:
        chunks = chunk_paragraphs(paragraphs)
        logger.info(
            f"Разбиение параграфов на чанки завершено. Всего чанков: {len(chunks)}."
        )
    except Exception as e:
        logger.error(f"Ошибка при разбиении параграфов на чанки: {e}")
        raise RuntimeError(f"Error chunking paragraphs: {e}")

    # Шаг 3: Генерируем эмбеддинги для чанков (как текстовых, так и изображений)
    try:
        embedding_generator = EmbeddingGenerator()
        generate_embeddings_for_chunks(chunks, embedding_generator)
        logger.info("Генерация эмбеддингов для всех чанков завершена.")
    except Exception as e:
        logger.error(f"Ошибка при генерации эмбеддингов: {e}")
        raise RuntimeError(f"Error generating embeddings: {e}")
    # Шаг 4: Сохранение данных в ClickHouse
    try:
        append_to_clickhouse(repo, chunks)
        logger.info("Данные успешно сохранены в ClickHouse.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в ClickHouse: {e}")
        raise RuntimeError(f"Error saving data to ClickHouse: {e}")

    logger.info("Обработка документа завершена успешно.")


# Пример использования
if __name__ == "__main__":
    from services.minio import MinioService
    from configs.Environment import get_environment_variables
    from minio import Minio

    docx_path = "ml/test_data/data.docx"
    repo = ClickhouseRepository()
    env = get_environment_variables()

    minio_client = Minio(
        env.MINIO_HOST,
        access_key=env.MINIO_ACCESS,
        secret_key=env.MINIO_SECRET,
        secure=False if env.ENV == "LOCAL" else True,
    )

    static_storage = MinioService(minio_client)

    embedding_generator = EmbeddingGenerator()
    try:
        docs2clickhouse(repo, static_storage, docx_path)
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке: {e}")
