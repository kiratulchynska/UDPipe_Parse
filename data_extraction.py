"""
Module for extracting relevant data from CoNLL-U files based on specified dependency relations.
"""

import os
import re
import pandas as pd
from ud_classes import Sent, Node

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
grandparent_dir = os.path.dirname(parent_dir)

UDPIPE_DIR = os.path.join(parent_dir, "udpipe", "src", "udpipe")
SUBTITLES_DIR = os.path.join(grandparent_dir, "ParTree_NEW", "text_aligned", "Stage C done")
OUTPUT_DIR = "output"
DEPRELS_TO_EXTRACT_PATH = 'deprels_to_extract.txt'

def parallel_id_to_extract(film: str, subtitles_dir: str) -> list:
    """
    Get the sentence IDs to extract for a given film.
    Args:
        film (str): The name of the film.
        subtitles_dir (str): The directory containing the subtitles.
    Returns:
        list: A list of sentence IDs to extract.
    """
    eng_file = [file for file in os.listdir(os.path.join(subtitles_dir, film)) if re.search(r'_eng_\w+\.txt$', file)][0]

    with open(os.path.join(subtitles_dir, film, eng_file), "r", encoding="utf-8") as f:
        eng_subtitles = f.read().split("\n")
        eng_subtitles = [line.split("\t") for line in eng_subtitles if line.strip() != '' and line.count("\t") >= 1]
    parallel_ids = [int(line[0].strip()) for line in eng_subtitles]

    for file in os.listdir(os.path.join(subtitles_dir, film)):
        if not file.endswith("txt") or '_eng_' in file:
            continue
        with open(os.path.join(subtitles_dir, film, file), "r", encoding="utf-8") as f:
            subtitles = f.read().split("\n")
        if subtitles[0][0].isdigit(): # written left to right
            subtitles = [line.split("\t") for line in subtitles if line.strip() != '' and line.count("\t") > 1]
        else:
            subtitles = [line.split("\t")[::-1] for line in subtitles if line.strip() != '' and line.count("\t") > 1]

        for line in subtitles:
            sid = int(line[0].strip())
            if line[2].strip() != '' and sid in parallel_ids:
                parallel_ids.remove(sid)
    print(f"For film {film}, {len(parallel_ids)} sentences to extract.")
    return parallel_ids

def extract_from_file(path: str, parallel_ids: list, deprels_to_extract: list, extract_all_deprels: bool=False) -> list:
    """
    Extract relevant data from a CoNLL-U file based on sentence IDs and dependency relations.
    Args:
        path (str): Path to the CoNLL-U file.
        parallel_ids (list): List of sentence IDs to extract.
        deprels_to_extract (list): List of dependency relations to extract.
        extract_all_deprels (bool): Whether to extract all dependency relations.
    Returns:
        list: A list of dictionaries containing the extracted data.
    """
    data = []
    with open(path, "r", encoding="utf-8") as f:
        conllu_text = f.read().split("\n\n")
    for sent in conllu_text:
        udsent = Sent(sent)
        parallel_id = udsent.metadata['parallel_id']
        parallel_id = int(parallel_id.split('/')[1]) if '/' in parallel_id else -1
        if parallel_id in parallel_ids:
            for node in udsent.nodes:
                node: Node
                if extract_all_deprels or node.deprel in deprels_to_extract or node.deprel.split(':')[0] in deprels_to_extract:
                    nr_verb = sum(1 for n in udsent.nodes if n.upos == 'VERB')
                    nr_aux = sum(1 for n in udsent.nodes if n.upos == 'AUX')
                    data.append({'ID_sent': parallel_id,
                                 'text': udsent.metadata.get("text", ""),
                                 'nr_verb': nr_verb,
                                 'nr_aux': nr_aux,
                                 'ID_word': node.id,
                                 'form_word': node.form,
                                 'pos_word': node.upos,
                                 'deprel_word': node.deprel, 
                                 'ID_head': node.head,
                                 'form_head': node.parent.form if node.parent else '',
                                 'pos_head': node.parent.upos if node.parent else '',
                                 'deprel_head': node.parent.deprel if node.parent else ''})
    return data
        


def data_extraction(output_dir: str=OUTPUT_DIR, subtitles_dir: str=SUBTITLES_DIR, deprels_path: str=DEPRELS_TO_EXTRACT_PATH):
    """
    Extract data from CoNLL-U files in the output directory based on specified dependency relations.
    Args:
        output_dir (str): Directory containing the CoNLL-U files.
        subtitles_dir (str): Directory containing the subtitles.
        deprels_path (str): Path to the file containing dependency relations to extract.
    """
    data = []
    extract_all_deprels = False
    # extract_all_deprels = input("All deprels? (y/N): ").strip().lower() in ['y', 'yes']

    with open(deprels_path, "r", encoding="utf-8") as f:
        deprels_to_extract = [line.strip() for line in f.readlines() if line.strip() != '']
    for film in os.listdir(output_dir):
        if os.path.isfile(os.path.join(output_dir, film)):
            continue
        parallel_ids = parallel_id_to_extract(film, subtitles_dir)
        for file in os.listdir(os.path.join(output_dir, film)):
            if not file.endswith(".conllu"):
                continue
            lang = re.search(fr"{re.sub(' ', '_', film)}_([a-z]{{3}})_.+\.conllu$", file).group(1)
            file_data = extract_from_file(os.path.join(output_dir, film, file), parallel_ids, deprels_to_extract, extract_all_deprels)
            data += [{'ID_lang': lang, 'ID_film': film, **entry} for entry in file_data]
    df = pd.DataFrame(data)
    df = df.reset_index().rename(columns={'index': 'ID'})
    if extract_all_deprels:
        df.to_csv(os.path.join(output_dir, "extracted_data_all_deprels.tsv"), sep='\t', index=False)
    else:
        df.to_csv(os.path.join(output_dir, "extracted_data.tsv"), sep='\t', index=False)
    
if __name__ == "__main__":
    data_extraction(OUTPUT_DIR, SUBTITLES_DIR, DEPRELS_TO_EXTRACT_PATH)