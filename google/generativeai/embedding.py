# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Sequence, Mapping
import itertools
from typing import Iterable, overload, TypeVar, Union, Mapping

import google.ai.generativelanguage as glm

from google.generativeai.client import get_default_generative_client
from google.generativeai.client import get_default_generative_async_client

from google.generativeai import string_utils
from google.generativeai.types import text_types
from google.generativeai.types import model_types
from google.generativeai.types import content_types

_EMBED_CONTENT_ASYNC_DOC = """The async version of `genai.embed_content`."""

_EMBED_CONTENT_DOC = """Calls the API to create embeddings for content passed in.

    Args:
        model:
            Which [model](https://ai.google.dev/models/gemini#embedding) to
            call, as a string or a `types.Model`.

        content:
            Content to embed.

        task_type:
            Optional task type for which the embeddings will be used. Can only
            be set for `models/embedding-001`.

        title:
            An optional title for the text. Only applicable when task_type is
            `RETRIEVAL_DOCUMENT`.

    Return:
        Dictionary containing the embedding (list of float values) for the
        input content.
    """

DEFAULT_EMB_MODEL = "models/embedding-001"
EMBEDDING_MAX_BATCH_SIZE = 100

EmbeddingTaskType = glm.TaskType

EmbeddingTaskTypeOptions = Union[int, str, EmbeddingTaskType]

_EMBEDDING_TASK_TYPE: dict[EmbeddingTaskTypeOptions, EmbeddingTaskType] = {
    EmbeddingTaskType.TASK_TYPE_UNSPECIFIED: EmbeddingTaskType.TASK_TYPE_UNSPECIFIED,
    0: EmbeddingTaskType.TASK_TYPE_UNSPECIFIED,
    "task_type_unspecified": EmbeddingTaskType.TASK_TYPE_UNSPECIFIED,
    "unspecified": EmbeddingTaskType.TASK_TYPE_UNSPECIFIED,
    EmbeddingTaskType.RETRIEVAL_QUERY: EmbeddingTaskType.RETRIEVAL_QUERY,
    1: EmbeddingTaskType.RETRIEVAL_QUERY,
    "retrieval_query": EmbeddingTaskType.RETRIEVAL_QUERY,
    "query": EmbeddingTaskType.RETRIEVAL_QUERY,
    EmbeddingTaskType.RETRIEVAL_DOCUMENT: EmbeddingTaskType.RETRIEVAL_DOCUMENT,
    2: EmbeddingTaskType.RETRIEVAL_DOCUMENT,
    "retrieval_document": EmbeddingTaskType.RETRIEVAL_DOCUMENT,
    "document": EmbeddingTaskType.RETRIEVAL_DOCUMENT,
    EmbeddingTaskType.SEMANTIC_SIMILARITY: EmbeddingTaskType.SEMANTIC_SIMILARITY,
    3: EmbeddingTaskType.SEMANTIC_SIMILARITY,
    "semantic_similarity": EmbeddingTaskType.SEMANTIC_SIMILARITY,
    "similarity": EmbeddingTaskType.SEMANTIC_SIMILARITY,
    EmbeddingTaskType.CLASSIFICATION: EmbeddingTaskType.CLASSIFICATION,
    4: EmbeddingTaskType.CLASSIFICATION,
    "classification": EmbeddingTaskType.CLASSIFICATION,
    EmbeddingTaskType.CLUSTERING: EmbeddingTaskType.CLUSTERING,
    5: EmbeddingTaskType.CLUSTERING,
    "clustering": EmbeddingTaskType.CLUSTERING,
}


def to_task_type(x: EmbeddingTaskTypeOptions) -> EmbeddingTaskType:
    if isinstance(x, str):
        x = x.lower()
    return _EMBEDDING_TASK_TYPE[x]


try:
    # python 3.12+
    _batched = itertools.batched  # type: ignore
except AttributeError:
    T = TypeVar("T")

    def _batched(iterable: Iterable[T], n: int) -> Iterable[list[T]]:
        if n < 1:
            raise ValueError(f"Batch size `n` must be >0, got: {n}")
        batch = []
        for item in iterable:
            batch.append(item)
            if len(batch) == n:
                yield batch
                batch = []

        if batch:
            yield batch


@overload
def embed_content(
    model: model_types.BaseModelNameOptions,
    content: content_types.ContentType,
    task_type: EmbeddingTaskTypeOptions | None = None,
    title: str | None = None,
    client: glm.GenerativeServiceClient | None = None,
) -> text_types.EmbeddingDict: ...


