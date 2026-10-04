import os
import shutil

from parse_subtitles import parse_subtitles
from final_subtitles import final_subtitles
from data_extraction import data_extraction


cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
grandparent_dir = os.path.dirname(parent_dir)

UDPIPE_DIR = os.path.join(parent_dir, "udpipe", "src", "udpipe")
SUBTITLES_DIR = os.path.join(grandparent_dir, "ParTree_NEW", "text_aligned", "Stage C done")
TEMP_DIR = "temp"
OUTPUT_DIR = "output"
DEPRELS_TO_EXTRACT_PATH = 'deprels_to_extract.txt'



def deleting_dir():
    """
    Delete old temporary directory if it exists.
    """
    if os.path.exists(TEMP_DIR):
        print(f"Deleting old temporary directory.\n")
        shutil.rmtree(TEMP_DIR)

def create_dirs():
    """
    Create necessary directories if they do not exist.
    """
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def print_lang_table(all_lang: list, parse_lang: dict):
    """
    Print a table summarizing the languages processed.
    Args:
        all_lang (list): All detected languages.
        parse_lang (dict): Languages that were parsed and their models.
    """
    print("-" * 60)
    print(f"{'Language':10} {'Parsed':<10} {'Model':<40}")
    print("-" * 60)
    for lang in sorted(set(all_lang)):
        parsed = "+" if lang in parse_lang else "-"
        model = parse_lang[lang] if lang in parse_lang else "-"
        print(f"{lang:<10} {parsed:<10} {model:<40}")
    print(f"-" * 60)
    print(f"{len(all_lang):<10} {len(parse_lang):<10}")
    print(f"-" * 60)

if __name__ == "__main__":
    create_dirs()

    all_lang = parse_subtitles(SUBTITLES_DIR, TEMP_DIR, OUTPUT_DIR)
    parsed_lang = final_subtitles(TEMP_DIR, OUTPUT_DIR)

    data_extraction(OUTPUT_DIR, SUBTITLES_DIR, DEPRELS_TO_EXTRACT_PATH)
    print_lang_table(all_lang, parsed_lang)

    # deliting_dir()


