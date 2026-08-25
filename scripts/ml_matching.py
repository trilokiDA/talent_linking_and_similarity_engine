import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "ml_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def preprocess_name(name):
    if not name:
        return ""

    # Remove titles
    name = re.sub(r'\b(Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?|Miss)\s+', '', name, flags=re.IGNORECASE)

    # Lowercase and strip whitespace
    name = name.lower().strip()

    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)

    return name

def preprocess_location(location):
    if not location:
        return ""

    # Common abbreviations
    abbreviations = {
        r'\bCA\b': 'California',
        r'\bNY\b': 'New York',
        r'\bSF\b': 'San Francisco',
        r'\bUSA\b': 'United States',
        r'\bU\.S\.A\b': 'United States',
        r'\bUK\b': 'United Kingdom',
    }

    location = location.lower()

    # Expand abbreviations
    for abbr, full in abbreviations.items():
        location = re.sub(abbr, full, location, flags=re.IGNORECASE)

    # Strip and normalize whitespace
    location = re.sub(r'\s+', ' ', location.strip())

    return location

class NameEmbedder:
    def __init__(self, config):
        self.config = config
        ngram_range = tuple(config['embeddings']['name']['char_ngram_range'])
        n_components = config['embeddings']['name']['svd_components']

        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='char',
            ngram_range=ngram_range,
            lowercase=True
        )
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.tfidf_weight = config['embeddings']['name']['tfidf_weight']
        self.fasttext_weight = config['embeddings']['name']['fasttext_weight']

    def fit(self, names):
        # Preprocess names
        processed_names = [preprocess_name(name) for name in names]

        # Fit TF-IDF
        tfidf_features = self.tfidf_vectorizer.fit_transform(processed_names)

        # Fit SVD
        self.svd.fit(tfidf_features)

        return self

    def transform_tfidf(self, names):
        processed_names = [preprocess_name(name) for name in names]
        tfidf_features = self.tfidf_vectorizer.transform(processed_names)
        svd_features = self.svd.transform(tfidf_features)
        normalized_features = normalize(svd_features, norm='l2')
        return normalized_features

    def transform_fasttext(self, names, fasttext_model):
        embeddings = []
        vector_size = fasttext_model.wv.vector_size
        for name in names:
            processed = preprocess_name(name)
            if not processed:
                embeddings.append(np.zeros(vector_size))
            else:
                words = processed.split()
                if words:
                    word_vectors = []
                    for word in words:
                        if word in fasttext_model.wv:
                            word_vectors.append(fasttext_model.wv[word])
                        else:
                            # Use zero vector for OOV words
                            word_vectors.append(np.zeros(vector_size))
                    if word_vectors:
                        embedding = np.mean(word_vectors, axis=0)
                        embeddings.append(embedding)
                    else:
                        embeddings.append(np.zeros(vector_size))
                else:
                    embeddings.append(np.zeros(vector_size))

        embeddings = np.array(embeddings)
        return normalize(embeddings, norm='l2')

    def transform_hybrid(self, names, fasttext_model):
        tfidf_embeddings = self.transform_tfidf(names)
        fasttext_embeddings = self.transform_fasttext(names, fasttext_model)

        # Check dimensions match
        if tfidf_embeddings.shape[1] != fasttext_embeddings.shape[1]:
            # Pad the smaller one with zeros
            max_dim = max(tfidf_embeddings.shape[1], fasttext_embeddings.shape[1])
            if tfidf_embeddings.shape[1] < max_dim:
                padding = np.zeros((tfidf_embeddings.shape[0], max_dim - tfidf_embeddings.shape[1]))
                tfidf_embeddings = np.hstack([tfidf_embeddings, padding])
            if fasttext_embeddings.shape[1] < max_dim:
                padding = np.zeros((fasttext_embeddings.shape[0], max_dim - fasttext_embeddings.shape[1]))
                fasttext_embeddings = np.hstack([fasttext_embeddings, padding])

        # Hybrid combination
        hybrid = (self.tfidf_weight * tfidf_embeddings +
                  self.fasttext_weight * fasttext_embeddings)

        return normalize(hybrid, norm='l2')

