import random

from nmtwizard.preprocess import prepoperator
from nmtwizard.preprocess.tu import TokReplace

@prepoperator.register_operator("noise")
class Noise(prepoperator.TUOperator):

    @staticmethod
    def is_applied_for(process_type):
        return process_type == prepoperator.ProcessType.TRAINING

    def __init__(self, config, *args):
        self._drop_word_prob = config.get("drop_word_prob", 0)
        self._drop_space_prob = config.get("drop_space_prob", 0)
        self._drop_char_prob = config.get("drop_char_prob", 0)
        self._duplicate_char_prob = config.get("duplicate_char_prob", 0)
        self._swap_char_prob = config.get("swap_char_prob", 0)

    def _preprocess_tu(self, tu, *args):
        src_tok = tu.src_tok
        tokens = src_tok.token_objects
        new_tokens = [self._apply_word_noise(tokens[0])]
        tu.src_tok = (src_tok.tokenizer, new_tokens)
        return [tu]

    def _apply_word_noise(self, tokens):
        new_tokens = []
        for token in tokens:
            if self._drop_word_prob > 0 and random.random() <= self._drop_word_prob:
                continue
            elif self._drop_space_prob > 0 and random.random() <= self._drop_space_prob:
                token.join_left = True

            if ((self._drop_char_prob > 0
                 or self._duplicate_char_prob > 0
                 or self._swap_char_prob > 0)
                and not token.is_placeholder()):
                token.surface = self._apply_character_noise(token.surface)
            if len(token.surface) != 0:  # Delete token if empty.
                new_tokens.append(token)
        return new_tokens

    def _apply_character_noise(self, cur_surface):
        new_surface = ""
        i = 0
        while i < len(cur_surface):
            if self._drop_char_prob > 0 and random.random() <= self._drop_char_prob:
                pass
            elif self._duplicate_char_prob > 0 and random.random() <= self._duplicate_char_prob:
                new_surface += cur_surface[i] * 2
            elif (self._swap_char_prob > 0
                  and i + 1 < len(cur_surface)
                  and random.random() <= self._swap_char_prob):
                new_surface += cur_surface[i + 1]
                new_surface += cur_surface[i]
                i += 1
            else:
                new_surface += cur_surface[i]
            i += 1
        return new_surface
