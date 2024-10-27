from transformers import pipeline
import torch


def load_toxic_model(model_path: str):
    """
    Загружает модель для классификации токсичных текстов.
    """
    pipe = pipeline("text-classification", model=model_path, device="cpu")
    return pipe


def is_toxic(pipe, input_text: str) -> bool:
    """
    Определяет, является ли вводимый текст токсичным.

    Args:
        pipe: Предварительно загруженная модель классификации токсичности.
        input_text (str): Текст для классификации.

    Returns:
        bool: True, если текст токсичен, False в противном случае.
    """

    with torch.no_grad():
        return True if pipe(input_text)[0]["label"] == "toxic" else False


if __name__ == "__main__":
    model_path = "ml/preloaded_models/toxic-classifier"
    pipe = load_toxic_model(model_path)
    text = """Чужой контент без разрешения автора или правообладателя. Например, музыку, видео и изображения из общего доступа, записи концертов, фильмов, аудиокниги, фрагменты новостных сюжетов из ТВ-эфиров, видео популярных блогеров, трансляции спортивных событий.
Рекламу трансцендентных услуг. Например, рекламу гаданий, услуг ясновидящих, экстрасенсов и т. д.
Откровенно сексуальный контент. Например, танцы в откровенных костюмах, рекламу интим-товаров или сексуальных услуг. 
Рекламу букмекеров, проведение ставок и пропаганду любых азартных игр. 
Рекламу или продвижение финансовых пирамид и сетевого маркетинга (MLM), преподнесение их в качестве надёжного источника заработка.  
Нецензурную брань, оскорбления, подстрекательства к незаконным действиям. 
Контент, который нацелен только на перенаправление зрителей на другие сайты. 
Контент иностранных агентов или о них без специальной маркировки.
Больше информации есть по ссылкам:

https://rutube.ru/info/taboo_agreement/
https://rutube.ru/info/socially_important/
https://rutube.ru/info/adverguide/
https://rutube.ru/info/content/"""
    result = is_toxic(pipe, text)
    print("Is toxic:", result)
