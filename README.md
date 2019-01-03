# Language Builder & Believable Word Generator

Define a language, then generate words that fit in the language.

## Description

This tool provides classes and methods for building out a custom language. First, do some building and shaping for your language. Assign features to symbols. Define a basic inventory with phonetic symbols and associated graphemes. Define possile syllable structures, grammatical affixes and sound changes. Then, use your language to generate words, including proper names (the original motivation).

## Background Motivation

I know someone who's working on a game concept and asked me about generating believable names for characters. I've gone through two iterations playing around with the idea since then.

## Getting Started

The code currently exists in two variants - a first take in C# for Unity and a more recent attempt in Python. The Python package is built in `3.6.4`. Here is one way to use it:
- get a copy of this repo
- command line your way to your local copy (the same level as `setup.py`)
- install the package: `pip3 install .`
- run the example: `python3 wordbuilder`

Once you verify it runs, you're probably eager to begin customizing your language. You can start by modifying the demo language in `example.py` or include modules in your own project.

## TODO
Identified tasks for maintenance and improvement:
- [ ] peel this list pff and format it as its own doc
- [ ] go through tasks in py files and organize them in the doc

## Contributing

The current project and any future iterations are for play and in various states of tinkered disrepair. Still, I'm curious to hear if you have any suggestions or updates. If this is your thing, feel happy and free to open an issue or PR once you get going.
