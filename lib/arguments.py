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
    This module contains the function to parse the script arguments.
    Constants in the program are initialized in arguments to allow to change them easily.
"""

#####################################################################################################################################################
################################################################### PREPARE STUFF ###################################################################
#####################################################################################################################################################

# External imports
import argparse
import os

#####################################################################################################################################################
##################################################################### FUNCTIONS #####################################################################
#####################################################################################################################################################

def script_args ():

    """
        Function to parse the script arguments.
        In:
            * None.
        Out:
            * The parsed arguments
    """

    # Prepare parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--datasets_path",
                        type=str,
                        help="Path to the dataset",
                        default="./data")
    
    parser.add_argument("--output_directory",
                        type=str,
                        help="Path to the output directory",
                        default="./output")
    
    parser.add_argument("--models_directory",
                        type=str,
                        help="Path to where models are downloaded",
                        default="./models")

    parser.add_argument("--hf_key_path",
                        type=str,
                        help="Path to the Hugging Face token file",
                        default=f"~/hugging_face.key")

    parser.add_argument("--source_separation_models",
                        type=list,
                        help="List of models to use for source separation",
                        default=[("Demucs", "mdx_extra")])
    
    parser.add_argument("--asr_models_emvd",
                        type=list,
                        help="List of models to evaluate on the EMVD dataset",
                        default=["Whisper_Large_V3",
                                 "Whisper_Large_V2",
                                 "Phi_4_Multimodal_Instruct",
                                 "Canary_1B",
                                 "Wav2vec2_Large_960h_Lv60_Self"])

    parser.add_argument("--asr_models_songs",
                        type=list,
                        help="List of models to evaluate on the songs and source-separated datasets",
                        default=["Whisper_Large_V3",
                                 "Whisper_Large_V2",
                                 "Phi_4_Multimodal_Instruct"])

    parser.add_argument("--metrics",
                        type=list,
                        help="Metrics or models used for computing similarity/error",
                        default=["WER",
                                 "BLEU",
                                 "ROUGE",
                                 ("EmbeddingSimilarity", "Gte_Qwen2_1d5B_Instruct"),
                                 ("EmbeddingSimilarity", "All_MiniLM_L6_V2"),
                                 ("EmbeddingSimilarity", "All_MPNet_Base_V2")])

    # Go
    return parser.parse_args()

#####################################################################################################################################################
#####################################################################################################################################################