class LocationEmbedder:
    def __init__(self, config):
        self.config = config
        ngram_range = tuple(config['embeddings']['location']['word_ngram_range'])
        n_components = config['embeddings']['location']['svd_components']

        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=ngram_range,
            lowercase=True
        )
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.tfidf_weight = config['embeddings']['location']['tfidf_weight']
        self.fasttext_weight = config['embeddings']['location']['fasttext_weight']

    def fit(self, locations):
        # Preprocess locations
        processed_locations = [preprocess_location(loc) for loc in locations]

        # Fit TF-IDF
        tfidf_features = self.tfidf_vectorizer.fit_transform(processed_locations)

        # Fit SVD
        self.svd.fit(tfidf_features)

        return self

    def transform_tfidf(self, locations):
        processed_locations = [preprocess_location(loc) for loc in locations]
        tfidf_features = self.tfidf_vectorizer.transform(processed_locations)
        svd_features = self.svd.transform(tfidf_features)
        normalized_features = normalize(svd_features, norm='l2')
        return normalized_features

    def transform_fasttext(self, locations, fasttext_model):
        embeddings = []
        vector_size = fasttext_model.wv.vector_size
        for location in locations:
            processed = preprocess_location(location)
            if not processed:
                embeddings.append(np.zeros(vector_size))
            else:
                words = processed.split()
                if words:
                    word_vectors = []
                    for word in words:
                        if word in fasttext_model.wv:
                            word_vectors.append(fasttext_model.wv[word])
                        else:
                            # Use zero vector for OOV words
                            word_vectors.append(np.zeros(vector_size))
                    if word_vectors:
                        embedding = np.mean(word_vectors, axis=0)
                        embeddings.append(embedding)
                    else:
                        embeddings.append(np.zeros(vector_size))
                else:
                    embeddings.append(np.zeros(vector_size))

        embeddings = np.array(embeddings)
        return normalize(embeddings, norm='l2')

    def transform_hybrid(self, locations, fasttext_model):
        tfidf_embeddings = self.transform_tfidf(locations)
        fasttext_embeddings = self.transform_fasttext(locations, fasttext_model)

        # Check dimensions match
        if tfidf_embeddings.shape[1] != fasttext_embeddings.shape[1]:
            # Pad the smaller one with zeros
            max_dim = max(tfidf_embeddings.shape[1], fasttext_embeddings.shape[1])
            if tfidf_embeddings.shape[1] < max_dim:
                padding = np.zeros((tfidf_embeddings.shape[0], max_dim - tfidf_embeddings.shape[1]))
                tfidf_embeddings = np.hstack([tfidf_embeddings, padding])
            if fasttext_embeddings.shape[1] < max_dim:
                padding = np.zeros((fasttext_embeddings.shape[0], max_dim - fasttext_embeddings.shape[1]))
                fasttext_embeddings = np.hstack([fasttext_embeddings, padding])

        # Hybrid combination
        hybrid = (self.tfidf_weight * tfidf_embeddings +
                  self.fasttext_weight * fasttext_embeddings)

        return normalize(hybrid, norm='l2')

def compute_profile_similarity(borealis_profile, candidate_profile,
                                name_embedder, location_embedder,
                                fasttext_model, config):
    # Extract fields
    b_name = borealis_profile.get('full_name', '')
    b_location = borealis_profile.get('full_adress', '')
    c_name = candidate_profile.get('full_name', '')
    c_location = candidate_profile.get('full_adress', '')

    # Compute name similarity
    name_emb_b = name_embedder.transform_hybrid([b_name], fasttext_model)
    name_emb_c = name_embedder.transform_hybrid([c_name], fasttext_model)
    name_similarity = cosine_similarity(name_emb_b, name_emb_c)[0][0]

    # Compute location similarity
    location_emb_b = location_embedder.transform_hybrid([b_location], fasttext_model)
    location_emb_c = location_embedder.transform_hybrid([c_location], fasttext_model)
    location_similarity = cosine_similarity(location_emb_b, location_emb_c)[0][0]

    # Weighted combination
    name_weight = config['matching']['name_weight']
    location_weight = config['matching']['location_weight']

    final_score = name_weight * name_similarity + location_weight * location_similarity

    return {
        'final_score': float(final_score),
        'name_similarity': float(name_similarity),
        'location_similarity': float(location_similarity)
    }

def find_best_match(borealis_profile, candidate_profiles,
                    name_embedder, location_embedder,
                    fasttext_model, config):
    threshold = config['matching']['similarity_threshold']

    best_match = None
    best_score_info = None

    for candidate in candidate_profiles:
        score_info = compute_profile_similarity(
            borealis_profile, candidate,
            name_embedder, location_embedder,
            fasttext_model, config
        )

        if score_info['final_score'] >= threshold:
            if best_match is None or score_info['final_score'] > best_score_info['final_score']:
                best_match = candidate
                best_score_info = score_info

    return best_match, best_score_info
