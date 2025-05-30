#####################################################################################################################################################
###################################################################### LICENSE ######################################################################
#####################################################################################################################################################
#
#    Copyright (C) 2025  Bastien Pasdeloup & Axel Marmoret
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#####################################################################################################################################################
################################################################### DOCUMENTATION ###################################################################
#####################################################################################################################################################

"""
    This module contains classes to perform automatic speech recognition.
    Models should be loaded using the "get_model" function from "lib.models.loader".
"""

#####################################################################################################################################################
################################################################### PREPARE STUFF ###################################################################
#####################################################################################################################################################

# External imports
import os
from typing import *
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, AutoModelForCausalLM, AutoProcessor, GenerationConfig, pipeline
from nemo.collections.asr.models import EncDecMultiTaskModel
import logging
import sys

# Project imports
from lib.arguments import script_args
import lib.models.base
import lib.audio

#####################################################################################################################################################
###################################################################### CLASSES ######################################################################
#####################################################################################################################################################

class Whisper_Large_V2 (lib.models.base.HuggingFaceModel):

    """
        Class to perform automatic speech recognition using the Whisper Large V2 model.
    """

    #############################################################################################################################################

    def __init__ ( self,
                   *args:    Optional[list[any]],
                   **kwargs: Optional[dict[any, any]]
                 ) ->        None:

        """
            Constructor for the class.
            In:
                * args:   Extra arguments.
                * kwargs: Extra keyword arguments.
            Out:
                * A new instance of the class.
        """

        # Inherit from parent class
        super().__init__(model_id="openai/whisper-large-v2", *args, **kwargs)

        # Attributes
        self.pipe = None

    #############################################################################################################################################

    @override
    def _setup ( self,
               ) -> None:
        
        """
            Method to setup the model.
            In:
                * None.
            Out:
                * None.
        """

        # Use a pipeline
        self.pipe = pipeline("automatic-speech-recognition", self.model_id)

    #############################################################################################################################################

    @override
    def _apply ( self,
                 audio_path: str,
                 language:   Optional[str] = "english",
               ) ->          str:

        """
            Method to apply the model to some data.
            In:
                * audio_path: The path to the audio file.
                * language:   The language of the audio.
            Out:
                * The text transcription of the audio.
        """
        
        # Go through the pipe
        return self.pipe(audio_path, return_timestamps=True, generate_kwargs={"language": language})["text"]

    #############################################################################################################################################
    #############################################################################################################################################

#####################################################################################################################################################

class Whisper_Large_V3 (lib.models.base.HuggingFaceModel):

    """
        Class to perform automatic speech recognition using the Whisper Large V3 model.
    """

    #############################################################################################################################################

    def __init__ ( self,
                   *args:    Optional[list[any]],
                   **kwargs: Optional[dict[any, any]]
                 ) ->        None:

        """
            Constructor for the class.
            In:
                * args:   Extra arguments.
                * kwargs: Extra keyword arguments.
            Out:
                * A new instance of the class.
        """

        # Inherit from parent class
        super().__init__(model_id="openai/whisper-large-v3", *args, **kwargs)

        # Attributes
        self.pipe = None

    #############################################################################################################################################

    @override
    def _setup ( self,
               ) -> None:
        
        """
            Method to setup the model.
            In:
                * None.
            Out:
                * None.
        """

        # Use a pipeline
        self.pipe = pipeline("automatic-speech-recognition", self.model_id)

    #############################################################################################################################################

    @override
    def _apply ( self,
                 audio_path: str,
                 language:   Optional[str] = "english",
               ) ->          str:

        """
            Method to apply the model to some data.
            In:
                * audio_path: The path to the audio file.
                * language:   The language of the audio.
            Out:
                * The text transcription of the audio.
        """
        
        # Go through the pipe
        return self.pipe(audio_path, return_timestamps=True, generate_kwargs={"language": language})["text"]

    #############################################################################################################################################
    #############################################################################################################################################

#####################################################################################################################################################

class Canary_1B (lib.models.base.NvidiaNemoModel):

    """
        Class to perform automatic speech recognition using the Canary 1B model.
    """

    #############################################################################################################################################

    def __init__ ( self,
                   *args:    Optional[list[any]],
                   **kwargs: Optional[dict[any, any]]
                 ) ->        None:

        """
            Constructor for the class.
            In:
                * args:   Extra arguments.
                * kwargs: Extra keyword arguments.
            Out:
                * A new instance of the class.
        """

        # Inherit from parent class
        super().__init__(model_id="nvidia/canary-1b", *args, **kwargs)

        # Attributes
        self.model = None

    #############################################################################################################################################

    def _setup ( self,
               ) -> None:
        
        """
            Method to setup the model.
            In:
                * None.
            Out:
                * None.
        """
        
        # Disable logging
        logging.getLogger('nemo_logger').setLevel(logging.ERROR)

        # https://huggingface.co/nvidia/canary-1b
        self.model = EncDecMultiTaskModel.from_pretrained(self.model_id)
        decode_cfg = self.model.cfg.decoding
        decode_cfg.beam.beam_size = 1
        self.model.change_decoding_strategy(decode_cfg)

    #############################################################################################################################################

    @override
    def _apply ( self,
                 audio_path: str,
                 language:   Optional[str] = "en",
               ) ->          str:

        """
            Method to apply the model to some data.
            In:
                * audio_path: The path to the audio file.
                * language:   The language of the audio.
            Out:
                * The text transcription of the audio.
        """

        # Needs data to be mono and resampled at 16kHz
        audio, sampling_rate = lib.audio.load_audio(audio_path, 16000, True)

        # Transcribe
        return self.model.transcribe(audio.squeeze(0), source_lang=language, target_lang=language, task="asr", pnc="no")[0].text

    #############################################################################################################################################
    #############################################################################################################################################

