from check_swear import SwearingCheck


def load_swear_model():
    """
    Загружает модель для проверки бранных слов.
    """
    sch = SwearingCheck(reg_pred=True)
    return sch


def has_swear(model, input_text: str) -> bool:
    """
    Проверяет, содержит ли вводимый текст бранные слова.

    Args:
        model: Предварительно загруженная модель SwearingCheck.
        input_text (str): Текст для проверки.

    Returns:
        bool: True, если текст содержит бранные слова, False в противном случае.
    """
    prediction = model.predict([input_text])
    return prediction[0] == 1


# Example usage:
if __name__ == "__main__":
    model = load_swear_model()
    text = "пид0рас"
    result = has_swear(model, text)
    print("Есть вульгарные слова:", result)
