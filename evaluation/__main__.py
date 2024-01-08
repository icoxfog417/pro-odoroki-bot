import os
from pathlib import Path
import logging
import argparse
import json

import boto3
import botocore
import numpy as np
import numpy.typing as npt
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

import aws_chalice.chalicelib.pro_odoroki_generator as pog
from aws_chalice.chalicelib.bedrock import Bedrock


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


class Evaluator():

    def __init__(self) -> None:
        self.generate_client = Bedrock()
        config = botocore.config.Config(
            read_timeout=900,
            connect_timeout=900,
            retries={"max_attempts": 3}
        )
        self.embedding_client = boto3.client("bedrock-runtime", config=config)
    
    def generate_odoroki(self, row: pd.Series) -> str:
        prompt_body = pog.generate(news=row.news_description, character=row.odoroki_persona)
        reply = self.generate_client.ask_to_claude(prompt_body, instant=True)
        reaction = pog.retrieve(reply)
        return reaction["reaction"]

    def generate_embedding(self, texts: list) -> npt.NDArray:
        body = {
            "texts": texts,
            "input_type": "search_document"
        }
    
        response = self.embedding_client.invoke_model(
            modelId="cohere.embed-multilingual-v3",
            body=json.dumps(body),
            accept="application/json",
            contentType="application/json"
        )
                
        response_body = response.get("body").read().decode("utf-8")
        response_json = json.loads(response_body)
        return response_json["embeddings"]

    def calculate_distance(self, a: npt.NDArray, b: npt.NDArray) -> npt.NDArray:
        # a, b is array of embedding
        distances = cosine_similarity(a, b).diagonal()
        return distances


def main(num_samples:int) -> None:
    logger.info("Generate odoroki files.")
    DATA_DIR = Path(os.path.join(os.path.dirname(__file__), "data"))
    raw_data_path = DATA_DIR.joinpath("raw/pro-odoroki-data.csv")

    logger.info(f"Read raw data from {raw_data_path}")
    data = pd.read_csv(raw_data_path)
    assert len(data) > 0
    
    logger.info(f"Generate odoroki {num_samples} times.")
    evaluator = Evaluator()
    
    if len(list(DATA_DIR.glob("interim/**/*.csv"))) == num_samples:
        logger.info(f"Already odoroki exists. If you want to generate again, please delete files.")
    else:
        for i in range(num_samples):
            logger.info(f"\tgenerating odoroki no {i + 1} ...")
            odoroki_requests = data.apply(evaluator.generate_odoroki, axis=1)
            data["generated"] = odoroki_requests
            data.to_csv(
                DATA_DIR.joinpath(f"interim/pro-odoroki-generated_{i + 1}.csv"),
                index=False)

    logger.info(f"Calculate embedding for {num_samples} generateds.")
    assert len(list(DATA_DIR.glob("interim/**/*.csv"))) == num_samples
    
    news_path = DATA_DIR.joinpath("processed/news_embedding.npy")
    odoroki_path =  DATA_DIR.joinpath("processed/odoroki_embedding.npy")

    for i, file in enumerate(DATA_DIR.glob("interim/**/*.csv")):
        generated = pd.read_csv(file)
        if i == 0:
            if news_path.exists():
                logger.info(f"Already news embedding exists. If you want to generate again, please delete files.")
            else:
                logger.info("\tcalculate embedding of news.")
                news = generated.news_description.tolist()
                news_embedding = evaluator.generate_embedding(news)
                np.save(news_path, news_embedding)

            if odoroki_path.exists():
                logger.info(f"Already odoroki embedding exists. If you want to generate again, please delete files.")
            else:
                logger.info("\tcalculate embedding of original odoroki.")
                odorokis = generated.odoroki_pro.tolist()
                odoroki_embedding = evaluator.generate_embedding(odorokis)
                np.save(odoroki_path, odoroki_embedding)
        
        index = i + 1
        logger.info(f"\tcalculate embedding of generated odoroki no {index} ...")
        if DATA_DIR.joinpath(f"processed/generated_embedding_{index}.npy").exists():
            logger.info(f"Already emgedding for {index} exists. If you want to generate again, please delete files.")
        else:
            generated_odorokis = generated.generated.tolist()
            generated_embedding = evaluator.generate_embedding(generated_odorokis)
            np.save(DATA_DIR.joinpath(f"processed/generated_embedding_{index}"), generated_embedding)

    logger.info(f"Calculate cosine similarity.")
    news_embeddings = np.load(news_path)
    odoroki_embeddings = np.load(odoroki_path)
    # Take diagonal value for pairwise comparison
    news_vs_odoroki = evaluator.calculate_distance(news_embeddings, odoroki_embeddings)

    _news_vs_generated_all = []
    _odoroki_vs_generated_all = []
    for file in DATA_DIR.glob("processed/generated_embedding_*.npy"):
        generated_embeddings = np.load(file)
        _news_vs_generated_all.append(evaluator.calculate_distance(news_embeddings, generated_embeddings))
        _odoroki_vs_generated_all.append(evaluator.calculate_distance(odoroki_embeddings, generated_embeddings))
    
    news_vs_generated_all = np.stack(_news_vs_generated_all)
    odoroki_vs_generated_all = np.stack(_odoroki_vs_generated_all)
    news_vs_generated = np.average(news_vs_generated_all, axis=0)
    odoroki_vs_generated = np.average(odoroki_vs_generated_all, axis=0)

    distances = pd.DataFrame({
        "news_vs_odoroki": news_vs_odoroki,
        "news_vs_generated": news_vs_generated,
        "odoroki_vs_generated": odoroki_vs_generated
    })
    
    logger.info("Calculated distances")
    logger.info(distances.describe())
    
    for i in range(odoroki_vs_generated_all.shape[1]):
        max_similarity = np.max(odoroki_vs_generated_all[:, i])
        max_index = np.argmax(odoroki_vs_generated_all[:, i])
        logger.info(f"\tMax similarity for data {i + 1} is {max_similarity:.2f} and file {max_index + 1}")
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate generated orodoki")
    parser.add_argument("--num_samples", help="number of samples to calculate vector", type=int, default=5)
    args = parser.parse_args()
    main(args.num_samples)
