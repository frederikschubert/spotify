import random
from typing import List

import parse
import numpy as np
import torch
import torch.distributions as distributions
from transformers.generation_utils import top_k_top_p_filtering
from common.mpd_model import Playlist, Track
from transformers import RobertaForMaskedLM, RobertaTokenizer, PreTrainedTokenizerBase
from loguru import logger


def create_prompts(
    playlist: Playlist,
    num_tracks: int,
    playlist_name_length_probs: List[float],
    num_prompts: int = 2
):
    playlist_length_distribution = distributions.Categorical(
        probs=torch.from_numpy(np.array(playlist_name_length_probs))
    )
    prompts = []
    for _ in range(num_prompts):
        prompt = "<BOS>"
        prompt += (
            '"' + playlist.name + '":'
            or " ".join(["<mask>"] * (playlist_length_distribution.sample() + 1)) + '":'
        )
        candidate_tracks = ["".join(track.track_name.split(" ")) for track in playlist.tracks] + ["<mask>"]
        playlist_samples = random.choices(candidate_tracks, weights=[1. if i < len(candidate_tracks) - 1 else len(candidate_tracks) + 1 for i in range(len(candidate_tracks))], k=num_tracks)
        for track_name in playlist_samples:
            prompt += ' "' + track_name + '"'
        prompt += "<EOS>"
        logger.trace(prompt)
        prompts.append(prompt)
    return prompts


def parse_tracks(sentence: str) -> List[Track]:
    logger.trace(sentence)
    title = sentence.split('": ')[0].split('"')[-1]
    logger.trace(title)
    track_candidates = sentence.split('": ')[1].replace('"', '').split('<EOS>')[0].split(' ')
    tracks = [Track(track_name=track, track_uri=track) for track in track_candidates]
    logger.trace(tracks)
    return tracks

def sample_sentence(
    logits: torch.Tensor, k: int, temperature: float, tokenizer: PreTrainedTokenizerBase, top_k=50, top_p=1.0
):
    scores = logits / temperature
    logscores = top_k_top_p_filtering(scores, top_k=top_k, top_p=top_p)
    distribution = distributions.Categorical(logits=logscores)
    token_ids = distribution.sample([k])
    return [tokenizer.decode(tokens[0]) for tokens in token_ids]


def generate(
    playlist: Playlist,
    checkpoint: str,
    k: int,
    temperature: float,
    num_tracks: int,
    playlist_name_length_probs: List[float],
) -> List[Track]:
    tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
    special_tokens_dict = {
        "bos_token": "<BOS>",
        "eos_token": "<EOS>",
        "pad_token": "<PAD>",
    }
    tokenizer.add_special_tokens(special_tokens_dict)
    model = RobertaForMaskedLM.from_pretrained(checkpoint, return_dict=True)
    model.resize_token_embeddings(len(tokenizer))
    prompts = create_prompts(
        playlist,
        num_tracks,
        playlist_name_length_probs,
    )
    inputs = tokenizer(prompts, return_tensors="pt", padding=True)
    logits = model(**inputs).logits
    sentences = sample_sentence(logits, k, temperature, tokenizer)
    tracks = []
    for sentence in sentences:
        tracks.extend(parse_tracks(sentence))
    return tracks
