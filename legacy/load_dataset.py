
import os
import logging
from typing import Callable, Dict
import json

import datasets
import xml.etree.ElementTree as ET

from transformers import PreTrainedTokenizerBase

from utils import create_prompt_completion

logger = logging.getLogger(__name__)


def _load_xml_canaries_dataset(
    dataset_name: str,
    canaries_dataset: str,
    type_of_canaries: str,
    language_prompt: str,
    seed: int,
):
    """Carga los datasets actuales basados en XML con canaries (meddocan, i2b2, achs_*, etc).

    Estructura de carpetas esperada:
        data/{dataset_name}/{canaries}_canaries[,_1|_2]
    """
    if canaries_dataset == "0":
        data_folder = f"data/{dataset_name}/{canaries_dataset}_canaries"
    else:
        suf = "_canaries_1" if type_of_canaries == "common" else "_canaries_2"
        data_folder = f"data/{dataset_name}/{canaries_dataset}{suf}"

    logger.info(f"Loading XML canaries dataset from {data_folder}")

    docs = []
    for fn in os.listdir(data_folder):
        if not fn.endswith(".xml"):
            continue
        xml = ET.parse(os.path.join(data_folder, fn), parser=ET.XMLParser(encoding="utf-8")).getroot()
        text = xml.find("TEXT").text
        prompt = create_prompt_completion(text, language_prompt, dataset_name=dataset_name)
        docs.append(prompt)

    raw = datasets.Dataset.from_dict({"text": docs})
    ds = raw.train_test_split(test_size=0.001, shuffle=True, seed=seed)
    return ds


def _load_ai4privacy_dataset(seed: int) -> datasets.DatasetDict:
    """Carga el dataset HuggingFace `ai4privacy/pii-masking-300k`.

    Usamos `target_text` como texto objetivo (texto con máscaras de privacidad),
    filtrando a language=="English" tal como pediste.
    """
    logger.info("Loading HF dataset ai4privacy/pii-masking-300k (English, target_text)")
    raw_hf = datasets.load_dataset("ai4privacy/pii-masking-300k", split="train")

    # Filtramos por idioma English
    raw_hf = raw_hf.filter(lambda ex: ex.get("language", "") == "English")

    texts = raw_hf["target_text"]
    # Para ai4privacy también envolvemos con un prompt de dominio privacidad
    texts = [create_prompt_completion(t, language='en', dataset_name="ai4privacy/pii-masking-300k") for t in texts]
    raw = datasets.Dataset.from_dict({"text": texts})
    ds = raw.train_test_split(test_size=0.001, shuffle=True, seed=seed)
    return ds


def _load_tab_dataset(seed: int) -> datasets.DatasetDict:
    """Carga el dataset local `tab`.

    Usa los ficheros JSON ECHR en `data/tab/echr_{train,dev,test}.json` y
    toma el campo `text` de cada ejemplo como texto de entrada.
    """
    data_folder = "data/tab"
    logger.info(f"Loading local TAB dataset from {data_folder}")

    part_files = [
        os.path.join(data_folder, name)
        for name in ["echr_train.json", "echr_dev.json", "echr_test.json"]
        if os.path.exists(os.path.join(data_folder, name))
    ]
    if not part_files:
        raise FileNotFoundError(
            f"Expected ECHR json files (echr_train.json, echr_dev.json, echr_test.json) in {data_folder}"
        )

    docs = []
    for path in part_files:
        logger.info(f"Reading TAB subset from {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for ex in data:
            # Cada ejemplo tiene la clave 'text' con el documento completo
            text = ex.get("text", "")
            if text:
                # TAB: prompt jurídico
                docs.append(create_prompt_completion(text, language='en', dataset_name='tab'))

    if not docs:
        raise ValueError(f"No text entries found in TAB dataset under {data_folder}")

    raw = datasets.Dataset.from_dict({"text": docs})
    ds = raw.train_test_split(test_size=0.001, shuffle=True, seed=seed)
    return ds


def get_raw_dataset(
    dataset_name: str,
    canaries_dataset: str,
    type_of_canaries: str,
    language_prompt: str,
    seed: int,
):
    """Devuelve un `datasets.DatasetDict` con la columna `text` para el dataset pedido.

    Soporta:
      - datasets XML locales con canaries (meddocan, i2b2, achs_*, etc.)
      - HF `ai4privacy/pii-masking-300k` (language=English, usamos target_text)
      - dataset local `tab` (textos en .txt bajo data/tab)
    """

    if dataset_name == "ai4privacy/pii-masking-300k":
        return _load_ai4privacy_dataset(seed=seed)

    if dataset_name == "tab":
        return _load_tab_dataset(seed=seed)

    # Por defecto, usamos el loader XML con canaries
    return _load_xml_canaries_dataset(
        dataset_name=dataset_name,
        canaries_dataset=canaries_dataset,
        type_of_canaries=type_of_canaries,
        language_prompt=language_prompt,
        seed=seed,
    )


def tokenize_dataset(
    ds: datasets.DatasetDict,
    tokenizer: PreTrainedTokenizerBase,
    sequence_len: int,
) -> datasets.DatasetDict:
    """Tokeniza un DatasetDict con columna `text` para causal LM.

    - truncation/padding a `sequence_len`
    - añade `labels = input_ids` para entrenamiento de LM.
    """

    def preprocess(examples: Dict[str, str]):
        tok = tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=sequence_len,
        )
        tok["labels"] = tok["input_ids"]
        return tok

    tokenized = ds.map(preprocess, batched=True, remove_columns=["text"])
    return tokenized


def load_and_tokenize_dataset(
    dataset_name: str,
    canaries_dataset: str,
    type_of_canaries: str,
    language_prompt: str,
    seed: int,
    tokenizer: PreTrainedTokenizerBase,
    sequence_len: int,
) -> datasets.DatasetDict:
    """Función de alto nivel usada por el script de finetuning.

    Devuelve un DatasetDict tokenizado listo para pasar al Trainer.
    """
    raw_ds = get_raw_dataset(
        dataset_name=dataset_name,
        canaries_dataset=canaries_dataset,
        type_of_canaries=type_of_canaries,
        language_prompt=language_prompt,
        seed=seed,
    )
    tokenized = tokenize_dataset(raw_ds, tokenizer=tokenizer, sequence_len=sequence_len)
    return tokenized
