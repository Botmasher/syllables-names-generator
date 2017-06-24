using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class LanguageBuilder : MonoBehaviour {

	// model sound structure
	public class Inventory {

		// TODO methods/properties for accessing inventory info from within dicts

		// letters per feature
		public Dictionary<string, HashSet<string>> lettersByFeature = new Dictionary<string, HashSet<string>>();

		// feature set equivalent to a letter
		public Dictionary<string, string[]> features = new Dictionary<string, string[]>();

		// letter equivalent to a feature set
		public Dictionary<string, string> letters = new Dictionary<string, string>();

		// hashes for looking up just C or V (for building syllables or applying rules)
		public HashSet<string> allConsonants = new HashSet<string>();
		public HashSet<string> allVowels = new HashSet<string>();

		// group features to allow for simple phonological "feature matrix" modeling
		List<string> voicing = new List<string> { "voiced", "voiceless" };
		List<string> place = new List<string> { "bilabial", "labiodental", "dental", "alveolar", "palatal", "velar", "uvular", "pharyngeal", "glottal" };
		List<string> manner = new List<string> { "nasal", "plosive", "affricate", "fricative", "approximant", "lateral" };
		List<string> height = new List<string> { "close", "mid", "open" };
		List<string> backness = new List<string> { "front", "central", "back" };
		List<string> rounding = new List<string> { "rounded", "unrounded" };

		public Inventory () {

			// basic consonant feature keys
			foreach (string f in this.voicing) {
				this.lettersByFeature.Add(f, new HashSet<string>());
			}
			foreach (string f in this.place) {
				this.lettersByFeature.Add(f, new HashSet<string>());
			}
			foreach (string f in this.manner) {
				this.lettersByFeature.Add(f, new HashSet<string>());
			}

			// basic vowel feature keys
			foreach (string f in this.height) {
				this.lettersByFeature.Add(f, new HashSet<string>());
			}
			foreach (string f in this.backness) {
				this.lettersByFeature.Add(f, new HashSet<string>());
			}
			foreach (string f in this.rounding) {
				this.lettersByFeature.Add(f, new HashSet<string>());
			}
		}

		// consonant and vowel feature sets for storage
		private string convertFeaturesToString (string[] featureArray) {
			string featureString = string.Join (",", featureArray);
			return featureString;
		}
		// consonant and vowel feature sets from storage
		private string[] convertFeaturesToArray (string featureString) {
			string[] featureArray = featureString.Split (',');
			return featureArray;
		}

		// does this feature set correspond to any known letter?
		private bool isLetterFetures (string feature0, string feature1, string feature2) {
			string featureSet = string.Format ("{0},{1},{2}", feature0, feature1, feature2);
			return this.letters.ContainsKey(featureSet);
		}
		private bool isLetterFeatures (string[] featureSet) {
			string features = this.convertFeaturesToString (featureSet);
			return this.letters.ContainsKey (features);
		}

		// are these three features actually a feature matrix?
		private bool isFeatureMatrix (string feature0, string feature1, string feature2) {

			// detect a consonant
			if (this.voicing.Contains (feature0) || this.voicing.Contains(feature1) || this.voicing.Contains(feature2)) {
				if (this.manner.Contains (feature0) || this.manner.Contains(feature1) || this.manner.Contains(feature2)) {
					if (this.place.Contains (feature0) || this.place.Contains(feature1) || this.place.Contains(feature2)) {
						return true;
					}
				}
			}
			// detect a vowel
			if (this.rounding.Contains (feature0) || this.rounding.Contains(feature1) || this.rounding.Contains(feature2)) {
				if (this.height.Contains (feature0) || this.height.Contains(feature1) || this.height.Contains(feature2)) {
					if (this.backness.Contains (feature0) || this.backness.Contains(feature1) || this.backness.Contains(feature2)) {
						return true;
					}
				}
			}
			// no such set found
			return false;
		}

		// store a vowel letter and its features
		public bool AddVowel (string letter, string rounding, string height, string backness) {

			// not a recognized consonant or vowel feature matrix
			if (!this.isFeatureMatrix (rounding, height, backness)) {
				return false;
			}

			// make letter accessible through each of its features
			this.lettersByFeature[rounding].Add (letter);
			this.lettersByFeature[height].Add (letter);
			this.lettersByFeature[backness].Add (letter);

			// make features available through letter
			this.features[letter] = new string[] { rounding, height, backness };

			// make letter available through its feature matrix
			this.letters[rounding + "," + height + "," + backness] = letter;

			// add to hash of all vowels for word and syllable building
			this.allVowels.Add (letter);

			return true;
		}

		// store a consonant letter and its features
		public bool AddConsonant (string letter, string voicing, string place, string manner) {

			// not a recognized consonant or vowel feature matrix
			if (!this.isFeatureMatrix (voicing, place, manner)) {
				return false;
			}
			// make letter accessible through each of its features
			this.lettersByFeature[voicing].Add (letter);
			this.lettersByFeature[place].Add (letter);
			this.lettersByFeature[manner].Add (letter);

			// make features available through letter
			this.features[letter] = new string[] { voicing, place, manner };

			// make letter available through its feature matrix
			this.letters[voicing + "," + place + "," + manner] = letter;

			// add to hash of all vowels for word and syllable building
			this.allConsonants.Add (letter);

			return true;
		}

		// find the features equivalent to this letter
		public string[] GetFeatures (string letter) {
			if (this.features.ContainsKey (letter)) {
				return this.features [letter];
			}
			return new string[] {};
		}

		// find the letter equivalent to these features
		public string GetLetter (List<string> features, string nonLetter="") {

			// check for a full feature matrix
			if (features.Count != 3) {
				return nonLetter;
			}

			// format features as string to match key
			string f = string.Format("{0},{1},{2}", features[0], features[1], features[2]);

			// found a letter that has all of these features
			if (this.letters.ContainsKey (f)) {
				return this.letters[f];
			}
			// no letter has all of these features
			return nonLetter;
		}

		// return list (set) of all consonants being stored
		public HashSet<string> GetConsonants () {
			return allConsonants;
		}

		// return list (set) of all vowels being stored
		public HashSet<string> GetVowels () {
			return allVowels;
		}

		// figure out if a string contains a letter, features or a C/V/# syllable marker
		public void Match (string match, string letter, out bool isMatch) {
			// general consonant match
			if (match == "C" && this.allConsonants.Contains (letter)) {
				isMatch = true;
			}
			// general vowel match
			else if (match == "V" && this.allVowels.Contains (letter)) {
				isMatch = true;
			}
			// exact letter match
			else if (match == letter && this.features.ContainsKey(match)) {
				isMatch = true;
			}
			// featureset match or no match at all
			else {
				string[] matchFeatures = match.Split(' ');
				isMatch = true;
				foreach (string f in matchFeatures) {
					isMatch = this.features.ContainsKey(f) ? isMatch : false;
				}
			}
		}
	}


	// model syllable structure as onset, nucleus, coda
	public class Syllable {
		// all possible syllable structures, e.g. C,V,C or C,j,V,V or plosive,V
		public List<List<string>> structures = new List<List<string>>();
		public List<string> symbols = new List<string> {"V", "C", "#", "_"};

		public void AddStructure (List<string> syllableStructure) {
			this.structures.Add (syllableStructure);
		}
	}

	// simple affixes mapping to properties supporting formats prefix- or -suffix
	public class Affixes {
		
		// affixes added to word for properties
		public Dictionary<string,List<string>> affixes = new Dictionary<string,List<string>>();

		public Affixes () {}

		// new property to dictionary
		public void AddAffix (string property, params string[] affix) {
			List<string> affixLetters = new List<string> ();
			foreach (string letter in affix) {
				affixLetters.Add (letter);
			}
			affixes[property] = affixLetters;
		}

		// currently handle prefixing or suffixing (only)
		public List<string> AttachAffix (List<string> word, string property) {
			List<string> affix = this.affixes[property];
			// get rid of boundary "#"
			word.RemoveAt(word.Count-1);
			// attach as prefix
			if (affix[affix.Count-1] == "-") {
				affix.RemoveAt(affix.Count-1);
				affix.AddRange(word);
				word = affix;
				// attach as suffix
			} else {
				affix.RemoveAt(0);
				word.AddRange(affix);
			}
			// add new ending boundary
			word.Add("#");
			Debug.Log ("Added affix to root: " + string.Join("", word.ToArray()));
			return word;
		}
	}

	// simple sound & grammar rules to map built syllables to word structure
	public class Rules {
		// sound change rules { { source, target, environment }, ... }
		public List<List<List<string>>> soundChanges = new List<List<List<string>>>();

		public Rules () {}

		// break rule segment into component features or letters
		private List<string> ConvertStringToList (string s) {
			List<string> splitString = new List<string>();
			splitString.AddRange(s.Split(' '));
			return splitString;
		}	

		// store "underlying" shape as key and "surface" shape as value
		// e.g. vowel, plosive, vowel -> vowel, fricative, vowel
		public void AddRule (string source, string target, string environment) {
			List<string> s = this.ConvertStringToList(source);
			List<string> t = this.ConvertStringToList(target);
			List<string> e = this.ConvertStringToList(environment);
			List<List<string>> newRule = new List<List<string>> {s, t, e};
			soundChanges.Add (newRule);
		}

		// split a rule string into source, target and environment letters/features
		public void SplitRule (List<List<string>> r, out List<string> s, out List<string> t, out List<string> e) {
			s = r[0];
			t = r[1];
			e = r[2];
		}

		public string DisplayRule (List<string> r) {
			string prettyRule = "";
			prettyRule = string.Format ("source: {0}, target: {1}, environment: {2}", r [0], r [1], r [2]);
			return prettyRule;
		}
	}


	// a language for building and storing words
	public class Language {

		// randomizer for building unique words
		System.Random random = new System.Random();

		// two-way word lookup dictionary
		Dictionary<string, List<string>> words = new Dictionary<string, List<string>>();
		Dictionary<string, string> translations = new Dictionary<string, string>();
		// language's native name
		string name;
		public string Name { get; set; }
		// components for building words in the language
		Inventory inventory;
		public Inventory Inventory { get; set; }
		Syllable syllable;
		public Syllable Syllable { get; set; }
		Rules rules;
		public Rules Rules { get; set; }
		Affixes affixes;
		public Affixes Affixes { get; set; }

		public Language (Inventory inventory, Syllable syllable, Rules rules, Affixes affixes) {
			this.inventory = inventory;
			this.syllable = syllable;
			this.rules = rules;
			this.affixes = affixes;
		}

		// dictionary string with each word entry on a newline
		// TODO format sorted A-Z
		public string PrintDictionary () {
			string dict = "";
			foreach (KeyValuePair<string, string> w in this.translations) {
				dict += w.Key + ": " + w.Value + "\n";
			}
			return dict;
		}

		// add a word and translation pair to the language's two-way dictionary
		public void AddEntry (List<string> word, string translation) {
			this.words[translation] = word;
			this.translations[string.Join("", word.ToArray())] = translation;
		}

		// overall word building recipe
		public List<string> BuildWord (int length, bool proper=false, params string[] affixes) {

			// choose syllables and build root word
			List<string> word = this.BuildRoot(length);

			// attach relevant affixes to root
			if (affixes != null) {
				foreach (string property in affixes) {
					word = this.affixes.AttachAffix (word, property);
				}
			}

			this.ApplyRules(word);

			// format name
			if (proper) {
				word = this.FormatName (word);
			}

			return word;
		}

		// take syllable topography and return a letter
		private string PickSyllableLetter (string letter, HashSet<string> consonants, HashSet<string> vowels) {
			// find a specific vowel
			// TODO weighted, Zipf?
			if (letter == "V") {
				string[] vowelsList = vowels.ToArray ();
				return vowelsList [this.random.Next (vowelsList.Length)];
			}
			// find a specific consonant
			// TODO weighted, Zipf?
			else if (letter == "C") {
				string[] consonantsList = consonants.ToArray ();
				return consonantsList [this.random.Next (consonantsList.Length)];
			}
			// add blank letter (empty string) or known letter as-is
			else if (letter == "" || consonants.Contains(letter) || vowels.Contains(letter)) {
				return letter;
			}
			// return letter matching features
			else {
				// set up possibilities based on multiple features
				HashSet<string> possibleLetters = new HashSet<string>();
				string[] features = new string[] {};
				if (letter.IndexOf(",") > -1) {
					features = letter.Split(',');
					// pick a consonant based on a single feature
				} else if (this.inventory.lettersByFeature.ContainsKey(letter)) {
					possibleLetters = this.inventory.lettersByFeature[letter];
					string[] possibleLettersList = possibleLetters.ToArray();
					return possibleLettersList[this.random.Next(0, possibleLetters.Count)];
					// pick a vowel based on a single feature
				} else if (this.inventory.lettersByFeature.ContainsKey(letter)) {
					possibleLetters = this.inventory.lettersByFeature[letter];
					string[] possibleLettersList = possibleLetters.ToArray ();
					return possibleLettersList[this.random.Next(0, possibleLetters.Count)];
				}
				// find possibilities based on multiple features
				foreach (string f in features) {
					string singleFeature = f.Trim();
					// initial feature - add all letters
					if (possibleLetters.Count <= 0) {
						if (this.inventory.lettersByFeature.ContainsKey(singleFeature)) {
							possibleLetters = this.inventory.lettersByFeature[singleFeature];
						} else if (this.inventory.lettersByFeature.ContainsKey(singleFeature)) {
							possibleLetters = this.inventory.lettersByFeature[singleFeature];
						} else{
							return "";
						}
						// subsequent features - only intersecting letters
					} else if (this.inventory.lettersByFeature.ContainsKey(singleFeature)) {
						possibleLetters.IntersectWith(this.inventory.lettersByFeature[singleFeature]);
					} else if (this.inventory.lettersByFeature.ContainsKey(singleFeature)) {
						possibleLetters.IntersectWith(this.inventory.lettersByFeature[singleFeature]);
					} else {
						continue;
					}
				}
				// select one of the letters that matches all given features
				string[] possibleLetterGroup = possibleLetters.ToArray();
				return possibleLetterGroup[this.random.Next(0, possibleLetterGroup.Length)];
			}
		}

		// use syllable structure to construct a single syllable
		private List<string> BuildSyllable (HashSet<string> consonants, HashSet<string> vowels) {
			// pick syllable parts
			List<string> structure = this.syllable.structures[random.Next(this.syllable.structures.Count)];

			// pick letters to replace each syllable piece (e.g. "V" -> "a", "C" -> "t")
			List<string> newSyllable = new List<string>();
			for (int i=0; i < structure.Count; i++) {
				string newLetter = this.PickSyllableLetter(structure[i], consonants, vowels);
				if (newLetter != "" && newLetter != null) {
					newSyllable.Add (newLetter);
				}
			}
			Debug.Log ("Finished building syllable: " + string.Join("", newSyllable.ToArray()));
			return newSyllable;
		}

		// build root with a certain number of syllables
		private List<string> BuildRoot (int numSyllables) {
			// grab inventory letters to fill in C, V symbols
			HashSet<string> consonants = this.inventory.GetConsonants();
			HashSet<string> vowels = this.inventory.GetVowels();

			// TODO add ability to build by features in BuildWord + BuildSyllable

			// create chosen number of syllables and add to word
			List<string> newRoot = new List<string>{"#"};
			for (int i=0; i < numSyllables; i++) {
				List<string> newSyllable = this.BuildSyllable(consonants, vowels);
				newRoot.AddRange(newSyllable);
			}
			newRoot.Add("#");
			Debug.Log ("Finished building root: " + string.Join("", newRoot.ToArray()));
			return newRoot;
		}

		// convert word into a formatted proper name
		private List<string> FormatName (List<string> word) {

			// find the first letter in the word
			int firstNonEmptyString = -1;
			for (int i=0; i < word.Count; i++) {
				if (word[i] != "" && word[i] != null) {
					firstNonEmptyString = i;
					break;
				}
			}
			// no identifiable letters in word - return as-is
			if (firstNonEmptyString == -1) {
				return word;
			}

			// caps the zeroth character in the zeroth graph/letter
			string firstLetter = word[firstNonEmptyString][0].ToString().ToUpper();
			if (word [firstNonEmptyString].Length > 1) {
				firstLetter += word[firstNonEmptyString].Substring(1, word[0].Length);
			}
			// put back the newly capsed letter
			word[firstNonEmptyString] = firstLetter;
			// uncaps the rest of the word
			for (int i=1; i < word.Count; i++) {
				word[i] = word[i].ToLower();
			}
			return word;
		}

		// apply every single rule in the ruleset to a built word
		public List<string> ApplyRules (List<string> word) {

			// prepare to extract source, target and phono environment in each rule
			List<string> source = new List<string> ();
			List<string> target = new List<string> ();
			List<string> environment = new List<string> ();

			// the indexes and the chunks that need rule changes
			Dictionary<int, List<string>> ruledSections = new Dictionary <int, List<string>>();

			// storing subword and indexes to cut and test for source and environment match
			List<string> cutWordSample = new List<string>();
			List<int> possibleIndexMatches = new List<int>();
			int blankIndex = -1;
			int firstIndex = -1;
			int lastIndex = -1;
			// test if environment matches word sample
			bool isMatch = false;
			string newLetter = "";
			List<string> newWord = word.GetRange (0, word.Count);

			// go through and apply every rule to the sample word
			foreach (List<List<string>> rule in this.rules.soundChanges) {

				ruledSections.Clear();

				// fill this rule's sound and environment
				this.rules.SplitRule(rule, out source, out target, out environment);

				// find each section where the rule applies
				possibleIndexMatches = this.FindRuleMatches(word, source);

				// location of the blank space in the environment
				blankIndex = environment.FindIndex(x => x == "_");

				// apply the rule to found sections
				foreach (int possibleIndex in possibleIndexMatches) {

					// list of indices to check should be all but the blank, which is matched src
					firstIndex = possibleIndex - blankIndex;
					lastIndex = possibleIndex + (environment.Count-1 - blankIndex);
					cutWordSample = word.GetRange(firstIndex, lastIndex - firstIndex);

					// test chunked word around index to see if matches the environment
					isMatch = this.FindRuleEnvironments (cutWordSample, environment);

					// build word out of changed sections
					if (isMatch) {
						newLetter = this.ChangeSourceToTarget(word[possibleIndex], source, target);
						newWord[possibleIndex] = newLetter;
						isMatch = false;
					}
				}
			}
			Debug.Log ("Just applied rule and built: "+string.Join("", newWord.ToArray()));
			return newWord;
		}

		// rule apply submethod - find letters in a word matching source sound for environment investigation
		private List<int> FindRuleMatches (List<string> word, List<string> source) {

			// store potential index matches to return
			List<int> possibleIndexes = new List<int>();

			// iterate through word looking for a letter/feature match
			for (int i=0; i < word.Count; i++) {

				// word letter matches source letter
				if (source.Count == 1 && word[i] == source[0]) {
					// store the possible index
					possibleIndexes.Add (i);
				}

				// word letter matches source feature(s)
				else if (this.inventory.lettersByFeature.ContainsKey(source[0])) {
					// store the possible index
					foreach (string s in source) {
						// if this letter does not have this feature
						continue;
					}
					possibleIndexes.Add (i);
				}

				// if this letter is a general syll C/V
				else if (source.Count == 1 && this.syllable.symbols.Contains(source[0])) {
					if (source[0] == "V" && this.inventory.allVowels.Contains(word[i])) {
						possibleIndexes.Add (i);
					} else if (source[0] == "C" && this.inventory.allConsonants.Contains(word[i])) {
						possibleIndexes.Add (i);
					} else {
						continue;
					}
				}

				// otherwise default to non-match
				else {
					// non-matches add nothing
				}
			}

			return possibleIndexes;
		}

		// Check word chunked into environment-length seg against the rule environment
		private bool FindRuleEnvironments (List<string> subWord, List<string> environment) {
			// check for subword/environment parallel matchup
			Debug.Log ("Wordcut length matches environment length: "+ (environment.Count == subWord.Count).ToString() );
			// splitting environment positions (esp for feature matrix; all else assumes length 1)
			string[] e = new string[] {};
			// test for complete match
			bool wordMatches = true;

			// iterate through environment looking for subword matches
			for (int i=0; i < environment.Count; i++) {
				e = environment[i].Split(',');
				// environment position contains nothing
				if (e.Length == 0) {
					continue;
				}
				// environment position is a vowel
				if (e.Length == 1 && e[0] == "V" && this.inventory.allVowels.Contains(subWord[i])) {
					continue;
					// environment position is a consonant
				} else if (e.Length == 1 && e[0] == "C" && this.inventory.allConsonants.Contains(subWord[i])) {
					continue;
					// environment position is one letter or symbol (incl #)
				} else if (e.Length == 1 && e[0] == subWord[i]) {
					continue;
					// environment position is a feature matrix
				} else if (this.inventory.lettersByFeature.ContainsKey(e[0])) {
					foreach (string feature in e) {
						if (!this.inventory.features[subWord[i]].Contains(feature)) {
							wordMatches = false;
						}
					}
					continue;
					// environment position is the blank
				} else if (e.Length == 1 && e[0] == "_") {
					continue;
					// subword does not match environment at this position
				} else {
					wordMatches = false;
				}
			}
			return wordMatches;
		}

		// change a rule-matching letter into the target sound
		private string ChangeSourceToTarget (string letter, List<string> source, List<string> target) {
			// target unidentified
			if (target.Count == 0) {
				return letter;
				// target is a letter or boundary or empty/delete
			} else if (target.Count == 1) {
				if (this.inventory.features.ContainsKey(target[0]) || target[0] == "#" || target[0] == "") {
					return target[0];
				}
				return letter;

			// target is features
			} else {
				List<string> letterFeatures = this.inventory.GetFeatures(letter).ToList();

				// iteration relies on parallel semantic and formal source/target structure
				// e.g. voiced plosive -> voiced fricative BUT NOT voiced plosive -> fricative
				for (int i=0; i < target.Count; i++) {
					// not checking for contains because feature verified in earlier method
					// if (letterFeatures.Contains(target[i])) {}

					// switch out the source feature for the new feature
					letterFeatures [ letterFeatures.IndexOf (source[i]) ] = target[i];
				}
				// get new letter if it exists, otherwise original letter
				return this.inventory.GetLetter(letterFeatures, letter);
			}
		}
		
		// go through word looking for rule pattern matches
		private List<string> ApplyRule (List<string> source, List<string> target, List<string> environment, List<string> word)
		{
			// no word letters to build
			if (word.Count <= 0) {
				return word;
			}

			// rule format e.g. { {"voiceless","plosive"}, {"voiced","plosive"}, {"V", "_", "V"} }

			// find indexes that potentially match the rule source
			List<int> possibleIndices = this.FindRuleMatches (word, source);

			if (possibleIndices.Count < 1) {
				return word;
			}

			// output updated word letters list
			return word;
		}
	}

	public static void Main (string[] args) {

		// build up a very simple vowel inventory
		// make sure features are within simple set in Inventory's place/manner/voicing
		Inventory inventory = new Inventory();
		inventory.AddConsonant("b", "voiced", "bilabial", "plosive");
		inventory.AddConsonant("p", "voiceless", "bilabial", "plosive");
		inventory.AddConsonant("g", "voiced", "velar", "plosive");
		inventory.AddConsonant("k", "voiceless", "velar", "plosive");
		inventory.AddConsonant("d", "voiced", "dental", "plosive");
		inventory.AddConsonant("t", "voiceless", "dental", "plosive");
		inventory.AddConsonant("h", "voiceless", "glottal", "fricative");
		inventory.AddConsonant("l", "voiced", "alveolar", "lateral");
		inventory.AddConsonant("r", "voiced", "alveolar", "approximant");
		inventory.AddConsonant("w", "voiced", "velar", "approximant");
		// build up very simple consonant inventory
		// make sure features are within simple set in Inventory's height/backness/rounding
		inventory.AddVowel("i", "close", "front", "unrounded");
		inventory.AddVowel("a", "open", "central", "unrounded");
		inventory.AddVowel("u", "close", "back", "rounded");

		// recall features using any letter
		Debug.Log (inventory.GetFeatures("b"));

		// This finds "b":
		List<string> testFeaturesList = new List<string> {"voiced", "bilabial", "plosive"};
		inventory.GetLetter(testFeaturesList);
		// This will not find "b":
		testFeaturesList [0] = "bilabial";
		testFeaturesList [1] = "voiced";
		inventory.GetLetter(testFeaturesList);

		Syllable syllableStructure = new Syllable();
		syllableStructure.AddStructure(new List<string> {"C","V"});
		syllableStructure.AddStructure(new List<string> {"C","V","V"});
		syllableStructure.AddStructure(new List<string> {"C","V","C"});
		syllableStructure.AddStructure(new List<string> {"C","V","V","C"});

		Rules rules = new Rules();
		rules.AddRule ("voiced", "voiceless", "_ voiceless");

		Affixes affixes = new Affixes();
		// add prefixes and suffixes
		// trusts you to use only characters found in inventory (matters for rule application)
		affixes.AddAffix("human", "-", "g", "u", "d");
		affixes.AddAffix("nonhuman", "-", "i", "d");
		affixes.AddAffix("strong", "t", "-");
		affixes.AddAffix("small", "l", "-");
		affixes.AddAffix("strange", "g", "-");

		// TODO structure language 
		Language language = new Language(inventory, syllableStructure, rules, affixes);

		// build a long proper noun
		List<string> properNoun = language.BuildWord(3, true, "strong", "nonhuman");
		Debug.Log(string.Join("", properNoun.ToArray()));

		// build a short regular noun
		List<string> justSomeNoun = language.BuildWord(2);

		// add both to the dictionary
		language.AddEntry(properNoun, "Wolf");
		language.AddEntry(justSomeNoun, "food");
		Debug.Log (language.PrintDictionary ());
	}
}