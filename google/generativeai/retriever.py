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

import re
import string
import dataclasses
from typing import AsyncIterable, Iterable, Optional

import google.ai.generativelanguage as glm

from google.generativeai.client import get_default_retriever_client
from google.generativeai.client import get_default_retriever_async_client
from google.generativeai.types.model_types import idecode_time
from google.generativeai.types import retriever_types


def create_corpus(
    name: str,
    display_name: Optional[str] = None,
    client: glm.RetrieverServiceClient | None = None,
) -> retriever_types.Corpus:
    """
    Create a new `Corpus` in the retriever service, and return it as a `retriever_types.Corpus` instance.

    Users can specify either a name or display_name.

    Args:
        name: The corpus resource name (ID). The name must be alphanumeric and fewer
            than 40 characters.
        display_name: The human readable display name. The display name must be fewer
            than 128 characters. All characters, including alphanumeric, spaces, and
            dashes are supported.

    Return:
        `retriever_types.Corpus` object with specified name or display name.

    Raises:
        ValueError: When the name is not specified or formatted incorrectly.
    """
    if client is None:
        client = get_default_retriever_client()

    corpus = None
    if retriever_types.valid_name(name):
        corpus_name = "corpora/" + name  # Construct the name
        corpus = glm.Corpus(name=corpus_name, display_name=display_name)
    else:
        raise ValueError(retriever_types.NAME_ERROR_MSG.format(length=len(name), name=name))

    request = glm.CreateCorpusRequest(corpus=corpus)
    response = client.create_corpus(request)
    response = type(response).to_dict(response)
    idecode_time(response, "create_time")
    idecode_time(response, "update_time")
    response = retriever_types.Corpus(**response)
    return response


async def create_corpus_async(
    name: str,
    display_name: Optional[str] = None,
    client: glm.RetrieverServiceAsyncClient | None = None,
) -> retriever_types.Corpus:
    """This is the async version of `retriever.create_corpus`."""
    if client is None:
        client = get_default_retriever_async_client()

    corpus = None
    if retriever_types.valid_name(name):
        corpus_name = "corpora/" + name  # Construct the name
        corpus = glm.Corpus(name=corpus_name, display_name=display_name)
    else:
        raise ValueError(retriever_types.NAME_ERROR_MSG.format(length=len(name), name=name))

    request = glm.CreateCorpusRequest(corpus=corpus)
    response = await client.create_corpus(request)
    response = type(response).to_dict(response)
    idecode_time(response, "create_time")
    idecode_time(response, "update_time")
    response = retriever_types.Corpus(**response)
    return response


def get_corpus(name: str, client: glm.RetrieverServiceClient | None = None) -> retriever_types.Corpus:  # fmt: skip
    """
    Fetch a specific `Corpus` from the retriever service.

    Args:
        name: The `Corpus` name.

    Return:
        a `retriever_types.Corpus` of interest.
    """
    if client is None:
        client = get_default_retriever_client()

    request = glm.GetCorpusRequest(name=name)
    response = client.get_corpus(request)
    response = type(response).to_dict(response)
    idecode_time(response, "create_time")
    idecode_time(response, "update_time")
    response = retriever_types.Corpus(**response)
    return response


async def get_corpus_async(name: str, client: glm.RetrieverServiceAsyncClient | None = None) -> retriever_types.Corpus:  # fmt: skip
    """This is the async version of `retriever.get_corpus`."""
    if client is None:
        client = get_default_retriever_async_client()

    request = glm.GetCorpusRequest(name=name)
    response = await client.get_corpus(request)
    response = type(response).to_dict(response)
    idecode_time(response, "create_time")
    idecode_time(response, "update_time")
    response = retriever_types.Corpus(**response)
    return response


def delete_corpus(name: str, force: bool = False, client: glm.RetrieverServiceClient | None = None):  # fmt: skip
    """
    Delete a `Corpus` from the service.

    Args:
        name: The `Corpus` name.
        force: If set to true, any `Document`s and objects related to this `Corpus` will also be deleted.
    """
    if client is None:
        client = get_default_retriever_client()

    request = glm.DeleteCorpusRequest(name=name, force=force)
    client.delete_corpus(request)


async def delete_corpus_async(name: str, force: bool = False, client: glm.RetrieverServiceAsyncClient | None = None):  # fmt: skip
    """This is the async version of `retriever.delete_corpus`."""
    if client is None:
        client = get_default_retriever_async_client()

    request = glm.DeleteCorpusRequest(name=name, force=force)
    await client.delete_corpus(request)


def list_corpora(
    *,
    page_size: Optional[int] = None,
    client: glm.RetrieverServiceClient | None = None,
) -> Iterable[retriever_types.Corpus]:
    """
    List the Corpuses you own in the service.

    Args:
        page_size: Maximum number of `Corpora` to request.
        page_token: A page token, received from a previous ListCorpora call.

    Return:
        Paginated list of `Corpora`.
    """
    if client is None:
        client = get_default_retriever_client()

    request = glm.ListCorporaRequest(page_size=page_size)
    for corpus in client.list_corpora(request):
        corpus = type(corpus).to_dict(corpus)
        yield retriever_types.Corpus(**corpus)


async def list_corpora_async(
    *,
    page_size: Optional[int] = None,
    client: glm.RetrieverServiceClient | None = None,
) -> AsyncIterable[retriever_types.Corpus]:
    """This is the async version of `retriever.list_corpora`."""
    if client is None:
        client = get_default_retriever_async_client()

    request = glm.ListCorporaRequest(page_size=page_size)
    async for corpus in await client.list_corpora(request):
        corpus = type(corpus).to_dict(corpus)
        yield retriever_types.Corpus(**corpus)
