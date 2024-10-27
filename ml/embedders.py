from typing import List
import torch
from PIL import Image
from loguru import logger
import open_clip


class EmbeddingGenerator:
    """
    Класс для генерации эмбеддингов текста и изображений с использованием мультиязычной модели OpenCLIP.
    """

    def __init__(
        self, model_name: str = "ViT-B-32", pretrained: str = "laion2b_s34b_b79k"
    ):
        """
        Инициализирует модель OpenCLIP для последующего использования.

        Параметры:
        - model_name (str): Название архитектуры модели.с
        - pretrained (str): Название предобученной модели.
        """
        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                model_name, pretrained=pretrained, device=self.device
            )
            self.tokenizer = open_clip.get_tokenizer(model_name)
            logger.info(
                f"Модель OpenCLIP {model_name} ({pretrained}) успешно загружена."
            )
        except Exception as e:
            logger.error(f"Не удалось загрузить модель OpenCLIP: {e}")
            raise RuntimeError(f"Failed to load OpenCLIP model: {e}")

    def get_text_embedding(self, texts: List[str]) -> torch.Tensor:
        """
        Преобразует список текстов в эмбеддинги с помощью модели OpenCLIP.

        Параметры:
        - texts (List[str]): Список текстовых строк для преобразования.

        Возвращает:
        - torch.Tensor: Тензор эмбеддингов для каждого текста.
        """
        if not texts:
            logger.error("Входной список текстов пуст.")
            raise ValueError("Input text list is empty.")

        try:
            with torch.no_grad():
                tokens = self.tokenizer(texts).to(self.device)
                embeddings = self.model.encode_text(tokens)
                embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
            logger.debug("Эмбеддинги текстов успешно сгенерированы.")
            return embeddings.cpu()
        except Exception as e:
            logger.error(f"Ошибка при генерации эмбеддингов текста: {e}")
            raise

    def get_image_embedding(self, images: List[Image.Image]) -> torch.Tensor:
        """
        Преобразует список изображений в эмбеддинги с помощью модели OpenCLIP.

        Параметры:
        - images (List[Image.Image]): Список объектов PIL Image.

        Возвращает:
        - torch.Tensor: Тензор эмбеддингов для каждого изображения.
        """
        if not images:
            logger.error("Входной список изображений пуст.")
            raise ValueError("Input image list is empty.")

        try:
            image_tensors = [self.preprocess(image).unsqueeze(0) for image in images]
            images_tensor = torch.cat(image_tensors).to(self.device)
            with torch.no_grad():
                embeddings = self.model.encode_image(images_tensor)
                embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
            logger.debug("Эмбеддинги изображений успешно сгенерированы.")
            return embeddings.cpu()
        except Exception as e:
            logger.error(f"Ошибка при генерации эмбеддингов изображений: {e}")
            raise


if __name__ == "__main__":
    # Пример использования класса EmbeddingGenerator

    # Инициализируем генератор эмбеддингов
    embedding_generator = EmbeddingGenerator()

    # Пример текстов для преобразования
    texts = ["Привет, мир!", "Это пример текста для преобразования в эмбеддинг."]

    # Получаем эмбеддинги текстов
    text_embeddings = embedding_generator.get_text_embedding(texts)
    print("Эмбеддинги текстов:")
    print(text_embeddings)

    # Пример изображений для преобразования
    try:
        images = [Image.open("image1.jpg"), Image.open("image2.jpg")]

        # Получаем эмбеддинги изображений
        image_embeddings = embedding_generator.get_image_embedding(images)
        print("Эмбеддинги изображений:")
        print(image_embeddings)
    except FileNotFoundError:
        print(
            "Изображения 'image1.jpg' и 'image2.jpg' не найдены. Загрузите изображения для получения эмбеддингов."
        )
