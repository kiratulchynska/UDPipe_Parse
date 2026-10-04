"""
Module for parsing subtitle files using UDPipe and handling diacritics.
"""

import os
import re
import sys

from udpipe_wrapper import UDPipeWrapper

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
grandparent_dir = os.path.dirname(parent_dir)

SUBTITLES_DIR = os.path.join(grandparent_dir, "ParTree_NEW", "text_aligned", "Stage C done")
TEMP_DIR = "temp"
OUTPUT_DIR = "output"

UDPIPE_LANGUAGE_ALIASES = {
    "als": "sqi",
    "arb": "ara",
    "ekk": "est",
    "pes": "fas",
}


def diacritics(text: str, lang: str) -> str:
    """
    Separates or combine diacritics from their base characters in a string for specific languages.
    Args:
        text (str): The input text.
        lang (str): The language code.
    Returns:
        str: The text with diacritics separated.
    """
    import unicodedata
    if lang == 'mar':
        # For Marathi: combine diacritics (use NFC normalization)
        return unicodedata.normalize('NFC', text)
    if lang == 'hin':
        nfd_form = unicodedata.normalize('NFD', text)
        separated_chars = []
        for char in nfd_form:
            if unicodedata.combining(char):
                # If it's a combining character (diacritic), append it separately
                separated_chars.append(char)
            else:
                # Otherwise, append the base character
                separated_chars.append(char)
        return ''.join(separated_chars)
    return text

def get_available_languages(udpipe: UDPipeWrapper) -> list:
    """
    Get the list of available languages supported by UDPipe.
    Returns:
        list: List of available language codes.
    """
    from iso639 import Lang, is_language    

    language_models, _ = udpipe.get_models() 
    available_languages = [m.split('-')[0] for m in language_models.keys()]
    available_languages = set(available_languages)
    available_languages = [re.sub('_', ' ', l).title() for l in available_languages]
    if 'Greek' in available_languages:
        available_languages.append('Modern Greek (1453-)')
    if 'North Sami' in available_languages:
        available_languages.append('Northern Sami')
    available_languages = [Lang(l).pt3 for l in available_languages if is_language(l)]
    return available_languages

def clean_subtitles(subtitles: list) -> list:
    """
    Clean subtitles by handling missing English, missing translations and forced duplications.
    Args:
        subtitles (list): List of subtitle lines.
    Returns:
        list: Cleaned list of subtitle lines.
    """
    if len(subtitles[0]) < 3:
        return subtitles
    subtitles_new = []
    for i, line in enumerate(subtitles):
        if not line[2].strip():
            subtitles_new.append(line)
            continue
        if 'missing translation' == line[2].strip():
            continue
        if 'forced duplication' in line[2].strip():
            if i > 0 and subtitles[i-1][1] == line[1] and 'forced duplication' in subtitles[i-1][2]: # if duplicate of previous line, modify previous ID
                subtitles_new[-1] = [subtitles_new[-1][0] + '_' + line[0], subtitles_new[-1][1], subtitles_new[-1][2]]
            else: # if first occurrence, keep as is
                subtitles_new.append(line)
        if 'missing English' in line[2].strip():
            subtitle_parts = []
            orig_text = line[1]
            text_parts = [p.strip() for p in re.split(r'<|/>', line[1]) if p.strip() != '']

            if 'forced duplication' in line[2].strip() and i < len(subtitles) - 1 and subtitles[i+1][1] == line[1] and 'forced duplication' in subtitles[i+1][2]: # if not the last duplicate, skip
                continue
            elif 'forced duplication' in line[2].strip():
                sent_id = subtitles_new[-1][0]
                subtitles_new = subtitles_new[:-1]  # remove last added line to modify its ID
            else:
                sent_id = line[0]

            part_id = 1
            for part in text_parts:
                if f"<{part}/>" in orig_text:
                    subtitle_parts.append([f"{sent_id}_engY{part_id}", part, line[2]])
                    orig_text = orig_text.replace(f"<{part}/>", '', 1).strip()
                    part_id += 1
                else:
                    subtitle_parts.append([f"{sent_id}_engN{part_id}", part, re.sub(r'(, )?missing English(, )?', '', line[2]).strip()])
                    part_id += 1

            subtitles_new.extend(subtitle_parts)

        if line[2].strip() not in ['missing English', 'forced duplication', 'missing translation', 'missing English, forced duplication', 'forced duplication, missing English']:
            print(f"Warning: unrecognized tag '{line[2]}' in subtitle ID {line[0]}", file=sys.stderr)
    return subtitles_new

def parse_one_file(subtitles: list, output_file_path: str, film: str, lang: str, udpipe: UDPipeWrapper) -> str:
    """
    Parse a single subtitle file using UDPipe.
    Args:
        subtitles (list): List of subtitle lines. Each line is a list of strings: [id, text, tag].
        output_file_path (str): Path to the output CoNLL-U file.
        film (str): Film identifier.
        lang (str): Language of the subtitles.
        udpipe (UDPipeWrapper): An instance of UDPipeWrapper.
    Returns:
        str: The parsed CoNLL-U content.
    """
    from tqdm import tqdm

    docid = film.lower().replace(' ', '_')
    conllu = ''
    udpipe_lang = UDPIPE_LANGUAGE_ALIASES.get(lang, lang)

    print(f"Parsing for language {lang}...") 

    for line in tqdm(subtitles):
        parsed_line = ''
        while parsed_line == '':
            try:
                parsed_line = udpipe.parse_text(line[1], model=udpipe_lang, input_format="horizontal", output_format="conllu")
            except:
                print('Error connecting to UDPipe server. Trying again...')
        sent_id = f"{docid}/{line[0]}"
        if len(re.findall(r'# sent_id = ', parsed_line)) > 1:
            parsed_line = re.sub(r'# sent_id = ', fr'# sent_id = {sent_id}/part', parsed_line)
        else:
            parsed_line = re.sub(r'# sent_id = .+', fr'# sent_id = {sent_id}', parsed_line)
        conllu += parsed_line

    # Clean unwanted metadata
    conllu = re.sub(r'# newpar\n', '', conllu) 
    while re.search(r'\n\n# (generator|udpipe|newdoc).*\n', conllu):
        conllu = re.sub(r'\n\n# (generator|udpipe|newdoc).*\n', '\n\n', conllu)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(conllu)

