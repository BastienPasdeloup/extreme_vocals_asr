#####################################################################################################################################################
################################################################### PREPARE STUFF ###################################################################
#####################################################################################################################################################

# External imports
import abc
import evaluate
import sys
from typing import override

# Project imports
from arguments import args
from lib_models import *

#####################################################################################################################################################
##################################################################### FUNCTIONS #####################################################################
#####################################################################################################################################################

def get_metric (metric_class_name, memoize=True):

    # Check if the metric is already in global memory to avoid reloading
    if memoize:
        if "loaded_metrics" not in globals():
            globals()["loaded_metrics"] = {}
        if metric_class_name in globals()["loaded_metrics"]:
            return globals()["loaded_metrics"][metric_class_name]

    # Metric can be passed as a tuple with arguments
    print(f"Loading metric \"{metric_class_name}\"")
    extra_args = []
    if type(metric_class_name) in [list, tuple]:
        metric_class_name, *extra_args = metric_class_name
    
    # Load the metric
    metric_class = getattr(sys.modules[__name__], metric_class_name)
    metric = metric_class(*extra_args)

    # Memoize if needed
    if memoize:
        globals()["loaded_metrics"][metric_class_name] = metric
    return metric

#####################################################################################################################################################
################################################################## ABSTRACT CLASSES #################################################################
#####################################################################################################################################################

class TextMetrics (abc.ABC):



    def __init__ (self, best, *args, **kwargs):
        
        # Inherit from parent class
        super().__init__(*args, **kwargs)

        # Attributes
        self.best = best



    @abc.abstractmethod
    def compute (self, text_1, text_2):

        # Abstract method
        raise NotImplementedError("Should be defined in children classes.")



#####################################################################################################################################################
################################################################### METRIC CLASSES ##################################################################
#####################################################################################################################################################

class WER (TextMetrics):



    def __init__ (self, *args, **kwargs):
        
        # Inherit from parent class
        super().__init__(best=min, *args, **kwargs)

        # Attributes
        self.wer = evaluate.load("wer")



    @override
    def compute (self, text_1, text_2):

        # Compute the error
        error = self.wer.compute(predictions=[text_2], references=[text_1])
        return error



#####################################################################################################################################################

class EmbeddingSimilarity (TextMetrics):



    def __init__ (self, model_name, *args, **kwargs):
        
        # Inherit from parent class
        super().__init__(best=max, *args, **kwargs)

        # Attributes
        self.model = get_model(model_name)



    @override
    def compute (self, text_1, text_2):

        # Compute the embeddings
        embedding_1 = self.model.embed(text_1)
        embedding_2 = self.model.embed(text_2)

        # Compute the similarity
        similarity = float(embedding_1 @ embedding_2 / (embedding_1.norm() * embedding_2.norm()))
        return similarity



#####################################################################################################################################################
#####################################################################################################################################################