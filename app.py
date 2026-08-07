from flask import Flask, render_template, jsonify, request
import sqlite3
import pymorphy3
import re
import random
import os

app = Flask(__name__)
morph = pymorphy3.MorphAnalyzer()

# Always resolve game.db relative to this file's own location, not the process's
# working directory (which WSGI hosts don't always set the way you'd expect).
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game.db')

# Russian verb-of-motion families: dictionary root -> (aspect of the prefixed forms, prefixed infinitives).
# Prefixing an unprefixed motion verb always yields a fixed aspect: the "-ходить/-ездить/..." derived
# stems are imperfective, the "-йти/-ехать/..." derived stems are perfective.
MOTION_VERB_FAMILIES = {
    "ходить": ("impf", ["входить", "выходить", "доходить", "заходить", "находить", "обходить", "отходить", "переходить", "подходить", "приходить", "проходить", "сходить", "уходить"]),
    "идти":   ("perf", ["войти", "выйти", "дойти", "зайти", "найти", "обойти", "отойти", "перейти", "подойти", "прийти", "пройти", "сойти", "уйти"]),
    "ездить": ("impf", ["въезжать", "выезжать", "доезжать", "заезжать", "наезжать", "объезжать", "отъезжать", "переезжать", "подъезжать", "приезжать", "проезжать", "съезжать", "уезжать"]),
    "ехать":  ("perf", ["въехать", "выехать", "доехать", "заехать", "наехать", "объехать", "отъехать", "переехать", "подъехать", "приехать", "проехать", "съехать", "уехать"]),
    "бегать": ("impf", ["вбегать", "выбегать", "добегать", "забегать", "набегать", "обегать", "отбегать", "перебегать", "подбегать", "прибегать", "пробегать", "сбегать", "убегать"]),
    "бежать": ("perf", ["вбежать", "выбежать", "добежать", "забежать", "набежать", "обежать", "отбежать", "перебежать", "подбежать", "прибежать", "пробежать", "сбежать", "убежать"]),
    "летать": ("impf", ["влетать", "вылетать", "долетать", "залетать", "налетать", "облетать", "отлетать", "перелетать", "подлетать", "прилетать", "пролетать", "слетать", "улетать"]),
    "лететь": ("perf", ["влететь", "вылететь", "долететь", "залететь", "налететь", "облететь", "отлететь", "перелететь", "подлететь", "прилететь", "пролететь", "слететь", "улететь"]),
    "носить": ("impf", ["вносить", "выносить", "доносить", "заносить", "наносить", "обносить", "относить", "переносить", "подносить", "приносить", "проносить", "сносить", "уносить"]),
    "нести":  ("perf", ["внести", "вынести", "донести", "занести", "нанести", "обнести", "отнести", "перенести", "поднести", "принести", "пронести", "снести", "унести"]),
    "возить": ("impf", ["ввозить", "вывозить", "довозить", "завозить", "навозить", "обвозить", "отвозить", "перевозить", "подвозить", "привозить", "провозить", "свозить", "увозить"]),
    "везти":  ("perf", ["ввезти", "вывезти", "довезти", "завезти", "навезти", "обвезти", "отвезти", "перевезти", "подвезти", "привезти", "провезти", "свезти", "увезти"]),
}

# Reverse lookup: prefixed infinitive -> family root
_LEMMA_TO_FAMILY = {}
for _family, (_aspect, _verbs) in MOTION_VERB_FAMILIES.items():
    for _v in _verbs:
        _LEMMA_TO_FAMILY[_v] = _family


def _best_infinitive_parse(word, expected_aspect):
    """
    pymorphy3's top parse for some prefixed motion verbs (e.g. 'выносить') picks an
    unrelated homograph lexeme (a different verb sharing the same spelling) instead of
    the motion-compound. Explicitly select the INFN parse matching the family's known
    aspect rather than trusting parse()[0].
    """
    for p in morph.parse(word):
        if p.tag.POS == 'INFN' and p.tag.aspect == expected_aspect:
            return p
    return morph.parse(word)[0]


