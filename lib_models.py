#####################################################################################################################################################
################################################################### PREPARE STUFF ###################################################################
#####################################################################################################################################################

# External imports
import abc
import os
import sys
from typing import override
import huggingface_hub
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, pipeline
from nemo.collections.asr.models import EncDecMultiTaskModel

# Project imports
from arguments import args

#####################################################################################################################################################
##################################################################### FUNCTIONS #####################################################################
#####################################################################################################################################################

def get_model (model_class_name, memoize=True):

    # Check if the model is already in global memory to avoid reloading
    if memoize:
        memoization_key = model_class_name
        if "loaded_models" not in globals():
            globals()["loaded_models"] = {}
        if memoization_key in globals()["loaded_models"]:
            return globals()["loaded_models"][memoization_key]

    # Load the model
    print(f"Loading model \"{model_class_name}\"", flush=True)
    model_class = getattr(sys.modules[__name__], model_class_name)
    model = model_class()

    # Memoize if needed
    if memoize:
        globals()["loaded_models"][memoization_key] = model
    return model

#####################################################################################################################################################
################################################################## ABSTRACT CLASSES #################################################################
#####################################################################################################################################################

class BaseModel (abc.ABC):



    def __init__ (self, model_id, *args, **kwargs):

        # Inherit from parent class
        super().__init__(*args, **kwargs)

        # Attributes
        self.model_id = model_id

        # Download model if needed
        self._download_model()
    
    

    def _download_model (self):

        # Download the model if not already downloaded
        model_path = os.path.join(args().models_directory, self.model_id)
        if not os.path.exists(model_path):

            # Get model from HuggingFace
            print(f"Downloading model {self.model_id} to {model_path}", file=sys.stderr, flush=True)
            huggingface_hub.login(token=open(args().hf_key, "r").read().strip())
            huggingface_hub.snapshot_download(repo_id=self.model_id, local_dir=model_path)

            # Set permissions for shared use
            os.chmod(model_path, 0o777)



#####################################################################################################################################################

class ASRModel (BaseModel, abc.ABC):



    def __init__ (self, *args, **kwargs):
        
        # Inherit from parent class
        super().__init__(*args, **kwargs)



    @abc.abstractmethod
    def transcribe (self, audio_path):

        # Abstract method
        raise NotImplementedError("Should be defined in children classes.")



#####################################################################################################################################################

class PipelineASRModel (ASRModel, abc.ABC):



    def __init__ (self, *args, **kwargs):
        
        # Inherit from parent class
        super().__init__(*args, **kwargs)

        # Attributes
        self.pipe = pipeline("automatic-speech-recognition", self.model_id)



    @override
    def transcribe (self, audio_path):
        
        # Go through the pipe
        return self.pipe(audio_path, return_timestamps=True, generate_kwargs={"language": "english"})["text"]



#####################################################################################################################################################

class TextEmbeddingModel (BaseModel, abc.ABC):
    


    def __init__ (self, *args, **kwargs):
        
        # Inherit from parent class
        super().__init__(*args, **kwargs)



    @abc.abstractmethod
    def embed (self, text):

        # Abstract method
        raise NotImplementedError("Should be defined in children classes.")



#####################################################################################################################################################

class PipelineTextEmbeddingModel (TextEmbeddingModel, abc.ABC):



    def __init__ (self, *args, **kwargs):
        
        # Inherit from parent class
        super().__init__(*args, **kwargs)

        # Attributes
        self.pipe = pipeline("feature-extraction", self.model_id)



    def embed (self, text):
        
        # Go through the pipe
        return self.pipe(text, return_tensors=True)[0].mean(dim=0)



#####################################################################################################################################################
#################################################################### ASR CLASSES ####################################################################
#####################################################################################################################################################

class Whisper_Large_V2 (PipelineASRModel):



    def __init__ (self, *args, **kwargs):

        # Inherit from parent class
        super().__init__(model_id="openai/whisper-large-v2", *args, **kwargs)



#####################################################################################################################################################

class Whisper_Large_V3 (PipelineASRModel):



    def __init__ (self, *args, **kwargs):

        # Inherit from parent class
        super().__init__(model_id="openai/whisper-large-v3", *args, **kwargs)



#####################################################################################################################################################

class Canary_1B (ASRModel):



    def __init__ (self, *args, **kwargs):

        # Inherit from parent class
        super().__init__(model_id="nvidia/canary-1b", *args, **kwargs)

        # Attributes
        self.model = self._setup()



    def _setup (self):
        
        # https://huggingface.co/nvidia/canary-1b
        # Requires to set NEMO_CACHE_DIR to local directory
        canary_model = EncDecMultiTaskModel.from_pretrained(self.model_id)
        decode_cfg = canary_model.cfg.decoding
        decode_cfg.beam.beam_size = 1
        canary_model.change_decoding_strategy(decode_cfg)
        return canary_model



    @override
    def transcribe (self, audio_path):

        # https://huggingface.co/nvidia/canary-1b
        return self.model.transcribe([audio_path])[0]



#####################################################################################################################################################

class Wav2vec2_Large_960h_Lv60_Self (ASRModel):

    

    def __init__ (self, *args, **kwargs):

        # Inherit from parent class
        super().__init__(model_id="facebook/wav2vec2-large-960h-lv60-self", *args, **kwargs)

        # Attributes
        self.processor, self.model = self._setup()



    def _setup (self):

        # https://huggingface.co/docs/transformers/model_doc/wav2vec2
        processor = Wav2Vec2Processor.from_pretrained(os.path.join(args().models_directory, self.model_id))
        model = Wav2Vec2ForCTC.from_pretrained(os.path.join(args().models_directory, self.model_id))
        return processor, model



    @override
    def transcribe (self, audio_path):

        # https://huggingface.co/docs/transformers/model_doc/wav2vec2
        audio_torch, orig_sr = torchaudio.load(audio_path, format="wav")
        #audio_torch = torchaudio.functional.resample(audio_torch, orig_freq=orig_sr, new_freq=sr)
        input_values = self.processor(audio_torch, return_tensors="pt", padding="longest").input_values.squeeze(0)
        with torch.no_grad():
            logits = self.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        return self.processor.batch_decode(predicted_ids)[0]



#####################################################################################################################################################
############################################################### TEXT EMBEDDING CLASSES ##############################################################
#####################################################################################################################################################

class Gte_Qwen2_1d5B_Instruct (PipelineTextEmbeddingModel):
    
    

    def __init__ (self, *args, **kwargs):

        # Inherit from parent class
        super().__init__(model_id="Alibaba-NLP/gte-Qwen2-1.5B-instruct", *args, **kwargs)



#####################################################################################################################################################

class All_MiniLM_L6_V2 (PipelineTextEmbeddingModel):



    def __init__ (self, *args, **kwargs):

        # Inherit from parent class
        super().__init__(model_id="sentence-transformers/all-MiniLM-L6-v2", *args, **kwargs)



#####################################################################################################################################################

class All_MPNet_Base_V2 (PipelineTextEmbeddingModel):



    def __init__ (self, *args, **kwargs):

        # Inherit from parent class
        super().__init__(model_id="sentence-transformers/all-mpnet-base-v2", *args, **kwargs)



#####################################################################################################################################################
#####################################################################################################################################################