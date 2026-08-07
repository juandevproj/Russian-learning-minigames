import sqlite3

def init_database():
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Drop old table if it exists to reset
    cursor.execute('DROP TABLE IF EXISTS phrases')
    
    # Clean, single-column schema
    cursor.execute('''
        CREATE TABLE phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrase_text TEXT NOT NULL
        )
    ''')
    
    # You just type normal sentences with brackets around the target word!
    test_data = [
        ("Я хочу купить [новый] дом.",),
        ("Я живу в [новом] доме.",),
        ("Вчера я видел твоего [брата].",)
    ]
    
    cursor.executemany('INSERT INTO phrases (phrase_text) VALUES (?)', test_data)
    conn.commit()
    conn.close()
    print("Database re-initialized with the smart syntax!")


def init_dropout_table():
    """Sets up the phrase bank for the Million Kopeki Drop motion-verb game."""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS dropout_phrases')

    cursor.execute('''
        CREATE TABLE dropout_phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrase_text TEXT NOT NULL
        )
    ''')

    # Bracketed word must be a prefixed Russian motion verb (see MOTION_VERB_FAMILIES in app.py)
    dropout_data = [
        ("Каждое утро директор [входит] в кабинет ровно в восемь.",),
        ("Вчера вечером он наконец [вошёл] в дом после долгой прогулки.",),
        ("Мы часто [приезжаем] в деревню на выходные.",),
        ("Завтра поезд [приедет] на станцию в полдень.",),
        ("Дети постоянно [забегают] в магазин за конфетами.",),
        ("Она быстро [прибежала] на работу, опоздав на пять минут.",),
        ("Самолёт обычно [пролетает] над горами по этому маршруту.",),
        ("Мы [прилетим] в Москву поздно ночью.",),
        ("Я всегда [приношу] домой свежий хлеб.",),
        ("Рабочие [привезли] новое оборудование на завод.",),
        # 50 additional phrases covering all 12 motion-verb families
        ("Он часто [заходит] к нам по вечерам.",),
        ("Мы обычно [выходим] из дома в семь утра.",),
        ("Дети [переходят] улицу только на зелёный свет.",),
        ("Я никогда не [подхожу] к чужим собакам.",),
        ("Наконец мы [дошли] до вершины горы.",),
        ("Она тихо [вышла] из комнаты.",),
        ("Гости [придут] к восьми часам.",),
        ("Он [подошёл] ко мне и поздоровался.",),
        ("Мы каждый год [переезжаем] в новую квартиру.",),
        ("Автобус обычно [подъезжает] к остановке вовремя.",),
        ("Туристы часто [заезжают] в этот городок.",),
        ("Я [уезжаю] из страны через неделю.",),
        ("Мы [доехали] до аэропорта без пробок.",),
        ("Машина [заехала] во двор и остановилась.",),
        ("Завтра он [уедет] в командировку.",),
        ("Мы [объехали] пробку по соседней улице.",),
        ("Собака [убегает] от хозяина каждый раз на прогулке.",),
        ("Спортсмены [пробегают] десять километров каждое утро.",),
        ("Кот [перебегает] дорогу перед машинами.",),
        ("Мы иногда [забегаем] в кафе после работы.",),
        ("Ребёнок [выбежал] на улицу без куртки.",),
        ("Мы [добежали] до финиша первыми.",),
        ("Вор [убежал] от полиции.",),
        ("Она [подбежала] к телефону, услышав звонок.",),
        ("Птицы [улетают] на юг осенью.",),
        ("Наш самолёт обычно [вылетает] рано утром.",),
        ("Пчела [залетает] в открытое окно.",),
        ("Мы часто [перелетаем] через океан по делам.",),
        ("Ракета [долетела] до орбиты за девять минут.",),
        ("Птица [влетела] в комнату через форточку.",),
        ("Самолёт [прилетит] в полночь.",),
        ("Листья [слетели] с дерева на землю.",),
        ("Официант [подносит] гостям меню.",),
        ("Мы [выносим] мусор каждый вечер.",),
        ("Ветер [уносит] листья далеко в поле.",),
        ("Я всегда [отношу] книги обратно в библиотеку вовремя.",),
        ("Официант [принёс] нам горячий кофе.",),
        ("Она [отнесла] письмо на почту.",),
        ("Рабочие [снесли] старое здание за неделю.",),
        ("Я [занесу] документы завтра утром.",),
        ("Компания [перевозит] грузы по всей стране.",),
        ("Такси обычно [подвозит] пассажиров к вокзалу.",),
        ("Родители [отвозят] детей в школу по утрам.",),
        ("Фермеры [привозят] свежие овощи на рынок.",),
        ("Друг [подвёз] меня до дома вчера вечером.",),
        ("Мы [перевезли] всю мебель за один день.",),
        ("Водитель [довёз] нас до самого аэропорта.",),
        ("Курьер [привезёт] посылку завтра.",),
        ("Туристы [обходят] музей за два часа.",),
        ("Мы [сошли] с поезда на конечной станции.",),
    ]

    cursor.executemany('INSERT INTO dropout_phrases (phrase_text) VALUES (?)', dropout_data)
    conn.commit()
    conn.close()
    print("Dropout phrase bank initialized!")


def init_race_words_table():
    """Sets up the 100-word English/Russian vocabulary bank for the Kavkaz racing game."""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS race_words')

    cursor.execute('''
        CREATE TABLE race_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english_word TEXT NOT NULL,
            russian_word TEXT NOT NULL
        )
    ''')

    race_word_data = [
        ("cat", "кошка"), ("dog", "собака"), ("house", "дом"), ("water", "вода"), ("bread", "хлеб"),
        ("car", "машина"), ("city", "город"), ("day", "день"), ("night", "ночь"), ("friend", "друг"),
        ("book", "книга"), ("table", "стол"), ("chair", "стул"), ("window", "окно"), ("door", "дверь"),
        ("sun", "солнце"), ("moon", "луна"), ("star", "звезда"), ("tree", "дерево"), ("flower", "цветок"),
        ("mountain", "гора"), ("river", "река"), ("sea", "море"), ("sky", "небо"), ("fire", "огонь"),
        ("ice", "лёд"), ("snow", "снег"), ("rain", "дождь"), ("wind", "ветер"), ("love", "любовь"),
        ("life", "жизнь"), ("death", "смерть"), ("work", "работа"), ("money", "деньги"), ("time", "время"),
        ("year", "год"), ("month", "месяц"), ("week", "неделя"), ("hour", "час"), ("name", "имя"),
        ("word", "слово"), ("language", "язык"), ("country", "страна"), ("world", "мир"), ("people", "люди"),
        ("man", "мужчина"), ("woman", "женщина"), ("child", "ребёнок"), ("mother", "мать"), ("father", "отец"),
        ("brother", "брат"), ("sister", "сестра"), ("family", "семья"), ("food", "еда"), ("milk", "молоко"),
        ("tea", "чай"), ("coffee", "кофе"), ("meat", "мясо"), ("fish", "рыба"), ("egg", "яйцо"),
        ("cheese", "сыр"), ("apple", "яблоко"), ("red", "красный"), ("blue", "синий"), ("green", "зелёный"),
        ("black", "чёрный"), ("white", "белый"), ("big", "большой"), ("small", "маленький"), ("good", "хороший"),
        ("bad", "плохой"), ("new", "новый"), ("old", "старый"), ("hot", "горячий"), ("cold", "холодный"),
        ("fast", "быстрый"), ("slow", "медленный"), ("happy", "счастливый"), ("sad", "грустный"), ("beautiful", "красивый"),
        ("strong", "сильный"), ("weak", "слабый"), ("easy", "лёгкий"), ("difficult", "трудный"), ("right", "правый"),
        ("left", "левый"), ("today", "сегодня"), ("tomorrow", "завтра"), ("yesterday", "вчера"), ("morning", "утро"),
        ("evening", "вечер"), ("school", "школа"), ("teacher", "учитель"), ("student", "студент"), ("doctor", "врач"),
        ("hospital", "больница"), ("train", "поезд"), ("airplane", "самолёт"), ("road", "дорога"), ("bridge", "мост"),
        # 300 additional common words (pronouns, prepositions, verbs, nouns, adjectives) added later
        ("I", "я"), ("you", "ты"),
        ("he", "он"), ("she", "она"),
        ("it", "оно"), ("we", "мы"),
        ("you (formal/pl.)", "вы"), ("they", "они"),
        ("this/it", "это"), ("that (one)", "тот"),
        ("this (one)", "этот"), ("which", "который"),
        ("one's own", "свой"), ("oneself", "себя"),
        ("who", "кто"), ("what", "что"),
        ("all/everyone", "весь"), ("every", "каждый"),
        ("nobody", "никто"), ("nothing", "ничто"),
        ("himself", "сам"), ("the most", "самый"),
        ("such", "такой"), ("any kind of", "всякий"),
        ("someone", "кто-то"), ("something", "что-то"),
        ("never", "никогда"), ("always", "всегда"),
        ("sometimes", "иногда"), ("everywhere", "везде"),
        ("nowhere", "нигде"), ("to where", "куда"),
        ("from where", "откуда"), ("why/what for", "зачем"),
        ("why", "почему"), ("because", "потому что"),
        ("if", "если"), ("although", "хотя"),
        ("in order to", "чтобы"), ("when", "когда"),
        ("in/at", "в"), ("on", "на"),
        ("with", "с"), ("towards", "к"),
        ("from", "от"), ("until", "до"),
        ("out of", "из"), ("at (someone's)", "у"),
        ("about", "о"), ("about (alt.)", "об"),
        ("in the presence of", "при"), ("for", "для"),
        ("behind/for", "за"), ("along", "по"),
        ("above", "над"), ("under", "под"),
        ("between", "между"), ("through", "через"),
        ("without", "без"), ("about (colloq.)", "про"),
        ("and", "и"), ("but/and", "а"),
        ("but", "но"), ("or", "или"),
        ("neither/nor", "ни"), ("yes", "да"),
        ("to be", "быть"), ("can/to be able", "мочь"),
        ("to say", "сказать"), ("to speak", "говорить"),
        ("to know", "знать"), ("to become", "стать"),
        ("to go (on foot)", "идти"), ("to see", "видеть"),
        ("to look", "смотреть"), ("to think", "думать"),
        ("to want", "хотеть"), ("to give", "дать"),
        ("to take", "брать"), ("to take (once)", "взять"),
        ("to stand", "стоять"), ("to live", "жить"),
        ("to seem", "казаться"), ("to work", "работать"),
        ("to write", "писать"), ("to read", "читать"),
        ("to hear", "слышать"), ("to understand", "понимать"),
        ("to love", "любить"), ("to play", "играть"),
        ("to do", "делать"), ("to arrive", "приходить"),
        ("to find", "находить"), ("to ask (question)", "спрашивать"),
        ("to answer", "отвечать"), ("to begin", "начинать"),
        ("to finish", "кончать"), ("to remember", "помнить"),
        ("to forget", "забывать"), ("to believe", "верить"),
        ("to hope", "надеяться"), ("to be afraid", "бояться"),
        ("to feel", "чувствовать"), ("to please/like", "нравиться"),
        ("to meet", "встречать"), ("to call (phone)", "звонить"),
        ("to buy", "покупать"), ("to sell", "продавать"),
        ("to pay", "платить"), ("to cost", "стоить"),
        ("to die", "умирать"), ("to be born", "родиться"),
        ("to grow", "расти"), ("to study", "учиться"),
        ("to teach", "учить"), ("to help", "помогать"),
        ("to wait", "ждать"), ("to search", "искать"),
        ("to lose", "терять"), ("to catch", "ловить"),
        ("to run", "бежать"), ("to swim", "плыть"),
        ("to drive/lead", "водить"), ("to put (lay)", "класть"),
        ("to place (stand)", "ставить"), ("to sit down", "садиться"),
        ("to get up", "вставать"), ("to lie down", "ложиться"),
        ("to sleep", "спать"), ("to wake up", "просыпаться"),
        ("to cook", "готовить"), ("to wash", "мыть"),
        ("to build", "строить"), ("to break", "ломать"),
        ("to open", "открывать"), ("to close", "закрывать"),
        ("hand", "рука"), ("leg", "нога"),
        ("eye", "глаз"), ("face", "лицо"),
        ("head", "голова"), ("heart", "сердце"),
        ("soul", "душа"), ("body", "тело"),
        ("finger", "палец"), ("ear", "ухо"),
        ("mouth", "рот"), ("tooth", "зуб"),
        ("hair", "волосы"), ("back", "спина"),
        ("shoulder", "плечо"), ("one", "один"),
        ("two", "два"), ("three", "три"),
        ("four", "четыре"), ("five", "пять"),
        ("six", "шесть"), ("seven", "семь"),
        ("eight", "восемь"), ("nine", "девять"),
        ("ten", "десять"), ("hundred", "сто"),
        ("thousand", "тысяча"), ("million", "миллион"),
        ("very", "очень"), ("here", "здесь"),
        ("there", "там"), ("to here", "сюда"),
        ("to there", "туда"), ("now", "сейчас"),
        ("then/later", "потом"), ("early", "рано"),
        ("late", "поздно"), ("quickly", "быстро"),
        ("slowly", "медленно"), ("well", "хорошо"),
        ("badly", "плохо"), ("loudly", "громко"),
        ("quietly", "тихо"), ("together", "вместе"),
        ("separately", "отдельно"), ("nearby", "близко"),
        ("far away", "далеко"), ("inside", "внутри"),
        ("question", "вопрос"), ("answer", "ответ"),
        ("problem", "проблема"), ("idea", "идея"),
        ("thought", "мысль"), ("plan", "план"),
        ("goal", "цель"), ("reason", "причина"),
        ("result", "результат"), ("history/story", "история"),
        ("case/incident", "случай"), ("fact", "факт"),
        ("example", "пример"), ("part", "часть"),
        ("number", "число"), ("quantity", "количество"),
        ("side", "сторона"), ("place", "место"),
        ("point", "точка"), ("line", "линия"),
        ("shape", "форма"), ("size", "размер"),
        ("weight", "вес"), ("color", "цвет"),
        ("sound", "звук"), ("voice", "голос"),
        ("music", "музыка"), ("song", "песня"),
        ("picture", "картина"), ("movie", "фильм"),
        ("theater", "театр"), ("art", "искусство"),
        ("science", "наука"), ("computer", "компьютер"),
        ("phone", "телефон"), ("letter (mail)", "письмо"),
        ("newspaper", "газета"), ("magazine", "журнал"),
        ("lesson", "урок"), ("exam", "экзамен"),
        ("class", "класс"), ("team", "команда"),
        ("game", "игра"), ("sport", "спорт"),
        ("law", "закон"), ("right (legal)", "право"),
        ("court", "суд"), ("freedom", "свобода"),
        ("truth", "правда"), ("lie", "ложь"),
        ("happiness", "счастье"), ("grief", "горе"),
        ("fear", "страх"), ("anger", "гнев"),
        ("joy", "радость"), ("health", "здоровье"),
        ("illness", "болезнь"), ("pain", "боль"),
        ("medicine", "лекарство"), ("street", "улица"),
        ("square", "площадь"), ("forest", "лес"),
        ("field", "поле"), ("garden", "сад"),
        ("factory", "завод"), ("young", "молодой"),
        ("tall/high", "высокий"), ("low", "низкий"),
        ("long", "длинный"), ("short", "короткий"),
        ("wide", "широкий"), ("narrow", "узкий"),
        ("deep", "глубокий"), ("shallow", "мелкий"),
        ("heavy", "тяжёлый"), ("clean", "чистый"),
        ("dirty", "грязный"), ("full", "полный"),
        ("empty", "пустой"), ("rich", "богатый"),
        ("poor", "бедный"), ("smart", "умный"),
        ("stupid", "глупый"), ("kind", "добрый"),
        ("evil/angry", "злой"), ("cheerful", "весёлый"),
        ("boring", "скучный"), ("interesting", "интересный"),
        ("important", "важный"), ("dangerous", "опасный"),
        ("safe", "безопасный"), ("free", "свободный"),
        ("busy", "занятый"), ("ready", "готовый"),
        ("alive", "живой"), ("dead", "мёртвый"),
        ("healthy", "здоровый"), ("sick", "больной"),
        ("dry", "сухой"), ("wet", "мокрый"),
        ("loud", "громкий"), ("quiet", "тихий"),
        ("bright/light", "светлый"), ("dark", "тёмный"),
        ("straight", "прямой"), ("crooked", "кривой"),
        ("sharp", "острый"), ("blunt", "тупой"),
        ("soft", "мягкий"), ("hard/firm", "твёрдый"),
        ("smooth", "гладкий"), ("expensive", "дорогой"),
        ("cheap", "дешёвый"), ("fresh", "свежий"),
        ("tasty", "вкусный"), ("sweet", "сладкий"),
    ]

    cursor.executemany('INSERT INTO race_words (english_word, russian_word) VALUES (?, ?)', race_word_data)
    conn.commit()
    conn.close()
    print("Race word bank initialized!")


if __name__ == "__main__":
    init_database()
    init_dropout_table()
    init_race_words_table()