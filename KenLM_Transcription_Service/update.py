import os
import re


model_paths = {
    'ory': '5gram_model.bin',
    'eng': '5gram_model_eng.bin'
}

vocab_paths = {
    'ory': 'lexicon.txt',
    'eng': 'lexicon_eng.txt'
}

texts_paths = {
    'ory': 'texts.txt',
    'eng': 'texts_eng.txt'
}


class UpdationModel():
    def __init__(self, model_paths, vocab_paths, texts_paths):
        self.model_paths = model_paths
        self.vocab_paths = vocab_paths
        self.texts_paths = texts_paths

    def set_language(self, lang):
        self.model_path = self.model_paths[lang]
        self.vocab_path = self.vocab_paths[lang]
        self.texts_path = self.texts_paths[lang]

    def train_kenlm_model(self):
        input_path = self.texts_path.split('.')[0] + '_unique.txt'

        output_file = '5gram_model'

        #  Making the arpa files
        output_file1 = output_file + ".arpa"
        output_file2 = output_file + "_correct.arpa"
        output_bin_file = self.model_path

        os.system(f"kenlm/build/bin/lmplz -o 5 <{input_path} > {output_file1} --discount_fallback")

        # adding the </s> character to the arpa file
        with open(output_file1, "r") as read_file, open(output_file2, "w") as write_file:
            has_added_eos = False
            for line in read_file:
                if not has_added_eos and "ngram 1=" in line:
                    count = line.strip().split("=")[-1]
                    write_file.write(line.replace(f"{count}", f"{int(count)+1}"))
                elif not has_added_eos and "<s>" in line:
                    write_file.write(line)
                    write_file.write(line.replace("<s>", "</s>"))
                    has_added_eos = True
                else:
                    write_file.write(line)

        # converting arpa file to bin file
        os.system(f"kenlm/build/bin/build_binary {output_file2} {output_bin_file}")

        os.remove(output_file1)
        os.remove(output_file2)

    def update_lexicon_file(self):
        with open(self.texts_path, 'r') as f:
            text = f.read()

        # Tokenize the text into words
        words = set(text.split())

        with open(self.vocab_path, 'w') as f:
            for word in words:
                phonemes = " ".join(list(word))
                line = word + " " + phonemes + " |\n"
                f.write(line)

        return True

    def remove_punctuation(self, word):
        return re.sub(r"[^\w\d\s'-]", ' ', word)

    def update_text_file(self, text):
        final_text = []

        if type(text) == list:
            # remove puntuations from the text
            for line in text:
                line = self.remove_punctuation(line)
                # final_text.append(' '.join([word for word in line.split() if word.isalnum()]))
                final_text.append(' '.join([word for word in line.split() if word]))
        else:
            text = self.remove_punctuation(text)
            final_text.append(' '.join([word for word in text.split() if word]))
            # final_text.append(' '.join([word for word in text.split() if word.isalnum()]))

        with open(self.texts_path, 'a+') as f:
            for line in final_text:
                f.write(line + '\n')

        unique_text = set(final_text)

        with open(self.texts_path.split('.')[0] + '_unique.txt', 'w') as f:
            for line in unique_text:
                f.write(line + '\n')

    async def update(self, req):
        self.lang = req.lang
        self.text = req.text

        self.set_language(self.lang)
        self.update_text_file(self.text)

        self.update_lexicon_file()

        self.train_kenlm_model()

        return 'Model updated successfully'