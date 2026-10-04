import os
import re
import sys

from ud_classes import Sent, Node

TEMP_DIR = "temp"
OUTPUT_DIR = "output"

def parallel_treebank_format(conllu: str, docid: str, lang: str) -> str: 
    """
    Format parsed CoNLL-U sentences for parallel treebank without alignment.
    Args:
        conllu (str): The CoNLL-U formatted string of the parsed sentences.
        docid (str): Document ID.
        lang (str): Language code.
    Returns:
        str: The updated CoNLL-U formatted string with sent_id information added.
    """
    conllu_sents = [(Sent(sent)) for sent in conllu.strip().split('\n\n')]
    updated_sents = []
    for i, sent in enumerate(conllu_sents):
        sent: Sent
        sent.metadata['parallel_id'] = sent.metadata['sent_id']
        parallel_id: str = sent.metadata['parallel_id'].split('/')[1:] # all but docid
        if not re.search(r'_', parallel_id[0]): # godfather/1 or godfather/1/part1
            for node in sent.nodes:
                node: Node
                node.misc['Ref'] = docid + '.' + parallel_id[0]
        elif not re.search(r'_eng', parallel_id[0]): # godfather/1_2 or godfather/1_2/part1
            parallel_id[0] = parallel_id[0].split('_')[0]
            sent.metadata['parallel_id'] = docid + '/' + '/'.join(parallel_id) # not adding Ref
        elif re.search(r'_eng', parallel_id[0]): # godfather/1_engY1 or godfather/1_engY1/part1 or godfather/1_2_engY1 or godfather/1_2_engY1/part1 ...
            english = 'engY' in parallel_id[0]
            duplicate = re.search(r'_\d', parallel_id[0]) is not None
            parallel_id[0] = re.sub(r'(\d+)_.*eng(Y|N)\d+', r'\1', parallel_id[0])
            if i > 0 and conllu_sents[i-1].metadata['parallel_id'].split('/')[1] == parallel_id[0].split('_')[0]:
                part_id = conllu_sents[i-1].metadata['parallel_id'].split('/')[-1]
                part_id = re.sub(r'part(\d+)', lambda m: f"part{int(m.group(1))+1}", part_id)
                sent.metadata['parallel_id'] = docid + '/' + parallel_id[0] + '/' + part_id
            else:
                sent.metadata['parallel_id'] = docid + '/' + parallel_id[0] + '/part1'
            if not english and not duplicate:
                for node in sent.nodes:
                    node: Node
                    node.misc['Ref'] = docid + '.' + parallel_id[0]

        elif re.search(r'_engN', parallel_id[0]): # godfather/1_engN1 or godfather/1_engN1/part1 or godfather/1_2_engN1 or godfather/1_2_engN1/part1
            if not re.search(r'_\d', parallel_id[0]): # godfather/1_engN1 or godfather/1_engN1/part1
                for node in sent.nodes:
                    node: Node
                    node.misc['Ref'] = parallel_id[0].split('_')[0]
            parallel_id[0] = re.sub(r'(\d+)_.*engN(\d+)', r'\1/part\2', parallel_id[0])
            sent.metadata['parallel_id'] = docid + '/' + '/'.join(parallel_id)
        else:
            print(f"Warning: unrecognized sent_id format '{parallel_id[0]}' in doc {docid} {lang}.", file=sys.stderr)
        sent.metadata['sent_id'] = i+1
        metadata_keys = list(sent.metadata.keys())
        metadata_keys = [k for k in metadata_keys if k != 'text'] + ['text']
        sent.metadata = {k: sent.metadata[k] for k in metadata_keys}
        updated_sents.append(str(sent).strip())
    return '\n\n'.join(updated_sents)



def final_subtitles(temp_dir: str = TEMP_DIR, output_dir: str = OUTPUT_DIR) -> dict:
    """
    Finalize the parsed subtitles by formatting them into a parallel treebank structure.
    Args:
        temp_dir (str): Directory containing the temporary parsed subtitle files.
        output_dir (str): Directory to save the finalized CoNLL-U files.
    Returns:
        dict: A dictionary of processed languages and their models.
    """
    parsed_lang = {}
    for film in sorted([dir for dir in os.listdir(temp_dir) if not dir.startswith('.')]):
        if film.startswith('.'):  # .DS_Store
            continue
        if not os.path.exists(os.path.join(output_dir, film)):
            os.makedirs(os.path.join(output_dir, film))
        print(f"Finalizing film: {film}...")
        for subtitles_file in sorted([f for f in os.listdir(os.path.join(temp_dir, film)) if f.endswith("_parsed.conllu")]):
            lang = re.search(r'_(\w+)_parsed\.conllu$', subtitles_file).group(1)
            # print(f"  Processing language: {lang}...")
            docid = re.sub(' ', '_', film).lower() # godfather, bridge_of_spies, ...
            with open(os.path.join(temp_dir, film, subtitles_file), "r", encoding="utf-8") as f:
                conllu = f.read()

            conllu = parallel_treebank_format(conllu, docid, lang)

            model = re.search(r'# udpipe_model = ([^\n]+)\n', conllu).group(1)
            if lang not in parsed_lang:
                parsed_lang[lang] = model
            with open(os.path.join(output_dir, film, f"{re.sub(' ', '_', film)}_{lang}_{model.split('-ud-')[0]}.conllu"), "w", encoding="utf-8") as f:
                f.write(conllu)
        print(f"Finished finalizing film: {film}.\n")
    return parsed_lang
    
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    parsed_lang = final_subtitles(TEMP_DIR, OUTPUT_DIR)