def _best_lexeme_parse(word):
    """
    The correct_word itself can also be a homograph of an unrelated lexeme (e.g. 'выходим'
    is also a conjugated form of a perfective verb meaning 'to nurse back to health', with
    a different tense). Prefer the parse whose lemma belongs to a known motion-verb family
    and whose aspect matches that family's expected aspect, rather than trusting parse()[0].
    """
    candidates = [p for p in morph.parse(word) if p.normal_form in _LEMMA_TO_FAMILY]
    for p in candidates:
        family = _LEMMA_TO_FAMILY[p.normal_form]
        expected_aspect = MOTION_VERB_FAMILIES[family][0]
        if p.tag.aspect == expected_aspect:
            return p
    if candidates:
        return candidates[0]
    return morph.parse(word)[0]


def get_verb_grammemes(tag):
    """Extracts the person/gender/number/tense needed to inflect a sibling verb into the same form."""
    grams = set()
    if tag.tense:
        grams.add(tag.tense)
    if tag.tense == 'past':
        if tag.gender:
            grams.add(tag.gender)
        if tag.number:
            grams.add(tag.number)
    else:
        if tag.person:
            grams.add(tag.person)
        if tag.number:
            grams.add(tag.number)
    return grams


def generate_motion_verb_options(correct_word):
    """
    Given a correctly-inflected prefixed motion verb, finds sibling verbs from the same
    motion-verb family (same root, different prefix) and inflects them into the same
    person/tense/number/gender so they read as grammatically valid distractors.
    """
    parsed = _best_lexeme_parse(correct_word)
    lemma = parsed.normal_form
    family = _LEMMA_TO_FAMILY.get(lemma)

    options = [correct_word]

    if family:
        expected_aspect, family_verbs = MOTION_VERB_FAMILIES[family]
        siblings = [v for v in family_verbs if v != lemma]
        random.shuffle(siblings)
        grams = get_verb_grammemes(parsed.tag)

        for sibling_lemma in siblings:
            if len(options) >= 4:
                break
            sibling_parsed = _best_infinitive_parse(sibling_lemma, expected_aspect)
            inflected = sibling_parsed.inflect(grams)
            if inflected and inflected.word not in options:
                options.append(inflected.word)

    random.shuffle(options)
    return options

def get_declensions(correct_word):
    """
    Analyzes the bracketed word, finds its dictionary lemma, 
    and generates a strictly ordered matrix of declensions.
    """
    parsed = morph.parse(correct_word)[0]
    pos = parsed.tag.POS
    
    # Extract the dictionary base form (lemma) automatically
    lemma = parsed.normal_form 
    lemma_parsed = morph.parse(lemma)[0]

    # Ordered strictly from Nominative down to Prepositional
    cases = [
        {"tag": "nomn", "display": "Nominative"},
        {"tag": "gent", "display": "Genitive"},
        {"tag": "datv", "display": "Dative"},
        {"tag": "accs", "display": "Accusative"},
        {"tag": "ablt", "display": "Instrumental"},
        {"tag": "loct", "display": "Prepositional"}
    ]
    
    options = []

    if pos == 'NOUN':
        # 6 Rows, 1 Column layout for Nouns
        for c in cases:
            form = lemma_parsed.inflect({c["tag"]})
            if form:
                options.append({
                    "word": form.word, 
                    "label": c["display"]
                })
                
    elif pos == 'ADJF':
        # 6 Rows, 3 Columns for Adjectives.
        # Outer loop: Cases (Rows) | Inner loop: Genders (Columns)
        genders = [
            {"tag": "masc", "display": "Masc"},
            {"tag": "femn", "display": "Fem"},
            {"tag": "neut", "display": "Neut"}
        ]
        for c in cases:
            for g in genders:
                form = lemma_parsed.inflect({g["tag"], 'sing', c["tag"]})
                if form:
                    options.append({
                        "word": form.word, 
                        "label": f"{g['display']} - {c['display']}"
                    })
                    
    return {"type": pos, "options": options}


@app.route('/')
def home():
    """Serves the main landing page containing both games."""
    return render_template('index.html')


@app.route('/declination')
def declination():
    """Serves the declension game page."""
    return render_template('declination.html')


@app.route('/dropout')
def dropout():
    """Serves the Million Kopeki Drop motion-verb betting game."""
    return render_template('dropout.html')


