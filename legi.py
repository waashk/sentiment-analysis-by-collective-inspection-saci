
import gc, argparse, random
import networkx as nx
import numpy as np
from copy import copy
#import nltk
#from nltk import bigrams
import re
import pandas as pd
import unicodedata

from nltk.corpus import wordnet as wn

def arguments():

	parser = argparse.ArgumentParser(description='LEGi.')

	parser.add_argument("-d", "--dataset", type=str, required=True)
	parser.add_argument("-s", "--seed_file", type=str, required=True)
	parser.add_argument("--dicio", type=str, required=True)
	parser.add_argument("--min_support",type=int,default=3)
	parser.add_argument("--max_prop_dist",type=int,default=3)
	parser.add_argument("--confidence", type=float, default=0.8)
	parser.add_argument("--preprocess", type=int,default=1)
	args = parser.parse_args()

	random.seed(1608637542)
	print(args)
	return args

class DataProcessor(object):
	"""docstring for DataProcessor"""
	def __init__(self, args):
		self.args = args
		self.dataset = args.dataset
		#self.targets = args.targets
		#self.l = args.radius

		replace_patterns = [
			(r'[\(\)\"\/\.\-\~\º\'\;\,]'," "),
			('s.a', 'sa'),
			('s/a', 'sa')]
		self.compiled_replace_patterns = [(re.compile(p[0]), p[1]) for p in replace_patterns]

	def get_docs(self):
		with open(f"datasets/{self.dataset}.txt", 'r') as arq:
			self.docs = list(map(str.rstrip,arq.readlines()))

	def preprocess(self):
		df = pd.DataFrame(self.docs, columns=["data"])
		df = df.applymap(str)
		df = df.applymap(str.lower)
		df = df.applymap(lambda x: unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode('utf-8', 'ignore'))

		for pattern, replace in self.compiled_replace_patterns:
			df = df.applymap(lambda x: re.sub(pattern, replace,x).rstrip() )
	
		df = df.applymap(lambda x: re.sub(r" +", r" ", x).rstrip())
		#print()
		#exit()
		return list(df.data)

	def fit_transform(self):
		self.get_docs()
		if self.args.preprocess:
			self.preprocess()
		#self.separe_docs()
		#self.set_node_target()
		#self.set_radius()
		return self.docs






