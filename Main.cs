using System;
using System.Collections.Generic;

class Main {
	
	Random random = new Random();

	// model sound structure
	public class Inventory {
		// letters per feature
		Dictionary<string, HashSet<string>> consonants = new Dictionary<string, HashSet<string>>();
		Dictionary<string, HashSet<string>> vowels = new Dictionary<string, HashSet<string>>();

		// feature equivalent to a letter
		Dictionary<string, string[]> features = new Dictionary<string, string[]>();

		// letter equivalent to a feature set
		Dictionary<string, string> letters = new Dictionary<string, string>();

		// group features for "feature matrix" setup
		string[] voicing = new string[] { "voiced", "voiceless" };
		string[] place = new string[] { "bilabial", "labiodental", "dental", "alveolar", "palatal", "velar", "uvular", "pharyngeal", "glottal" };
		string[] manner = new string[] { "nasal", "plosive", "affricate", "fricative", "approximant" };
		string[] height = new string[] { "close", "mid", "open" };
		string[] backness = new string[] { "front", "central", "back" };
		string[] rounding = new string[] { "rounded", "unrounded" };

		public Inventory () {
			// basic consonant feature keys
			string[] cFeatures = this.voicing.Concat(this.place).Concat(this.manner).ToArray();
			foreach (f in cFeatures) {
				this.consonants.Add(f, new HashSet<string>());
			}
			// basic vowel feature keys
			string[] vFeatures = this.height.Concat(this.backness).Concat(this.rounding).ToArray();
			foreach (f in vFeatures) {
				this.vowels.Add(f, new HashSet<string>());
			}
		}

		// make features per letter equivalences available for later
		private void AddFeatures (string letter, string[] features) {
			this.features[letter] = features;
			string featureSet = this.FeatureSet (features);
			this.letters[features] = letter;
		}

		// format single string out of array of three features
		private string FeatureSet (string[] features) {
			string featureSet = String.Format("{0}, {1}, {2}", features[0], features[1], features[2]);
			return featureSet;
		}

		// store vowel letter and features
		public void AddVowel (string letter, string[] features) {
			// make letter accessible through each of its features
			foreach(f in features) {
				this.vowels[f].Add(letter);
			}
			this.AddFeatures(letter, features);
		}

		// store consonant letter and features
		public void AddConsonant (string letter, string[] features) {
			// make letter accessible through each feature
			foreach(f in features) {
				this.consonants[f].Add(letter);
			}
			this.AddFeatures(letter, features);
		}

		// find the letter equivalent to these features
		public string[] GetFeatures (string letter) {
			return this.features[letter];
		}

		// find the features equivalent to this letter
		public string GetLetter (string[] features) {
			string featureSet = this.FeatureSet(features);
			return this.letters[featureSet];
		}

		// return list (set) of all consonants being stored
		public HashSet<string> GetConsonants () {
			HashSet<string> consonants = new HashSet<string>();
			this.consonants.Values.ForEach ( c => consonants.Add(c) );
			return consonants;
		}

		// return list (set) of all vowels being stored
		public HashSet<string> GetVowels () {
			HashSet<string> vowels = new HashSet<string>();
			this.vowels.Values.ForEach ( v => vowels.Add(v) );
			return vowels;
		}
	}


	// model syllable structure as onset, nucleus, coda
	public class Syllable {
		List<string[]> nuclei = new List<string[]>();
		List<string[]> onsets = new List<string[]>();
		List<string[]> codas = new List<string[]>();
		float averageCount;
		float minCount;
		float maxCount;

		public Syllable (int min, int average, int max) {
			this.average = average;
			this.min = min;
			this.max = max;
		}
		// TODO use avg, min, max to roll for word length
		public int HowManySyllables () {
			return this.average;
		}

