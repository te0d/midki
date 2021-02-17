import csv
import json
import logging
import os
import re

logging.basicConfig(level='WARN')

hsk_freq_dir = "./raw_data/hsk_freq/"
hsk_freq_all = "./raw_data/HSK Overall.csv"
wubi_file = "./raw_data/wubi86_stripped.txt"

overall_content = None
with open(hsk_freq_all, "r", encoding="utf-8-sig") as overall_file:
    overall_content = overall_file.read()

wubi_dictionary = None
with open(wubi_file, "r", encoding="utf-8-sig") as wf:
    wubi_dictionary = wf.read()

word_list = []
hsk_freq_files = os.listdir(hsk_freq_dir)
for hsk_file in hsk_freq_files:
    logging.info("processing {}...".format(hsk_file))
    with open("{}{}".format(hsk_freq_dir, hsk_file), "r", encoding="utf-8-sig") as level_file:
        hsk_level = re.search(r"L([1-6])", hsk_file).group(1)   # extract hsk level from filename
        reader = csv.reader(level_file, delimiter="\t")
        for row in reader:
            word = {
                "simplified": row[0],
                "traditional": row[1],
                "hsk_level": int(hsk_level),
                "pinyin_number": row[2],
                "pinyin_accent": row[3],
                "meaning": row[4]
            }

            # find relative frequency of word
            rel_freq = re.search(r"^{}\t[1-6]\t(\d+)$".format(word["simplified"]), overall_content, re.MULTILINE).group(1)
            word["overall_freq"] = int(rel_freq)

            # find the wubi strokes for each character
            wubi = []
            for char in word["simplified"]:
                keys = re.search(r"^{}\t([a-z]+)$".format(char), wubi_dictionary, re.MULTILINE).group(1)
                wubi.append(keys)

            word["wubi"] = " ".join(wubi)

            word_list.append(word)

print(json.dumps(word_list, ensure_ascii=False))