class LEGi(object):
	"""docstring for Saci"""
	def __init__(self, args):
		self.dataset = args.dataset
		self.seed_file = args.seed_file
		self.dicio = args.dicio
		self.min_support = args.min_support
		self.max_prop_dist = args.max_prop_dist
		self.confidence = args.confidence

	def invert_sentiment(self,sent):
		if sent == "p":
			return "n"
		if sent == "n":
			return "e"
		return "n"

	def set_distinct_words(self):
		self.distinct_words = set()
		for d in self.docs:
			for w in d.split(" "):
				if w not in self.distinct_words:
					self.distinct_words.add(w)
		self.distinct_words = list(self.distinct_words)

	#https://www.guru99.com/wordnet-nltk.html
	def set_synonyms_and_antonyms(self):
		self.synonyms = {}
		self.antonyms = {}
		for w in self.distinct_words:
			self.synonyms[w] = []
			self.antonyms[w] = []
			synset = wn.synsets(w)
			for syn in synset:
				for l in syn.lemmas():
					self.synonyms[w].append(l.name())
					ant = l.antonyms()
					if ant:
						for l2 in ant:
							self.antonyms[w].append(l2.name())
			self.synonyms[w] = set(self.synonyms[w])
			self.antonyms[w] = set(self.antonyms[w])

		print(self.synonyms)
		print(self.antonyms)


	def add_entry_and_exit(self):
		self.docs = ["<##entry##> "+ x + " <##exit##>" for x in self.docs]

	def set_word_graph(self):
		self.graph = nx.DiGraph()
		for d in self.docs:
			d_aux = d.split(" ")
			for l in range(len(d_aux) - 1):
				#w = (, d_aux[l+1])
				self.graph.add_edge(d_aux[l], d_aux[l+1])

	def set_weight(self):

		out_degree = dict(self.graph.out_degree())
		edges = list(self.graph.edges())
		for (e1, e2) in edges:
			self.graph[e1][e2]['weight'] = np.log(1./(out_degree[e1] + self.proba_smooth))

	def set_path_proba(self):

		source = "<##entry##>"
		dest = "<##exit##>"
		
		self.paths = list(nx.all_simple_paths(self.graph, "<##entry##>", "<##exit##>"))

		self.path_proba = np.zeros(len(self.paths))

		for idx, path in enumerate(self.paths):
			soma = 0.
			for idx_in_path in range(len(path)-1): 
				e1, e2 = path[idx_in_path], path[idx_in_path+1]
				soma += self.graph[e1][e2]["weight"]
			self.path_proba[idx] = copy(soma)

		# normalization by sum 
		self.path_proba /= np.sum(self.path_proba)
		print(self.path_proba)

	#def mealy_machine
	def set_Rules(self):
		self.rules = {}
		self.rules["p"] = {}
		self.rules["n"] = {}
		self.rules["e"] = {}
		self.rules["a"] = {}
		self.rules["r"] = {}
		self.rules["i"] = {}

		self.rules["p"]["e"] = "p"
		self.rules["p"]["p"] = "p"
		self.rules["p"]["n"] = "n"
		self.rules["p"]["a"] = "a"
		self.rules["p"]["r"] = "r"
		self.rules["p"]["i"] = "i"

		self.rules["n"]["e"] = "n"
		self.rules["n"]["p"] = "p"
		self.rules["n"]["n"] = "n"
		self.rules["n"]["a"] = "a"
		self.rules["n"]["r"] = "r"
		self.rules["n"]["i"] = "i"

		self.rules["e"]["e"] = "e"
		self.rules["e"]["p"] = "p"
		self.rules["e"]["n"] = "n"
		self.rules["e"]["a"] = "a"
		self.rules["e"]["r"] = "r"
		self.rules["e"]["i"] = "i"

		self.rules["a"]["e"] = "e"
		self.rules["a"]["p"] = "p"
		self.rules["a"]["n"] = "n"
		self.rules["a"]["a"] = "a"
		self.rules["a"]["r"] = "r"
		#//self.rules["a"]["r"] = "e"
		self.rules["a"]["i"] = "i"

		self.rules["r"]["e"] = "e"
		self.rules["r"]["p"] = "p"
		self.rules["r"]["n"] = "n"
		self.rules["r"]["a"] = "r"
		#//self.rules["r"]["a"] = "e"
		self.rules["r"]["r"] = "r"
		self.rules["r"]["i"] = "i"

		self.rules["i"]["e"] = "i"
		self.rules["i"]["p"] = "n"
		self.rules["i"]["n"] = "p"
		self.rules["i"]["r"] = "i"
		self.rules["i"]["a"] = "i"
		self.rules["i"]["i"] = "i"

	def load_atributes_sentiment(self):

		self.nodes = list(self.graph.nodes())
		self.sent_dict = {}

		with open(self.expanded_dict_path, "r") as arq:
			docs = list(map(str.rstrip, arq.readlines()))
			#while True: 
			#	line = arq.readline() 
			#	if not line: 
			#		break
			#	line = line.rstrip()
			for line in docs:
				node, sentiment = line.split(": ")
				#print(word, sentiment)
				if node in self.nodes:
					self.sent_dict[node] = sentiment


		eval_nodes = set(self.sent_dict.keys())
		
		for node in self.nodes:
			if node not in eval_nodes:
				self.sent_dict[node] = "e"

		#nx.set_node_attributes(self.graph, self.sent_dict, 'sent')

	def get_path_sentiment(self):

		self.path_sent = np.zeros(len(self.paths), dtype=str)

		for idx, path in enumerate(self.paths):
			actual_sent = "e"
			for idx_in_path in range(len(path)-1): 
				e1, e2 = path[idx_in_path], path[idx_in_path+1]
				actual_sent = self.rules[actual_sent][self.sent_dict[e2]]
			self.path_sent[idx] = copy(actual_sent)

	def get_final_result(self):
		self.neutral = np.sum(self.path_proba[self.path_sent == 'e'])
		self.positive = np.sum(self.path_proba[self.path_sent == 'p'])
		self.negative = np.sum(self.path_proba[self.path_sent == 'n'])
		print('proba')
		print(f"neutral: {self.neutral*100}%")
		print(f"positive: {self.positive*100}%")
		print(f"negative: {self.negative*100}%")



	def fit(self, docs):
		self.docs = docs
		self.set_distinct_words()
		self.set_synonyms_and_antonyms()
		exit()
		self.add_entry_and_exit()
		self.set_word_graph()

		



def main():
	gc.collect()
	args = arguments()

	dataprocessor = DataProcessor(args)
	docs = dataprocessor.fit_transform()

	legi = LEGi(args)
	legi.fit(docs)



if __name__ == '__main__':
	main()

	