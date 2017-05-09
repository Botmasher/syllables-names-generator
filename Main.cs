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

		// store consonant letter and features
		public void AddConsonant (string[] features, string letter) {
			// make letter accessible through each feature
			foreach(f in features) {
				this.consonants[f].Add(letter);
			}

			this.AddFeatures(letter, features);
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
		public void AddVowel (string[] features, string letter) {
			// make letter accessible through each of its features
			foreach(f in features) {
				this.vowels[f].Add(letter);
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
	}


	// basic rule outcomes:
	// 'CVC' : 'CV' => delete last C
	// 'VplosiveV' : 'VfricativeV' => change only medial C
	// '#stV' : '#estV' => insert e- at beginning of word
	// 'VC1C2V' : 'VC1V' => delete second C
	// 'CVC' : 'CVV' => lengthen vowel
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
		Dictionary<string,string> soundChanges = new Dictionary<string,string>();

		public Rules () {
		}
		public void AddAffix (string property, string affix) {
			affixes[property] = affix;
		}
		public void AddRule (string source, string target) {
			soundChanges[source] = target;
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
		}
		public string BuildName () {
			// - attach syllables->word
			// 		- keep around word (e.g. gabaa) and syll structure (CVCVV)
			
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