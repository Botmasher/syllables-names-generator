using System;
using System.Collections.Generic;

class Main {
	
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
		List<string> nuclei = new List<string>();
		List<string> onsets = new List<string>();
		List<string> codas = new List<string>();

		public Syllable () {
		}
		public void AddOnset (string onsets) {
			this.onsets.Add(onset);
		}
		public void AddNucleus (string nucleus) {
			this.nuclei.Add(nucleus);
		}
		public void AddCoda (string coda) {
			this.codas.Add(coda);
		}
		// TODO add syllable internal rules (like if you pick this, pick that next)
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
		Dictionary<string,string> affixes = new Dictionary<string,string>();
		// sound change kvs of structure 'feature, feature' -> 'feature, feature'
		Dictionary<List<string[]>, List<string[]>> soundChanges = new Dictionary<List<string[]>, List<string[]>>();

		public Rules () {}
		
		public void AddAffix (string property, string affix) {
			affixes[property] = affix;
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
		List<string> names;
		public Inventory { get { return inventory; } set { inventory = value; } }
		public Syllable { get { return syllable; } set { syllable = value; } }
		public Rules { get { return rules; } set { rules = value; } }
		public Names { get; set; }

		public Language (Inventory inventory, Syllable syllable, Rules rules) {
			this.inventory = inventory;
			this.syllable = syllable;
			this.rules = rules;
		}

		public List<string> ApplyRulesToWord (List<string> word, string syllables) {
			
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
				string[] source = rule.Key;
				string[] target = rule.Value;
				changedWord = this.ApplyRule(source, target, word, syllables);
			}

			// back out in this function, need to turn those back into letters list
			//  	- look up each feature array in inventory and concat letters
			// return the word string[]
		}

		// go through word looking for rule pattern matches
		// TODO document user guidelines for formatting a readable rule
		private List<string[]> ApplyRuleToWord (
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

			// count up SOURCE feature matches found adjacently in WORD features
			int matchCount = 0;
			// store features/letters found and to change in word
			List<string[]> matchList = new List<string[]>();

			// iterate through each letter in word hunting for sourcerule
			for (int i=0; i < word.Count; i++) {

				// move to end to avoid last iter non-coverage (e.g. word-final #)
				if (matchCount >= sourceRule.Length && matchCount > 0) {
					// catch overlapping by setting iter just after start of match
					i -= (matchCount-1);
					// reset adjacent matches
					matchCount = 0;
				}

				// Keep rule structure in mind and remember rules can nest:
				// 	['V','plosive','V'] -> ['V','fricative','V']
				// 	['V','voiceless,plosive','V'] -> ['V','voiced,fricative','V']
				//
				// Recently changed to this structure:
				//	(['V'], ['voiceless','plosive'], ['V']) -> (['V'], ['voiced','fricative'], ['V'])

				// the current feature set to search for in the word
				featureSet = sourceRule[matchCount];

				// merely checking for a consonant or vowel
				if (featureSet.Length == 1 && featureSet == ['C'] || featureSet == ['V']) {
				 	matchCount += wordSyllables[i] == featureSet ? 1 : 0;
					continue;
				}
				// checking for specific features
				else {
					// does this letter in word match the searched features?
					string[] theseFeatures = this.inventory.features[word[i]];
					int matches = 0;
					// tally any found matches so that any pos return means >0 hits
					Array.ForEach(featureSet, f => matches+=theseFeatures.IndexOf(f)+1);
					//foundMatch = false;
					//foreach (string f in featureSet) {
					//	foundMatch = thisLetterFeatures.IndexOf(f) == -1? true: foundMatch;
					//}

					// end pass if no letter features match rule features
					if (matches <= 0) {
						continue;
					}
					matchCount += 1;
					// success! we have at least one rule match
					// - add rulefeature (source or target?) to the found feature set
					// - decide which letter this should be
					// 		- based on change in features from above
					// - use letter to construct new word
					// - it has to understand how the source/target rules differ
				}
			}
			// - then returns word array list with change (updated array)
		}

		//  EXTRA:	add support for ranking/ordering rules
		//  EXTRA: 	handle deletion, insertion and metathesis
		public List<string> ApplyAllRules (
			List<string> sampleLetters,
			List<string[]> sampleFeatures,
			string sampleSyllables)
		{
			
		}
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