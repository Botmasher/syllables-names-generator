using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

public class LanguageBuilder {

	// model sound structure
	public class Inventory {

		// TODO methods/properties for accessing inventory info from within dicts

		// letters per feature
		public Dictionary<string, HashSet<string>> consonants = new Dictionary<string, HashSet<string>>();
		public Dictionary<string, HashSet<string>> vowels = new Dictionary<string, HashSet<string>>();

		// feature equivalent to a letter
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
				this.consonants.Add(f, new HashSet<string>());
			}
			foreach (string f in this.place) {
				this.consonants.Add(f, new HashSet<string>());
			}
			foreach (string f in this.manner) {
				this.consonants.Add(f, new HashSet<string>());
			}

			// basic vowel feature keys
			foreach (string f in this.height) {
				this.vowels.Add(f, new HashSet<string>());
			}
			foreach (string f in this.backness) {
				this.vowels.Add(f, new HashSet<string>());
			}
			foreach (string f in this.rounding) {
				this.vowels.Add(f, new HashSet<string>());
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
			this.vowels[rounding].Add (letter);
			this.vowels[height].Add (letter);
			this.vowels[backness].Add (letter);

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
			this.consonants[voicing].Add (letter);
			this.consonants[place].Add (letter);
			this.consonants[manner].Add (letter);

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
		public string GetLetter (string feature0, string feature1, string feature2, string nonLetter="") {

			// format features as string to match key
			string features = string.Format("{0},{1},{2}", feature0, feature1, feature2);

			// found a consonant that has all of these features
			if (this.letters.ContainsKey (features)) {
				return this.letters[features];
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
	}


	// model syllable structure as onset, nucleus, coda
	public class Syllable {
		// all possible syllable structures, e.g. C,V,C or C,j,V,V or plosive,V
		public List<List<string>> structures = new List<List<string>>();

		public void HowManySyllables () {}

		public void AddStructure (List<string> syllableStructure) {
			this.structures.Add (syllableStructure);
		}

		// TODO add syll weights (like you have a n% chance of picking this)
		// TODO add syll internal rules (like if you pick this, pick that next)
		// 		OR do similar with a blacklist (e.g. zv, aa, ii, uu, Vh) 

	}


	// BASIC rule outcomes
	// V,plosive,V : V,fricative,V => change medial C
	// C,V,C,C : 
	//
	// EXTRA rule outcomes
	// C,V,C : C,V => delete last C
	// #,s,t,V : #,e,s,t,V => insert e- at beginning of word
	// V,C1,C2,V : V,C1,V => delete second C
	// C,V,C : C,V,V,C => lengthen vowel
	// C,y,V,C : palatal,V,C => palatalize consonant, delete y
	// C,V,nasal,C : C,V˜,C => delete nasal, nasalize vowel
	//
	// * NOTES
	//  - C, V, #, _ reserved for syllables
	// 	- lowercase reserved for letters
	// 	- have to match BOTH symbols and letters
	// 	- also have to match features
	// 	- each word's characters broken into list, so we can check:
	// 		- if string length > 1 and in inventory cons/vowel dicts == FEATURE
	// 		- if string is C, V, #, _ == SYLL STRUCTURE
	// 		- otherwise if string is lowercase, len > 0 < 4 == LETTER

	// simple affixes mapping to properties supporting formats prefix- or -suffix
	public class Affixes {
		
		// TODO methods/properties for accessing dict
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
			Debug.Log ("Added affix to root: " + string.Join("", word.ToArray()));
			return word;
		}
	}

	// simple sound & grammar rules to map built syllables to word structure
	public class Rules {
		// TODO add properties/methods for accessing this dict
		// sound change kvs of structure 'feature, feature' -> 'feature, feature'
		public Dictionary<List<string>, List<string>> soundChanges = new Dictionary<List<string>, List<string>>();

		public Rules () {}

		// split csv rule string into array of features
		private string[] ConvertStringToArray (string csvString) {
			string[] arr = csvString.Split(',');
			return arr;
		}

		// split csv rule feature array into string
		private string ConvertArrayToString (string[] arr) {
			string csvString = String.Join(",", arr);
			return csvString;
		}		

		// store "underlying" shape as key and "surface" shape as value
		// e.g. vowel, plosive, vowel -> vowel, fricative, vowel
		public void AddRule (List<string> source, List<string> target) {
			soundChanges[source] = target;
		}

		// TODO take rule set and output a formatted string
		private void FormatRules () {}
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
				} else if (this.inventory.consonants.ContainsKey(letter)) {
					possibleLetters = this.inventory.consonants[letter];
					string[] possibleLettersList = possibleLetters.ToArray();
					return possibleLettersList[this.random.Next(0, possibleLetters.Count)];
				// pick a vowel based on a single feature
				} else if (this.inventory.vowels.ContainsKey(letter)) {
					possibleLetters = this.inventory.vowels[letter];
					string[] possibleLettersList = possibleLetters.ToArray ();
					return possibleLettersList[this.random.Next(0, possibleLetters.Count)];
				}
				// find possibilities based on multiple features
				foreach (string f in features) {
					string singleFeature = f.Trim();
					// initial feature - add all letters
					if (possibleLetters.Count <= 0) {
						if (this.inventory.vowels.ContainsKey(singleFeature)) {
							possibleLetters = this.inventory.vowels[singleFeature];
						} else if (this.inventory.consonants.ContainsKey(singleFeature)) {
							possibleLetters = this.inventory.consonants[singleFeature];
						} else{
							return "";
						}
						// subsequent features - only intersecting letters
					} else if (this.inventory.vowels.ContainsKey(singleFeature)) {
						possibleLetters.IntersectWith(this.inventory.vowels[singleFeature]);
					} else if (this.inventory.consonants.ContainsKey(singleFeature)) {
						possibleLetters.IntersectWith(this.inventory.consonants[singleFeature]);
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
			List<string> newRoot = new List<string>();
			for (int i=0; i < numSyllables; i++) {
				List<string> newSyllable = this.BuildSyllable(consonants, vowels);
				newRoot.AddRange(newSyllable);
			}
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

			// run rules with the word's letters and features
			List<string> changedWord = word;

			// go through and apply every rule to the sample word
			foreach (KeyValuePair<List<string>,List<string>> rule in this.rules.soundChanges) {
				List<string> source = rule.Key;
				List<string> target = rule.Value;
				changedWord = this.ApplyRule(source, target, changedWord);
			}
			return changedWord;
		}

		// go through word looking for rule pattern matches
		// TODO document user guidelines for formatting a readable rule
			// - list of strings expecting "C", "V", "", letter string or csv feature string
			// - rules that delete go from e.g. "V" -> ""
			// - rules that change features need matching number of features e.g. "voiced,plosive" -> "voiced,fricative" NOT just "fricative" 
		private List<string> ApplyRule (
			List<string> sourceRule,
			List<string> targetRule,
			List<string> word)
		{
			// no rule to apply or no word to apply it to
			if (sourceRule.Count == 0 || word.Count == 0) {
				return word;
			}

			// count matches until a source case is found
			int sourceLength = sourceRule.Count;
			int sourceMatches = 0;

			// keep track of indices that need to be changed
			List<string> newWord = new List<string>();
			Dictionary<int, string> lettersToChange = new Dictionary<int, string>();

			// REDO this looking for
			// format rules as source, target, environment strings (all csv)
				// 		
				// 		if first is # then search only beginning
			 	// 		if last is # then search only end
				// FOR all letters in the word
				// 		IF single sound to change
				// 			add to a list of indices of checkworthy sounds
				// FOR index in that list
				// 		find the one difference marked by "_" in environment (store as index for later)
				//		check the sound's environment
				// 		if all the stuff before it and after it match rule
				//
			for (int i = 0; i < word.Count; i ++) {

				newWord.Add (word [i]);
				
//				Debug.Log ("Applying rule to: "+word[i]+", searching for: "+sourceRule[sourceMatches]);

				// the current rule letter/feature to search for
				string ruleElement = sourceRule [sourceMatches];

				// currently looking for a consonant
				if (ruleElement == "C" && this.inventory.allConsonants.Contains (word [i])) {
					if (targetRule[sourceMatches] == "" || targetRule [sourceMatches] == "_") {
						lettersToChange[i] = "";
					}
					sourceMatches++;
				}

				// currently looking for a vowel
				else if (ruleElement == "V" && this.inventory.allVowels.Contains (word[i])) {
					if (targetRule[sourceMatches] == "" || targetRule [sourceMatches] == "_") {
						lettersToChange[i] = "";
					}
					sourceMatches++;
				}

				// currently looking for a specific letter
				else if (this.inventory.features.ContainsKey (ruleElement) && ruleElement == word[i]) {
					if (targetRule[sourceMatches] == "" || targetRule [sourceMatches] == "_") {
						lettersToChange[i] = "";
					}
					sourceMatches++;
				}

				// empty rule element or some other match
				// TODO break this out, e.g.  "", "a" -> "", "y"
				// TODO account for both source and target are empty
				else if (ruleElement == "_" || ruleElement == "" || ruleElement == word[i]) {
					if (targetRule [sourceMatches] == "" || targetRule [sourceMatches] == "_") {
						lettersToChange[i] = "";
					}
					sourceMatches++;
				}

				// currently looking for a specific feature
				// TODO account for target is letter not features
				// TODO account for target is empty string
				else if (this.inventory.consonants.ContainsKey (ruleElement.Split(',')[0]) || this.inventory.vowels.ContainsKey (ruleElement.Split(',')[0])) {

					// gather and format feature lists to compare letter to rule
					string[] sourceFeatures = sourceRule [sourceMatches].Split (',');
					string[] targetFeatures = targetRule [sourceMatches].Split (',');
					string[] letterFeatures = this.inventory.GetFeatures (word [i]);

					// match test - all rule element features are found in this letter 
					bool isFeatureMismatch = false;
					for (int f = 0; f < sourceFeatures.Length; f++) {

						Debug.Log ("Broke down " + word [i] + " to look for: " + sourceFeatures [f]);

						// test for feature mismatch and abandon letter if so
						if (sourceFeatures[f].Length > 0 && !letterFeatures.Contains (sourceFeatures [f])) {
							Debug.Log ("Did not find target features!");
							isFeatureMismatch = true;
							sourceMatches = 0;
							break;
						}

						Debug.Log ("Changing it to: "+targetFeatures[f]);
						// set this sourcefeature in the letter to match targetfeature instead
						letterFeatures [Array.IndexOf (letterFeatures, sourceFeatures [f])] = targetFeatures [f];
					}

					// found matching feature set
					if (!isFeatureMismatch) {
						sourceMatches ++;
						lettersToChange[i] = this.inventory.GetLetter (letterFeatures[0], letterFeatures[1], letterFeatures[2], word[i]);
					}
				// did not find any matches for the rule
				} else {
					sourceMatches = 0;
				}

				// found a full rule match - alter new word and reset rule search
				if (sourceMatches >= sourceLength) {

					// add applicable target rule letters to the new word
					foreach (KeyValuePair<int, string> newLetter in lettersToChange) {
						newWord [newLetter.Key] = newLetter.Value;
					}
					lettersToChange.Clear ();

					// reset rule match search
					sourceMatches = 0;

					// back up to look for overlapping cases
					i = i-sourceMatches;
				}
			}

			// now we have a full match? if so, let's walk back to that word[i] - matches
				// then we'll try to identify any differences between source and target
				// then we'll log which letters in the original need to be changed
				// finally, we'll make those changes (at the very end?)

			// Keep rule structure in mind and remember rules can nest:
			// 	['V','plosive','V'] -> ['V','fricative','V']
			// 	['V','voiceless,plosive','V'] -> ['V','voiced,fricative','V']
			//
			// Recently changed to this structure:
			//	(['V'], ['voiceless','plosive'], ['V']) -> (['V'], ['voiced','fricative'], ['V'])

			Debug.Log ("Just applied rule to produce: " + string.Join("", newWord.ToArray()));

			// output updated word letters list
			return newWord;
		}

		//  TODO add support for ranking/ordering rules
		// 		e.g. apply intervocalic voicing before fricativization

		// 	TODO support rules with # to detect word beginning/ending
		// 		e.g. allow "attadda" but not "ttadd"

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

		// /!\ ONLY recall letters using correct feature order /!\
		// This finds "b":
		inventory.GetLetter("voiced", "bilabial", "plosive");
		// This will not find "b":
		//inventory.GetLetter("voiced", "plosive", "bilabial"));

		Syllable syllableStructure = new Syllable();
		syllableStructure.AddStructure(new List<string> {"C","V"});
		syllableStructure.AddStructure(new List<string> {"C","V","V"});
		syllableStructure.AddStructure(new List<string> {"C","V","C"});
		syllableStructure.AddStructure(new List<string> {"C","V","V","C"});

		Rules rules = new Rules();
		/*
		 * 	Make sure you have inventory letters for every feature change otherwise you'll replace with empty
		 *  	e.g. voiced -> voiceless will change "r" -> "" if you don't have a voiceless r
		 */
		// assimilate consonant clusters
		rules.AddRule ( new List<string>{"voiced", "voiceless"}, new List<string>{"voiceless", "voiceless"} );
		rules.AddRule ( new List<string>{ "voiceless", "voiced" }, new List<string>{ "voiceless", "voiceless"} );
		// a dash of lenition
		rules.AddRule ( new List<string>{"V", "voiced,plosive", "V"}, new List<string>{"V","voiced, fricative", "V"} );
		// avoid awkward clusters
		rules.AddRule ( new List<string>{"h", "C"}, new List<string>{"","C"} );
		rules.AddRule ( new List<string>{"r", "w"}, new List<string>{"r", "r"} );
		// simplify certain long vowels
		rules.AddRule ( new List<string>{"a", "a"}, new List<string>{"a", ""} );
		rules.AddRule ( new List<string>{"i", "i"}, new List<string>{"i", ""} );
		rules.AddRule ( new List<string>{"u", "u"}, new List<string>{"u", ""} );

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
		//properNoun = language.ApplyRules(properNoun);
		// build a short regular noun
		List<string> justSomeNoun = language.BuildWord(2);
		//justSomeNoun = language.ApplyRules(justSomeNoun);

		// add both to the dictionary
		language.AddEntry(properNoun, "Wolf");
		language.AddEntry(justSomeNoun, "food");
		Debug.Log (language.PrintDictionary ());
	}
}