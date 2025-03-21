<h2 align="center">CVPR 2025<br>Rethinking Few-Shot Adaptation of Vision-Language Models in Two Stages</h2>

<p align="center">
  <a href="https://scholar.google.com/citations?user=SxQwDD8AAAAJ&authuser=1">Matteo Farina</a>, 
  <a href="https://scholar.google.com/citations?user=bqTPA8kAAAAJ&authuser=1">Massimiliano Mancini</a>, 
  <a href="https://scholar.google.com/citations?user=qSw6YfcAAAAJ&authuser=1">Giovanni Iacca</a> and 
  <a href="https://scholar.google.com/citations?user=xf1T870AAAAJ&authuser=1">Elisa Ricci</a>
</p>

>**Abstract.** *An old-school recipe for training a classifier is to (i) learn a good feature extractor and (ii) optimize a linear layer atop. When only a handful of samples are available per category, as in Few-Shot Adaptation (FSA), data are insufficient to fit a large number of parameters, rendering the above impractical. This is especially true with large pre-trained Vision-Language Models (VLMs), which motivated successful research at the intersection of Parameter-Efficient Fine-tuning (PEFT) and FSA. In this work, we start by analyzing the learning dynamics of PEFT techniques when trained on few-shot data from only a subset of categories, referred to as the “base” classes. We show that such dynamics naturally splits into two distinct phases: (i) task-level feature extraction and (ii) specialization to the available concepts. To accommodate this dynamic, we then depart from prompt- or adapter-based methods and tackle FSA differently. Specifically, given a fixed computational budget, we split it to (i) learn a task-specific feature extractor via PEFT and (ii) train a linear classifier on top. We call this scheme Two-Stage Few-Shot Adaptation (2SFS). Differently from established methods, our scheme enables a novel form of selective inference at a category level, i.e., at test time, only novel categories are embedded by the adapted text encoder, while embeddings of base categories are available within the classifier. Results with fixed hyperparameters across two settings, three backbones, and eleven datasets, show that 2SFS matches or surpasses the state-of-the-art, while established methods degrade significantly across settings.*

### Updates [dd/mm/yy]
- [07/03/25] Code release happening soon! (ETA ~2/3 weeks 😊)
