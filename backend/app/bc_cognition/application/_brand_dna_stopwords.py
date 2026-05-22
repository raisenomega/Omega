"""Stopwords ES + EN para keyword extraction en brand_dna_builder.

Mínimas pero cubren la mayoría de palabras funcionales que dominarían
el Counter si no se filtraran. Frozen para evitar mutación accidental.
"""

STOPWORDS_ES: frozenset[str] = frozenset({
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las",
    "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como",
    "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque",
    "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me",
    "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante",
    "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante",
    "ellos", "te", "mi", "qué", "tu", "tus", "ellas", "nosotros", "mis",
    "tú", "ti", "ha", "fue", "ser", "es", "son", "era", "soy", "está",
})

STOPWORDS_EN: frozenset[str] = frozenset({
    "the", "of", "and", "to", "in", "that", "it", "is", "was", "for",
    "on", "are", "as", "with", "they", "be", "at", "this", "have",
    "from", "or", "had", "by", "not", "but", "what", "all", "were",
    "we", "when", "your", "can", "said", "there", "use", "an", "each",
    "which", "their", "if", "will", "do", "how", "has", "more", "her",
    "two", "go", "no", "way", "could", "my",
})

STOPWORDS: frozenset[str] = STOPWORDS_ES | STOPWORDS_EN
