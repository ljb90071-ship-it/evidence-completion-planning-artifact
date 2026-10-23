"""Paths for computed outputs and the immutable archived result baseline."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def result_path(name):
    folder=ROOT/'results/generated'
    folder.mkdir(parents=True,exist_ok=True)
    return folder/name
def read_result(name):
    generated=ROOT/'results/generated'/name
    return generated if generated.exists() else ROOT/'results/archive'/name