#####################################################################################################################################################

class Wav2vec2_Large_960h_Lv60_Self (lib.models.base.HuggingFaceModel):

    """
        Class to perform automatic speech recognition using the Wav2Vec2 Large 960h Lv60 Self model.
    """

    #############################################################################################################################################

    def __init__ ( self,
                   *args:    Optional[list[any]],
                   **kwargs: Optional[dict[any, any]]
                 ) ->        None:

        """
            Constructor for the class.
            In:
                * args:   Extra arguments.
                * kwargs: Extra keyword arguments.
            Out:
                * A new instance of the class.
        """

        # Inherit from parent class
        super().__init__(model_id="facebook/wav2vec2-large-960h-lv60-self", *args, **kwargs)

        # Attributes
        self.processor = None
        self.model = None

    #############################################################################################################################################

    @override
    def _setup ( self,
               ) -> None:
        
        """
            Method to setup the model.
            In:
                * None.
            Out:
                * None.
        """
        
        # https://huggingface.co/docs/transformers/model_doc/wav2vec2
        self.processor = Wav2Vec2Processor.from_pretrained(os.path.join(script_args().models_directory, self.model_id))
        self.model = Wav2Vec2ForCTC.from_pretrained(os.path.join(script_args().models_directory, self.model_id))

    #############################################################################################################################################

    @override
    def _apply ( self,
                 audio_path: str,
               ) ->          str:

        """
            Method to apply the model to some data.
            In:
                * audio_path: The path to the audio file.
            Out:
                * The text transcription of the audio.
        """

        # Needs data to be mono and resampled at 16kHz
        audio, sampling_rate = lib.audio.load_audio(audio_path, 16000, True)

        # Transcribe
        input_values = self.processor(audio, return_tensors="pt", padding="longest", sampling_rate=sampling_rate).input_values.squeeze(0)
        with torch.no_grad():
            logits = self.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        return self.processor.batch_decode(predicted_ids)[0]

    #############################################################################################################################################
    #############################################################################################################################################

#####################################################################################################################################################

class Phi_4_Multimodal_Instruct (lib.models.base.HuggingFaceModel):

    """
        Class to perform automatic speech recognition using the Phi 4 Multimodal Instruct model.
    """

    #############################################################################################################################################

    def __init__ ( self,
                   *args:    Optional[list[any]],
                   **kwargs: Optional[dict[any, any]]
                 ) ->        None:

        """
            Constructor for the class.
            In:
                * args:   Extra arguments.
                * kwargs: Extra keyword arguments.
            Out:
                * A new instance of the class.
        """

        # Inherit from parent class
        super().__init__(model_id="microsoft/Phi-4-multimodal-instruct", *args, **kwargs)

        # Attributes
        self.processor = None
        self.model = None
        self.config = None

    #############################################################################################################################################

    @override
    def _setup ( self,
               ) -> None:
        
        """
            Method to setup the model.
            In:
                * None.
            Out:
                * None.
        """
        
        # Use flash attention if available
        attn = None
        try:
            import flash_attn
            attn = "flash_attention_2"
            print("Using flash attention.", file=sys.stderr, flush=True)
        except ImportError:
            print("Flash attention not available, using default attention implementation.", file=sys.stderr, flush=True)

        # https://huggingface.co/microsoft/Phi-4-multimodal-instruct
        self.processor = AutoProcessor.from_pretrained(os.path.join(script_args().models_directory, self.model_id), trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(os.path.join(script_args().models_directory, self.model_id), device_map="cuda", torch_dtype="auto", trust_remote_code=True, _attn_implementation=attn).cuda()
        self.config = GenerationConfig.from_pretrained(os.path.join(script_args().models_directory, self.model_id))

    #############################################################################################################################################

    @override
    def _apply ( self,
                 audio_path: str,
               ) ->          str:

        """
            Method to apply the model to some data.
            In:
                * audio_path: The path to the audio file.
            Out:
                * The text transcription of the audio.
        """

        # Load audio
        audio, sampling_rate = lib.audio.load_audio(audio_path, engine="soundfile")

        # Define prompt
        user_prompt = "<|user|>"
        assistant_prompt = "<|assistant|>"
        prompt_suffix = "<|end|>"
        asr_prompt = "Transcribe the lyrics in the audio to text. Do not write anything else."
        prompt = f"{user_prompt}<|audio_1|>{asr_prompt}{prompt_suffix}{assistant_prompt}"

        # Transcribe
        inputs = self.processor(text=prompt, audios=[(audio, sampling_rate)], return_tensors="pt").to("cuda:0")
        generate_ids = self.model.generate(**inputs, max_new_tokens=1000, generation_config=self.config)
        generate_ids = generate_ids[:, inputs["input_ids"].shape[1]:]
        return self.processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

    #############################################################################################################################################
    #############################################################################################################################################

#####################################################################################################################################################
#####################################################################################################################################################