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
		Dictionary<string, string> soundChanges = new Dictionary<string, string>();

		public Rules () {}
		
		public void AddAffix (string property, string affix) {
			affixes[property] = affix;
		}

		// split csv rule string into array of features
		private string ConvertRuleStringToArray (string csvFeatureString) {
			string[] featureArray = string.Split(",", csvFeatureString);
			return featureArray;
		}

		// split csv rule feature array into string
		private string ConvertRuleArrayToString (string[] featureArray) {
			string csvFeatureString = string.Join(",", featureArray);
			return csvFeatureString;
		}		

		// store "underlying" shape as key and "surface" shape as value
		// e.g. 'vowel,plosive,vowel' -> 'vowel,fricative,vowel'
		public void AddRule (string[] source, string[] target) {
			// format rules and store them
			source = this.ConvertRuleToString(source);
			target = this.ConvertRuleToString(target);
			soundChanges[source] = target;
		}

		// take underlying and return surface as an array
		public string[] GetRule (string source) {
			// not found - just return underlying as surface
			if !this.soundChanges.ContainsKey(source) {
				string[] sources = sources.Split(",");
				return sources;
			}
			// found - format and return surface
			string[] targets = this.ConvertRule(this.soundChanges[source]);
			return targets;
		}

		// go through word looking for rule pattern matches
		public List<string> ApplyRule (
			string[] sourceRule,
			List<string> sampleLetters,
			List<string[]> sampleFeatures,
			string sampleSyllables)
		{
			// 	- does this array in word have my property?
			//	  (e.g. is this letter a vowel?)
			//		- if it's just vowel/consonant, check syllable structure
			//			next_looking_for == 'consonant' && syll[i] == 'C'
			// 		... or check inventory keys?
			// 			this.nventory.consonant.ContainsKey("plosive")
			// 		- if it's a specific property, dig into the list
			// 			sample[i].Contains("plosive")
			// 		- count up the found_count until we find all el in rule
			// 	- if it finds n arrays in a row containing its n rule features
			// 	- then it returns the new target features
			// 		- it has to understand how the source/target rules differ
			// 		- then returns word array list with change (updated array)
		}

		//  EXTRA:	add support for ranking/ordering rules
		//  EXTRA: 	handle deletion, insertion and metathesis
		public List<string> ApplyAllRules (
			List<string> sampleLetters,
			List<string[]> sampleFeatures,
			string sampleSyllables)
		{
			// go through and apply every rule to the sample word
			foreach (KeyValuePair<string,string> change in soundChanges) {
				string[] source = this.ConvertRuleStringToArray(change.Key);
				this.ApplyRule(source, sampleLetters, sampleFeatures, sampleSyllables);
			}
			//	- for each rule, it passes sourcerule and sample to ApplyRule
		}
	}


	// a language for passing  
	public class Language () {

		Inventory inventory;
		Syllable syllable;
		Rules rules;
		public Inventory { get { return inventory; } set { inventory = value; } }
		public Syllable { get { return syllable; } set { syllable = value; } }
		public Rules { get { return rules; } set { rules = value; } }

		public Language (Inventory inventory, Syllable syllable, Rules rules) {
			this.inventory = inventory;
			this.syllable = syllable;
			this.rules = rules;
		}

		// properties used above instead
		//public void SetSyllable (Syllable syllable) {
		//	this.syllable = syllable;
		//}
		//public void SetInventory (Inventory inventory) {
		//	this.inventory = inventory;
		//}
		//public void SetRules (Rules rules) {
		//	this.rules = rules;
		//}

		public List<string> ApplyRules (List<string> sample, string syllableStructure) {
			// convert word into list of feature arrays
			List<string[]> sampleFeatures = new List<string[]>();
			for (int i=0; i < sample.Count; i++) {
				string thisLetter = sample[i];
				string[] letterFeatures = this.inventory.GetFeatures (thisLetter);
				sampleFeatures.Add(letterFeatures);
			}

			// run rules with the word's letters, features and syllables
			List<string> newSample;
			newSample = this.rules.ApplyAllRules(sample, sampleFeatures, syllableStructure);
			
			// back out in this function, need to turn those back into letters list
			//  	- look up each feature array in inventory and concat letters
			// return the word string[]
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