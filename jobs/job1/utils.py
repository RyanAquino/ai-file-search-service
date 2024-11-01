import uuid


def format_pinecone_payload(extracted_texts, embeddings, filename) -> list[dict]:
    """
    Formats the texts with its embeddings and metadata.

    :param extracted_texts: list of extracted texts type list[str]
    :param embeddings: list of embeddings
    :param filename: filename as file_id
    :return: list of objects ready for pinecone upsert
    """
    index_payload = []

    for txt, embedding in zip(extracted_texts, embeddings):
        index_payload.append(
            {
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {"text": txt, "file_id": filename},
            }
        )

    return index_payload
