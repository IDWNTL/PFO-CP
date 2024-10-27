from yandex_cloud_ml_sdk import YCloudML

from configs.Environment import get_environment_variables

env = get_environment_variables()

sdk = YCloudML(folder_id=env.YANDEX_FOLDER_ID, auth=env.YANDEX_TOKEN)

yandexGPT = sdk.models.completions("yandexgpt").langchain(model_type="chat", timeout=60)