		public void AddOnset (string[] onset) {
			this.onsets.Add(onset);
		}
		public void AddNucleus (string[] nucleus) {
			this.nuclei.Add(nucleus);
		}
		public void AddCoda (string[] coda) {
			this.codas.Add(coda);
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

	// simple sound & grammar rules to map built syllables to word structure
	public class Rules {
		// additional affixes added to word for properties
		Dictionary<string,List<string>> affixes = new Dictionary<string,List<string>>();
		// sound change kvs of structure 'feature, feature' -> 'feature, feature'
		Dictionary<List<string[]>, List<string[]>> soundChanges = new Dictionary<List<string[]>, List<string[]>>();

		public Rules () {}
		
		public void AddAffix (string property, List<string> affix) {
			affixes[property] = affix;
		}

		// currently handle prefixing or suffixing (only)
		public List<string> AttachAffix (List<string> word, string property) {
			List<string> affix = this.affixes[property];
			// attach as prefix
			if (affix[affix.Count-1] == "-") {
				affix.RemoveAt(affix.Count-1);
				affix.AddRange(word);
			// attach as suffix
			} else {
				affix.RemoveAt(0);
				word.AddRange(affix);
			}
			return word;
		}

		// split csv rule string into array of features
		private string ConvertStringToArray (string csvString) {
			string[] arr = string.Split(",", csvString);
			return arr;
		}

		// split csv rule feature array into string
		private string ConvertArrayToString (string[] arr) {
			string csvString = string.Join(",", arr);
			return csvString;
		}		

		// store "underlying" shape as key and "surface" shape as value
		// e.g. vowel, plosive, vowel -> vowel, fricative, vowel
		public void AddRule (List<string[]> source, List<string[]> target) {
			soundChanges[source] = target;
		}

		// TODO take rule set and output a formatted string
		private List<string> FormatRules () {
			List<string> rulesList = new List<string>();
			string rulesFormatted = "";
			// TODO format each string[] as a string
			foreach (KeyValuePair<List<string[]>,List<string[]>> rule in this.soundChanges) {
				List.Add (String.Format("{0}, {1}", rule.Key, rule.Value));
				rulesFormatted += String.Format("{0} -> {1}\n", rule.Key, rule.Value);
			}
			return rulesFormatted;

			// TODO List keys check for ref not for value so won't be equal 
			if !this.soundChanges.ContainsKey(source) {
				return sources;
			}
			return targets;
		}
	}


	// a language for building and storing words
	public class Language () {
		Inventory inventory;
		Syllable syllable;
		Rules rules;
		string name;
		Dictionary<string, List<string>> words = new Dictionary<string, List<string>>();
		Dictionary<string, string> translations = new Dictionary<string, string>();
		public Inventory { get { return inventory; } set { inventory = value; } }
		public Syllable { get { return syllable; } set { syllable = value; } }
		public Rules { get { return rules; } set { rules = value; } }
		public Name { get; set; }
		public Words { get; set; }

		public Language (Inventory inventory, Syllable syllable, Rules rules) {
			this.inventory = inventory;
			this.syllable = syllable;
			this.rules = rules;
		}

		// dictionary string with each word entry on a newline
		// TODO format sorted A-Z
		public PrintDictionary () {
			string dict;
			foreach (KeyValuePair<string, string> w in this.translations) {
				dict += w.Key + ": " + w.Value + "\n";
			}
			return dict;
		}

		// add a word and translation pair to the language's two-way dictionary
		private AddEntry (List<string> word, string translation) {
			this.words[translation] = word;
			this.translations[string.Join("", word.ToArray())] = translation;
		}

		// overall word building recipe
		public BuildWord (int length, string translation="", string[] affixes=null, bool proper=false) {
			
			// choose syllables and build root word
			List<string> word = this.BuildRoot(length);

			// attach relevant affixes to root
			if (affixes != null) {
				foreach (string property in affixes) {
					word = this.rules.AttachAffix (word, property);
				}
			}

			// format name
			if (proper) {
				word = this.FormatName (word);
			}
			
			// add to the two-way dictionary
			this.AddEntry (word, translation);

			return word;
		}

		// take syllable topography and return a letter
		private string PickSyllableLetter (string letter, HashSet<string> consonants, HashSet<string> vowels) {
			switch (letter) {
				// find a specific vowel
			if (letter == "V") {
				return vowels[random.Next(0, vowels.Count)];
			}
			// find a specific consonant
			else if (letter == "C") {
				return consonants[random.Next(0, consonants.Count)];
			}
			// if just a letter add the letter
			else if (consonants.Contains(letter) || vowels.Contains(letter)) {
				return letter;
			}
			// return letter matching features
			// TODO break this out into a method for Inventory
			else {
				// set up possibilities based on multiple features
				if (letter.IndexOf[","] > -1) {
					string[] features = letter.Split(",")
					HashSet<string> possibleLetters = new HashSet<string>();
				// pick a consonant based on a single feature
				} else if (this.inventory.consonants.ContainsKey(letter)) {
					HashSet<string> possibleLetters = this.inventory.consonants[letter];
					return possibleLetters[random.Next(0, possibleLetters.Count)];
				// pick a vowel based on a single feature
				} else if (this.inventory.vowels.ContainsKey(letter)) {
					HashSet<string> possibleLetters = this.inventory.vowels[letter];
					return possibleLetters[random.Next(0, possibleLetters.Count)];
				}
				// find possibilities based on multiple features
				foreach (string f in features) {
					f = f.Trim();
					// initial feature - add all letters
					if (possibleLetters.Count <= 0) {
						if (this.inventory.vowels.ContainsKey(f)) {
							possibleLetters = this.inventory.vowels[f];
						} else if (this.inventory.consonants.ContainsKey(f)) {
							possibleLetters = this.inventory.consonants[f];
						} else{
							return null;
						}
					// subsequent features - only intersecting letters
					} else if (this.inventory.vowels.ContainsKey(f)) {
						possibleLetters.IntersectWith(this.inventory.vowels[f]);
					} else if (this.inventory.consonants.ContainsKey(f)) {
						possibleLetters.IntersectWith(this.inventory.consonants[f]);
					} else {
						continue;
					}
				}
				// select one of the letters that matches all given features
				return possibleLetters[random.Next(0, possibleLetters.Count)];
			}
		}

		// use syllable structure to construct a single syllable
		private List<string> BuildSyllable (HashSet<string> consonants, HashSet<string> vowels) {
			// pick syllable parts
			string[] newOnset = this.syllable.onsets[random.Next(0, this.syllable.onsets.Count)];
			string[] newNucleus = this.syllable.nuclei[random.Next(0, this.syllable.nuclei.Count)];
			string[] newCoda = this.syllable.codas[random.Next(0, this.syllable.codas.Count)];

			// pick letters for each part
			List<string> newSyllable = new List<string>();
			foreach (string o in newOnset) {
				newSyllable.Add(this.PickSyllableLetter(o, consonants, vowels));
			}
			foreach (string n in newNucleus) {
				newSyllable.Add(this.PickSyllableLetter(n, consonants, vowels));
			}
			foreach (string c in newCoda) {
				newSyllable.Add(this.PickSyllableLetter(c, consonants, vowels));
			}
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
			for (int i=0, i < numSyllables; i++) {
				List<string> newSyllable = this.BuildSyllable(consonants, vowels);
				newRoot.AddRange(newSyllable);
			}
			return newRoot;
		}

		// convert word into a formatted proper name
		private List<string> FormatName (List<string> word) {
			// caps the zeroth character in the zeroth graph/letter
			string firstLetter = word[0][0].ToUpper().ToString().Concat(word[0][1:word[0].Length]);
			word[0] = firstLetter;
			// uncaps the rest of the word
			for (int i=1; i < word.Count; i++) {
				word[i] = word[i].ToLower();
			}
			return word;
		}

		// apply every single rule in the ruleset to a built word
		public List<string> ApplyRules (List<string> word, string syllables) {
			// convert word into list of feature arrays
			// TODO just do this in .ApplyRule for each letter as it's checked
			List<string[]> wordFeatures = new List<string[]>();
			for (int i=0; i < word.Count; i++) {
				string letter = word[i];
				string[] letterFeatures = this.inventory.GetFeatures (thisLetter);
				wordFeatures.Add(letterFeatures);
			}

			// run rules with the word's letters, features and syllables
			List<string> changedWord;
			//changedWord = this.ApplyRule (word, wordFeatures, wordSyllables);

			// go through and apply every rule to the sample word
			foreach (KeyValuePair<List<string[]>,List<string[]>> rule in this.rules.soundChanges) {
				List<string[]> source = rule.Key;
				List<string[]> target = rule.Value;
				changedWord = this.ApplyRule(source, target, word, syllables);
			}
			return changedWord;
		}

		// go through word looking for rule pattern matches
		// TODO document user guidelines for formatting a readable rule
		private List<string[]> ApplyRule (
			List<string[]> sourceRule,
			List<string[]> targetRule,
			List<string> word,
			string wordSyllables)
		{
			// no rule to apply or no word to apply it to
			if (sourceRule.Count == 0 || word.Count == 0) {
				List<string[]> emptyChange = new List<string[]>();
				return emptyChange;
			}

			// track adjacent matches of SOURCE features within WORD letters
			bool isMatch = false;
			int matchCount = 0;

			// store letters to change in word
			List<string> newWord = new List<string>();

			// letters to change in newWord if find adjacent matches
			// e.g. ( {"t", "2"}, {"", "4"}, ) contains one change, one delete
			List<string[]> lettersToModify = new List<string[]>();
			List<string[]> lettersToInsert = new List<string[]>();
			// letter holding tanks while testing full match (then added to above)
			List<string[]> insertionMatches = new List<string[]>();
			List<string[]> modificationMatches = new List<string[]>();

			// iterate through each letter in word hunting for sourcerule
			for (int i=0; i < word.Count; i++) {

				// Keep rule structure in mind and remember rules can nest:
				// 	['V','plosive','V'] -> ['V','fricative','V']
				// 	['V','voiceless,plosive','V'] -> ['V','voiced,fricative','V']
				//
				// Recently changed to this structure:
				//	(['V'], ['voiceless','plosive'], ['V']) -> (['V'], ['voiced','fricative'], ['V'])

				// the current feature set to search for in the word
				featureSet = sourceRule[matchCount];

				// merely check for a consonant or vowel match
				if (featureSet.Length == 1 && (featureSet == ['C'] || featureSet == ['V']) ) {
				 	// report and tally if this is a match
				 	isMatch = wordSyllables[i] == featureSet ? true : isMatch;
				 	matchCount += wordSyllables[i] == featureSet ? 1 : 0;
				}
				// TODO account for CC or VV gemination
				// TODO account for C or V insertion incl metathesis

				// check for specific features and look for changes
				else {
					// does this letter in word match the searched features?
					string[] theseFeatures = this.inventory.features[word[i]];
					string[] thisTarget = targetRule[matchCount];
					int fmatches = true;

					// check features in word and set them to match target features
					foreach (string f in featureSet) {
						// identify target signaling removal "_"
						if (theseFeatures.IndexOf(f) > -1 && thisTarget[0] == '_') {
							string newFeature = "_";
						// identify target features
						} else if (theseFeatures.IndexOf(f) > -1) {
							string newFeature = thisTarget[featureSet.IndexOf(f)];
						// source did not match - rule does not apply
						} else {
							fmatches = false;
							string newFeature = f;
						}
						theseFeatures[theseFeatures.IndexOf(f)] = newFeature;
					}

					// letter match if all features found
					if (fmatches) {
						isMatch = true;
						string newLetter = this.inventory.GetLetter(theseFeatures);
						
						// store new letter in temp list until check rest of rule
						modificationMatches.Add(new[] {newLetter, i});
						insertionMatches.Add(new[] {newLetter, i});
					}
				}

				// rule in the middle of applying does not apply
				if (!isMatch && matchCount > 0) {
					// reset adjacent matches
					matchCount = 0;
				}
				// rule in the middle of applying does fully apply - add new letters
				else if (matchCount >= sourceRule.Length && matchCount > 0) {
					// add letters from temp lists and empty lists for next match
					lettersToModify.AddRange(modificationMatches);
					lettersToInsert.AddRange(insertionMatches);
					modificationMatches.Clear();
					insertionMatches.Clear();
					
					// rewind to just after match start to catch possible overlaps
					i -= matchCount-1;

					// reset adjacent matches
					matchCount = 0;
				}
				// rule did not apply and is not in middle of applying (or fails at word end)
				else {
					continue;
				}
			}

			// change letters at stored indices
			foreach (string[] modification in modificationMatches) {
				int modId = -1;
				if (Int32.TryParse(modification[1], out modId)) {
					word[modId] = modification[0];
				}
			}
			// insert new letters at stored indices ( /!\ expects ascending index!)
			int numInserted = 0;
			foreach (string[] insertion in insertionMatches) {
				int insertId = -1;
				if (Int32.TryParse(insertion[1], out insertId)) {
					word.Insert(insertId+numInserted, insertion[0]);
				}
			}

			// output updated word letters list
			return word;
		}

		//  TODO add support for ranking/ordering rules

	}


	// build names in a language
	public class NameGeneration {

		Language language;

		public NameGeneration () {
			this.language = new Language();
		}

		private string BuildSyllable () {
			// ?- internal rules
			// - build by features
			// - roll for each part
			// - choose parts
			// - KEEP SYLLABLES as SEPARATE LIST
		}
		public string BuildName () {
			// - attach syllables->word
			// 		- keep around word (e.g. gabaa) and syll structure (CVCVV)
			// 		- KEEP SYLLABLES as SEPARATE LIST

			// - word affixes

			// - prepend and append # to word for syllable
			// - word-internal changes
			// - word-edge changes
			// 		- iterate over keys in dict and if they're in syll
			//
		}
	}


	public static void Main(string[] args) {

		Console.WriteLine ("test print");

	}
}