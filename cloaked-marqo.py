import asyncio
import marqo
import pprint
import ironcore_alloy
import time


def head_context(list):
    return f"[{list[0]}, {list[1]}, {list[2]}, {list[3]}, {list[4]}, ..]"


async def main() -> None:
    # sample OpenAI ada-002 embeddings generated from the nfcorpus dataset of documents and queries
    # can be found [here](https://github.com/skeet70/beir-openai-embeddings/) if you'd like "real"
    # data.
    # replace with your own embedding dimensionality
    dimensions = 768

    # replace with your own document embeddings
    doc1 = [-0.1234, 0.5678, 0.9012, -0.3456] * 192  # must match index dimensionality
    doc2 = [-0.4321, 0.8765, 0.2222, -0.3333] * 192  # must match index dimensionality

    # replace with your own query embedding
    query = [-0.3333, 0.5555, 0.9021, -0.3556] * 192  # must match index dimensionality

    # print out a few values of the plaintext vectors
    print(f"doc1 {head_context(doc1)}")
    print(f"doc2 {head_context(doc2)}")
    print(f"query {head_context(query)}")

    ##
    ## Encrypt our document and query embeddings with IronCore Labs Cloaked AI
    ##
    encryption_secret_key = ironcore_alloy.Secret(
        "awholelotoftotallyrandomdatathatcanbeusedasasecurecryptokey".encode("utf-8")
    )
    standalone_mode_secret = ironcore_alloy.StandaloneSecret(1, encryption_secret_key)
    # encryption keys can be rotated
    rotatable_secret = ironcore_alloy.RotatableSecret(standalone_mode_secret, None)
    # this can be adjusted to achieve a balance of security and search accuracy
    approximation_factor = 2.0
    # used when encrypting embedding vectors
    vector_secrets = {
        "secret_path": ironcore_alloy.VectorSecret(
            approximation_factor, rotatable_secret
        )
    }
    # standard secrets, used if you want to store encrypted data alongside your vectors,
    # not used in this example
    standard_secrets = ironcore_alloy.StandardSecrets(None, [])
    ironcore_config = ironcore_alloy.StandaloneConfiguration(
        standard_secrets,
        # deterministic secrets, used if you want encrypted data alongside your vectors
        # that can be exact matched on, not used in this example
        {},
        vector_secrets,
    )
    ironcore_sdk = ironcore_alloy.Standalone(ironcore_config)
    metadata = ironcore_alloy.AlloyMetadata.new_simple("")

    # encrypt the vectors
    encrypted_doc1 = (
        await ironcore_sdk.vector().encrypt(
            ironcore_alloy.PlaintextVector(doc1, "secret_path", ""), metadata
        )
    ).encrypted_vector
    encrypted_doc2 = (
        await ironcore_sdk.vector().encrypt(
            ironcore_alloy.PlaintextVector(doc2, "secret_path", ""), metadata
        )
    ).encrypted_vector
    encrypted_query = (
        await ironcore_sdk.vector().generate_query_vectors(
            {"query": ironcore_alloy.PlaintextVector(query, "secret_path", "")},
            metadata,
        )
    )["query"][0].encrypted_vector

    # print out a few values of the encrypted vectors
    print(f"doc1 {head_context(encrypted_doc1)}")
    print(f"doc2 {head_context(encrypted_doc2)}")
    print(f"query {head_context(encrypted_query)}")

    ##
    ## Ingest the encrypted documents into Marqo AI and query with the encrypted query
    ##
    mq = marqo.Client(url="http://localhost:8882")

    mq.index("my-first-index").delete()

    index_settings = {
        "index_defaults": {
            "model": "no_model",
            "model_properties": {"dimensions": dimensions},
        },
    }

    mq.create_index("my-first-index", settings_dict=index_settings)

    # Define any raw (encrypted) embedding fields here
    my_mappings = {
        "my_custom_encrypted_vector": {"type": "custom_vector"},
    }

    mq.index("my-first-index").add_documents(
        documents=[
            {
                "_id": "doc1",
                "my_custom_encrypted_vector": {
                    "vector": encrypted_doc1,
                    "content": "encrypted document",
                },
            },
            {
                "_id": "doc2",
                "my_custom_encrypted_vector": {
                    "vector": encrypted_doc2,
                    "content": "encrypted document",
                },
            },
        ],
        tensor_fields=["my_custom_encrypted_vector"],
        mappings=my_mappings,
    )

    # wait for opensearch indexing to take place
    time.sleep(5)

    results = mq.index("my-first-index").search(
        context={
            "tensor": [
                {
                    "vector": encrypted_query,
                    "weight": 1,
                }
            ]
        },
    )

    pprint.pprint(results)


if __name__ == "__main__":
    asyncio.run(main())