@app.route('/kavkaz')
def kavkaz():
    """Serves the Fast, Furious and Kavkas vocabulary racing game."""
    return render_template('kavkaz.html')


@app.route('/api/get_phrase')
def get_phrase():
    """Fetches a random phrase not yet seen this session, parses target bracket word, and generates grid metadata."""
    exclude_param = request.args.get('exclude', '')
    excluded_ids = [int(x) for x in exclude_param.split(',') if x.strip().isdigit()]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if excluded_ids:
        placeholders = ','.join('?' * len(excluded_ids))
        cursor.execute(
            f"SELECT id, phrase_text FROM phrases WHERE id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT 1",
            excluded_ids
        )
    else:
        cursor.execute("SELECT id, phrase_text FROM phrases ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        # All phrases in the deck have already been shown this session
        return jsonify({"completed": True})

    phrase_id, raw_phrase = row

    # Locate text bounded inside square brackets [ ]
    match = re.search(r'\[(.*?)\]', raw_phrase)
    if not match:
        return jsonify({"error": "Phrase format invalid. Target word must be enclosed in [brackets]."}), 500

    correct_answer = match.group(1)

    # Swap bracketed text with standard game underscores
    display_phrase = re.sub(r'\[(.*?)\]', '_______', raw_phrase)

    # Process options via morphosyntactic mapping rules
    declension_data = get_declensions(correct_answer)

    return jsonify({
        "id": phrase_id,
        "phrase": display_phrase,
        "correct_answer": correct_answer,
        "type": declension_data["type"],
        "options": declension_data["options"]
    })


@app.route('/api/dropout/get_question')
def dropout_get_question():
    """Fetches a random motion-verb phrase not yet seen this session, plus 4 shuffled answer options."""
    exclude_param = request.args.get('exclude', '')
    excluded_ids = [int(x) for x in exclude_param.split(',') if x.strip().isdigit()]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if excluded_ids:
        placeholders = ','.join('?' * len(excluded_ids))
        cursor.execute(
            f"SELECT id, phrase_text FROM dropout_phrases WHERE id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT 1",
            excluded_ids
        )
    else:
        cursor.execute("SELECT id, phrase_text FROM dropout_phrases ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        # Every phrase in the deck has already been shown this session
        return jsonify({"completed": True})

    phrase_id, raw_phrase = row

    match = re.search(r'\[(.*?)\]', raw_phrase)
    if not match:
        return jsonify({"error": "Phrase format invalid. Target verb must be enclosed in [brackets]."}), 500

    correct_answer = match.group(1)
    display_phrase = re.sub(r'\[(.*?)\]', '_______', raw_phrase)
    options = generate_motion_verb_options(correct_answer)

    return jsonify({
        "id": phrase_id,
        "phrase": display_phrase,
        "correct_answer": correct_answer,
        "options": options
    })


@app.route('/api/kavkaz/get_word')
def kavkaz_get_word():
    """Fetches a random English/Russian word pair not yet seen this game, plus a random decoy translation."""
    exclude_param = request.args.get('exclude', '')
    excluded_ids = [int(x) for x in exclude_param.split(',') if x.strip().isdigit()]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    row = None
    reset_happened = False

    if excluded_ids:
        placeholders = ','.join('?' * len(excluded_ids))
        cursor.execute(
            f"SELECT id, english_word, russian_word FROM race_words WHERE id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT 1",
            excluded_ids
        )
        row = cursor.fetchone()

    if not row:
        # Either no exclusions yet, or every word has already been used this game — reset and repeat
        reset_happened = bool(excluded_ids)
        cursor.execute("SELECT id, english_word, russian_word FROM race_words ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()

    word_id, english_word, russian_word = row

    # Decoy: another word's Russian translation, picked at random
    cursor.execute(
        "SELECT russian_word FROM race_words WHERE id != ? ORDER BY RANDOM() LIMIT 1",
        (word_id,)
    )
    decoy_row = cursor.fetchone()
    conn.close()

    return jsonify({
        "id": word_id,
        "english": english_word,
        "correct_russian": russian_word,
        "decoy_russian": decoy_row[0],
        "reset": reset_happened
    })


if __name__ == '__main__':
    # Start server
    app.run(debug=True)