def parse_subtitles(subtitles_dir: str=SUBTITLES_DIR, temp_dir: str=TEMP_DIR, output_dir: str=OUTPUT_DIR) -> list:
    """
    Parse subtitle files in the specified directory using UDPipe.
    Args:
        subtitles_dir (str): Directory containing the subtitle files.
        temp_dir (str): Temporary directory to store intermediate files.
        output_dir (str): Directory to store the final parsed files.
    Returns: 
        list: All detected languages.
    """
    from udpipe_wrapper import UDPipeWrapper
    udpipe = UDPipeWrapper()
    available_languages = get_available_languages(udpipe)

    all_lang = []

    print(f"Films found: {len([dir for dir in os.listdir(subtitles_dir) if not dir.startswith('.')])}\n")

    for film in sorted([dir for dir in os.listdir(subtitles_dir) if not dir.startswith('.')]):
        subtitles_for_parsing = dict()
        # print(f"Parsing subtitles for film {film}...\n")
        if not os.path.exists(os.path.join(temp_dir, film)):
            os.makedirs(os.path.join(temp_dir, film))
        if not os.path.exists(os.path.join(output_dir, film)):
            os.makedirs(os.path.join(output_dir, film))
        for file in sorted([f for f in os.listdir(os.path.join(subtitles_dir, film)) if not f.startswith('.')]):
            lang = re.search(r'_([a-z]{3})_\w+\.txt$', file).group(1)
            all_lang.append(lang)
            udpipe_lang = UDPIPE_LANGUAGE_ALIASES.get(lang, lang)
            # if lang not in ['eng', 'rus', 'heb', 'ukr']: # TODO delete after testing
            #     continue
            if udpipe_lang not in available_languages:
                subtitles_for_parsing[lang] = f"Skipping {lang}: no supported UDPipe model found.\n"
                # print(f"Skipping {lang}: no supported UDPipe model found.\n")
                continue
            # if os.path.exists(os.path.join(temp_dir, film, f"{film}_{lang}_parsed.conllu")):
            #     print(f"Skipping {lang}: already parsed.\n")
            #     continue

            
            with open(os.path.join(subtitles_dir, film, file), "r", encoding="utf-8") as f:
                subtitles = f.read()
            subtitles = diacritics(subtitles, lang)
            subtitles = subtitles.split('\n')

            if subtitles[0][0].isdigit(): # written left to right
                subtitles = [line.split("\t") for line in subtitles if line.strip() != '' and line.count("\t") > 0]
            else:
                subtitles = [line.split("\t")[::-1] for line in subtitles if line.strip() != '' and line.count("\t") > 0]

            subtitles = clean_subtitles(subtitles)

            if os.path.exists(os.path.join(temp_dir, film, f"{film}_{lang}_for_parsing.txt")) and os.path.exists(os.path.join(temp_dir, film, f"{film}_{lang}_parsed.conllu")):
                with open(os.path.join(temp_dir, film, f"{film}_{lang}_for_parsing.txt"), "r", encoding="utf-8") as f:
                    subtitles_for_parsing_old = f.read()
                    if subtitles_for_parsing_old == '\n'.join(['\t'.join(line) for line in subtitles]):
                        subtitles_for_parsing[lang] = f"Skipping {lang}: already parsed and no changes detected.\n"
                        continue
            subtitles_for_parsing[lang] = subtitles

        print(f"Languages without supported UDPipe models: {len([lang for lang, content in subtitles_for_parsing.items() if isinstance(content, str) and 'UDPipe' in content])}")
        print(f"\t{', '.join([lang for lang, content in subtitles_for_parsing.items() if isinstance(content, str) and 'UDPipe' in content])}\n")
        print(f"Languages already parsed and unchanged: {len([lang for lang, content in subtitles_for_parsing.items() if isinstance(content, str) and 'already parsed' in content])}")
        print(f"\t{', '.join([lang for lang, content in subtitles_for_parsing.items() if isinstance(content, str) and 'already parsed' in content])}\n")
        print(f"Languages to be parsed: {len([lang for lang, content in subtitles_for_parsing.items() if isinstance(content, list)])}\n")
        print(f"\t{', '.join([lang for lang, content in subtitles_for_parsing.items() if isinstance(content, list)])}\n")

        for lang in sorted([lang for lang, content in subtitles_for_parsing.items() if isinstance(content, list)]):
            print(f"Parsing language {lang} for film {film}...")
            subtitles = subtitles_for_parsing[lang]
            with open(os.path.join(temp_dir, film, f"{film}_{lang}_for_parsing.txt"), "w", encoding="utf-8") as f:
                f.write('\n'.join(['\t'.join(line) for line in subtitles]))
            

            parse_one_file(subtitles, os.path.join(temp_dir, film, f"{film}_{lang}_parsed.conllu"), film, lang, udpipe)
            print()
            
    return all_lang
    

if __name__ == "__main__":
    _ = parse_subtitles(SUBTITLES_DIR, TEMP_DIR, OUTPUT_DIR)