import re
import nltk
import numpy
import gensim
import networkx
from scipy import spatial
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')

def weightpoints(sentences):
    # Clean sentences
    sents_clean = [re.sub(r'[^\w\s]', '', sent.lower()) for sent in sentences]  # remove punctuation
    sents_clean = [re.sub('\n|\xa0|\t', '', sent.lower()) for sent in sents_clean]  # remove weird special characters

    # Remove stopwords
    stop_words = stopwords.words('english')
    sent_tokens = [[word for word in sent.split(' ') if word not in stop_words] for sent in sents_clean]

    # Load Word2Vec model
    w2v = gensim.models.Word2Vec.load('gensim-w2v-eula.model')  # vectorize with word2vec

    # Vectorize sentences
    sent_vecs = [[w2v.wv[word][0] for word in words] for words in sent_tokens]

    # Make all sentence vector arrays the same size
    max_len = max([len(tokens) for tokens in sent_tokens])
    sent_vecs = [numpy.pad(embedding, (0, max_len - len(embedding)), 'constant') for embedding in sent_vecs]

    # Compute similarity matrix
    similarity_matrix = numpy.zeros((len(sent_vecs), len(sent_vecs)))
    for i, row in enumerate(sent_vecs):
        for j, col in enumerate(sent_vecs):
            similarity_matrix[i][j] = 1 - spatial.distance.cosine(row, col)

    # Apply PageRank
    sim_graph = networkx.from_numpy_array(similarity_matrix)
    scores = networkx.pagerank(sim_graph)

    # Create dictionary of sentences and their scores
    sents_dict = {sent: scores[index] for index, sent in enumerate(sentences)}

    return sents_dict