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
    This script performs analyzes on the songs and source-separated datasets.
    It produces figures for each metric, to compare the performance of the ASR models on the datasets, per style.
"""

#####################################################################################################################################################
################################################################### PREPARE STUFF ###################################################################
#####################################################################################################################################################

# External imports
import os
import pickle
import torch
import plotly.express as px
import pandas

# Project imports
from lib.arguments import script_args
import lib.audio
import lib.metrics

#####################################################################################################################################################
######################################################################### GO ########################################################################
#####################################################################################################################################################

# Produce a set of figures per dataset
datasets = [f for f in os.listdir(os.path.join(script_args().datasets_path, "audio")) if f != "emvd"]
for dataset in datasets:

    # Get the list of all files to work on
    all_file_paths = lib.audio.list_from_dataset(dataset)

    # Load metrics from file
    metrics_file_path = os.path.join(script_args().output_directory, "data", "metrics.pt")
    with open(metrics_file_path, "rb") as file:
        all_metrics = pickle.load(file)

    # Build a plot per metric
    for metric_name in script_args().metrics:
        
        # Create dataframe for the figure
        metric = lib.metrics.get_metric(metric_name)
        data = []
        for sub_dataset in all_file_paths:
            style = sub_dataset.split(os.path.sep)[-1]
            for asr_model in script_args().asr_models:
                best_per_song = [metric.best(all_metrics[sub_dataset][file_name][asr_model][lyrics_version][metric_name] for lyrics_version in all_metrics[sub_dataset][file_name][asr_model]) for file_name in all_file_paths[sub_dataset]]
                mean_value = torch.mean(torch.tensor(best_per_song)).item()
                data.append({"Style": style, "Model": asr_model, "Metric": metric_name, "Value": mean_value})
        
        # Build polar figure
        fig = px.line_polar(pandas.DataFrame(data), r="Value", theta="Style", color="Model", line_close=True)
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True)

        # Save figure
        figure_file_path = os.path.join(script_args().output_directory, "figures", f"{dataset} - {metric_name}.png")
        fig.write_image(figure_file_path)
        os.chmod(figure_file_path, 0o777)
    
#####################################################################################################################################################
#####################################################################################################################################################: