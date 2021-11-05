# corpus-cast
This repo contains notebooks and data for generating a novel, specifically for [NaNoGenMo 2021](https://github.com/NaNoGenMo/2021/issues). I made these to be as hopefully intuitive/usable as possible for people with a solid beginner-to-intermediate level of comfort with Python. There's lots of description/context in markdown cells, and the functions/steps are, at least from my perspective, well-documented. Please feel free to send questions or suggestions to me!
## data
Folder containing two files that will be used in txt_from_web.ipynb. See that notebook for more information.
## txt_from_web.ipynb
This notebook contains a bunch of ways to get text from the web that you can write out to text files, which you can then use in markov_modeling.ipynb.

The different mini-guides for getting text are:

    1. Corpora from NLTK
        a. Brown corpus
        b. Gutenberg corpus
    2. Social Media
        a. Tweets from a specific user
        b. Transcripts from Youtube
    3. Webpages

## markov_modeling.ipynb
This notebook works pretty differently from txt_from_web.ipynb. The other notebook is meant to get a bunch of text files for you to analyze. In theory, you would go through it, get what you want, and go back to it as-needed for more text. By contrast, this notebook is more interactive, and you're intended to fill certain blocks with your own code to make use of the main object: marky the Markov Model Manager! The functions you can make use of are described in the code blocks, but I'll also have a block with examples of the functions being used, and how you might make use of a Markov Model Manager object.

The main idea is that marky will take the folder you set in section 0 as root, create any missing folders, and allow you to handle file management and markov model building all in one place! You can:

    * import text files and turn them into markov models
    * import markov models from json files
    * create new models and then export them as json files
    * combine models and export the result as a json file
    * create formatted sentence outputs for any model so you can test models and fiddle with settings

(Note: the reason jsons are used here is because you can convert a markovify model to json, save the json, and convert the json back later. Making a model from json is way faster than remaking the model from a string. Get more info on markovify here: https://github.com/jsvine/markovify)