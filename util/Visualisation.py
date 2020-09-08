import matplotlib.pyplot as plt
import pandas as pd
import os


def load_result(file_name):
    path = os.path.dirname(os.path.dirname(__file__)) + '/result/'
    result = pd.read_excel(path+file_name)
    return result


def visualise_cos_sim(w2v, bert):
    topics = [i for i in range(len(w2v))]
    plt.title('Result Analysis')
    plt.plot(topics, w2v, color='green', label='Word2Vec')
    plt.plot(topics, bert, color='blue', label='Bert')
    plt.legend()

    plt.xlabel('Topic Sampler')
    plt.ylabel('Cosine Similarity')
    plt.show()