@overload
def embed_content(
    model: model_types.BaseModelNameOptions,
    content: Iterable[content_types.ContentType],
    task_type: EmbeddingTaskTypeOptions | None = None,
    title: str | None = None,
    client: glm.GenerativeServiceClient | None = None,
) -> text_types.BatchEmbeddingDict: ...


@string_utils.set_doc(_EMBED_CONTENT_DOC)
def embed_content(
    model: model_types.BaseModelNameOptions,
    content: content_types.ContentType | Iterable[content_types.ContentType],
    task_type: EmbeddingTaskTypeOptions | None = None,
    title: str | None = None,
    client: glm.GenerativeServiceClient = None,
) -> text_types.EmbeddingDict | text_types.BatchEmbeddingDict:
    model = model_types.make_model_name(model)

    if client is None:
        client = get_default_generative_client()

    if title and to_task_type(task_type) is not EmbeddingTaskType.RETRIEVAL_DOCUMENT:
        raise ValueError(
            "If a title is specified, the task must be a retrieval document type task."
        )

    if task_type:
        task_type = to_task_type(task_type)

    if isinstance(content, Iterable) and not isinstance(content, (str, Mapping)):
        result = {"embedding": []}
        requests = (
            glm.EmbedContentRequest(
                model=model, content=content_types.to_content(c), task_type=task_type, title=title
            )
            for c in content
        )
        for batch in _batched(requests, EMBEDDING_MAX_BATCH_SIZE):
            embedding_request = glm.BatchEmbedContentsRequest(model=model, requests=batch)
            embedding_response = client.batch_embed_contents(embedding_request)
            embedding_dict = type(embedding_response).to_dict(embedding_response)
            result["embedding"].extend(e["values"] for e in embedding_dict["embeddings"])
        return result
    else:
        embedding_request = glm.EmbedContentRequest(
            model=model, content=content_types.to_content(content), task_type=task_type, title=title
        )
        embedding_response = client.embed_content(embedding_request)
        embedding_dict = type(embedding_response).to_dict(embedding_response)
        embedding_dict["embedding"] = embedding_dict["embedding"]["values"]
        return embedding_dict


@overload
async def embed_content_async(
    model: model_types.BaseModelNameOptions,
    content: content_types.ContentType,
    task_type: EmbeddingTaskTypeOptions | None = None,
    title: str | None = None,
    client: glm.GenerativeServiceAsyncClient | None = None,
) -> text_types.EmbeddingDict: ...


@overload
async def embed_content_async(
    model: model_types.BaseModelNameOptions,
    content: Iterable[content_types.ContentType],
    task_type: EmbeddingTaskTypeOptions | None = None,
    title: str | None = None,
    client: glm.GenerativeServiceAsyncClient | None = None,
) -> text_types.BatchEmbeddingDict: ...


@string_utils.set_doc(_EMBED_CONTENT_ASYNC_DOC)
async def embed_content_async(
    model: model_types.BaseModelNameOptions,
    content: content_types.ContentType | Iterable[content_types.ContentType],
    task_type: EmbeddingTaskTypeOptions | None = None,
    title: str | None = None,
    client: glm.GenerativeServiceAsyncClient = None,
) -> text_types.EmbeddingDict | text_types.BatchEmbeddingDict:
    model = model_types.make_model_name(model)

    if client is None:
        client = get_default_generative_async_client()

    if title and to_task_type(task_type) is not EmbeddingTaskType.RETRIEVAL_DOCUMENT:
        raise ValueError(
            "If a title is specified, the task must be a retrieval document type task."
        )

    if task_type:
        task_type = to_task_type(task_type)

    if isinstance(content, Iterable) and not isinstance(content, (str, Mapping)):
        result = {"embedding": []}
        requests = (
            glm.EmbedContentRequest(
                model=model, content=content_types.to_content(c), task_type=task_type, title=title
            )
            for c in content
        )
        for batch in _batched(requests, EMBEDDING_MAX_BATCH_SIZE):
            embedding_request = glm.BatchEmbedContentsRequest(model=model, requests=batch)
            embedding_response = await client.batch_embed_contents(embedding_request)
            embedding_dict = type(embedding_response).to_dict(embedding_response)
            result["embedding"].extend(e["values"] for e in embedding_dict["embeddings"])
        return result
    else:
        embedding_request = glm.EmbedContentRequest(
            model=model, content=content_types.to_content(content), task_type=task_type, title=title
        )
        embedding_response = await client.embed_content(embedding_request)
        embedding_dict = type(embedding_response).to_dict(embedding_response)
        embedding_dict["embedding"] = embedding_dict["embedding"]["values"]
        return embedding_dict
