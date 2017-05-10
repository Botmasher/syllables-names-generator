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
		string[] height = new string[] { "hi", "mid", "low" };
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
		public string[] GetConsonants () {
			List<string> consonants = new List<string>();
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


	// basic rule outcomes:
	// 'CVC' : 'CV' => delete last C
	// 'VplosiveV' : 'VfricativeV' => change only medial C
	// '#stV' : '#estV' => insert e- at beginning of word
	// 'VC1C2V' : 'VC1V' => delete second C
	// 'CVC' : 'CVV' => lengthen vowel
	// * UPDATE use ONLY one representation:
	// 		- just features (instead of syll / feat / letters)
	// 		- OR just letters (can always do feature lookup in Inventory)
	// * NOTES
	//  	- C, V, #, _ reserved for syllables
	// 		- lowercase reserved for letters
	// 		- have to match BOTH symbols and letters
	// 		- also have to match features
	// 		- better: use array? that way can check:
	// 			- if string length > 1 and in inventory cons/vowel dicts == FEATURE
	// 			- if string is C, V, #, _ == SYLL STRUCTURE
	// 			- otherwise if string is lowercase, len > 0 < 4 == LETTER

	// simple sound & grammar rules to map built syllables to word structure
	public class Rules {
		// additional affixes added to word for properties
		Dictionary<string,string> affixes = new Dictionary<string,string>();
		// sound change kvs of structure 'feature, feature' -> 'feature, feature'
		Dictionary<string, string[]> soundChanges = new Dictionary<string, string[]>();

		public Rules () {}
		
		public void AddAffix (string property, string affix) {
			affixes[property] = affix;
		}

		// store "underlying" shape as key and "surface" shape as value
		// 	- e.g. 'vowel, plosive, vowel' -> ['vowel', 'fricative', 'vowel']
		public void AddRule (string source, string target) {
			string[] targets = target.Split(', ');
			soundChanges[source] = targets;
		}

		public bool RuleApplies (string[] sample, string match) {
			List<int> sampleIndicesToChange = new List<int>();
			List<string[]> changeThemToWhat = new List<string[]>(); 
			// does a single rule (already passed in key from the dict) apply?
			// sample is, for conceptual purposes, a word broken into letter arrays
			// (0) check if each letter has feature in rule
			//		(0.1) need to bring along consonant and vowel lists?
			// (1) once get to one that does, store those indices for change
			// (2) also store which of the features needs to be changed
			//		2.1 get by accessing this matched rule key in the dictionary
			// (3) now you can just lookup that feature
			// ** but what about ones that change order like metathesis?
			// 		- may need to enforce structures, like:
			//			-  _ for deletion, so surface never shorter than underlying
			// 			-  array length check, so longer means something added
		}
	}

	// build a new name (modeled as process -ation rather than entity -ator)
	public class NameGeneration {

		Inventory inventory;
		Syllable syllable;
		Rules rules;

		public NameGeneration () {
			this.inventory = new Inventory();
			this.syllable = new Syllable();
			this.rules = new Rules();
		}
		private string BuildSyllable () {
			// ?- internal rules
			// - build by features
			// - roll for each part
			// - choose parts
			// - KEEP SYLLABLES SEPARATED in List
		}
		public string BuildName () {
			// - attach syllables->word
			// 		?- keep around word (e.g. gabaa) and syll structure (CVCVV)
			// 		- KEEP SYLLABLES SEPARATED in List

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