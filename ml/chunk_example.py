import json
import time

from ml.chunkers import RecursiveChunker

with open("server/RAG/data_text_true_full.json", "r", encoding="utf-8") as file:
    data = json.load(file)


recursive_splitter = RecursiveChunker(chunk_overlap=75, chunk_size=512)
text = []
metadata_recursive = []
for item in data:
    # здесь сохраняем текста в отдельный список, которые будут разбиваться на части
    text.append(item.pop("text"))
    # если надо что-то удалить из полных данных
    del item["id"]
    # метаданные по каждому тексту (например, uuid документа, но можно добавить и другие данные)
    metadata_recursive.append(item)

start = time.time()
print("Начинаем разбиение текста")
docs_recursive = recursive_splitter.create_documents(text, metadata_recursive)
chunking_recursive = recursive_splitter.split_documents(docs_recursive)
print(
    f"Разбиение {len(docs_recursive)} документов при помощи RecursiveChunker на {len(chunking_recursive)} частей заняло {time.time() - start} секунд"
)
start_sentence = time.time()
all_documents = docs_recursive
all_chunks = chunking_recursive
print(
    f"Общее количество документов: {len(all_documents)}\nОбщее количество частей: {len(all_chunks)}\nОбщее время: {time.time() - start}"
)


with open("data_text_chunked_rec.json", "w", encoding="utf-8") as file:
    json.dump(
        [item.to_dict() for item in all_chunks], file, ensure_ascii=False, indent=1
    )
