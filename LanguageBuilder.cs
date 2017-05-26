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

		// make features per letter equivalences available for later
		private void AddFeatures (string letter, string[] features) {
			this.features[letter] = features;
			string featureSet = this.FeatureSet (features);
			this.letters[featureSet] = letter;
		}

		// format single string out of array of three features
		private string FeatureSet (string[] features) {
			string featureSet = string.Format("{0}, {1}, {2}", features[0], features[1], features[2]);
			return featureSet;
		}

		// store vowel letter and features
		public void AddVowel (string letter, string[] features) {
			// make letter accessible through each of its features
			foreach(string f in features) {
				this.vowels[f].Add (letter);
				this.allVowels.Add (letter);
			}
			this.AddFeatures(letter, features);
		}

		// store consonant letter and features
		public void AddConsonant (string letter, string[] features) {
			// make letter accessible through each feature
			foreach(string f in features) {
				this.consonants[f].Add (letter);
				this.allConsonants.Add (letter);
			}
			this.AddFeatures(letter, features);
		}

		// find the letter equivalent to these features
		public string[] GetFeatures (string letter) {
			return this.features[letter];
		}

		// find the letter equivalent to these features
		public string GetLetter (string feature0, string feature1, string feature2) {

			// found a consonant that has all of these features
			if (this.consonants.ContainsKey (feature0) && this.consonants.ContainsKey (feature1) && this.consonants.ContainsKey (feature2)) {
				HashSet<string> lettersWithTheseFeatures = this.consonants [feature0];
				Debug.Log (feature0 + ": " + string.Join ("", lettersWithTheseFeatures.ToArray()));
				lettersWithTheseFeatures.IntersectWith (this.consonants [feature1]);
				Debug.Log (feature1 + ": " + string.Join ("", lettersWithTheseFeatures.ToArray()));
				lettersWithTheseFeatures.IntersectWith (this.consonants [feature2]);
				Debug.Log (feature2 + ": " + string.Join ("", lettersWithTheseFeatures.ToArray()));
				return lettersWithTheseFeatures.ToList () [0];
			
			// found a vowel that has all of these features
			} else if (this.vowels.ContainsKey (feature0) && this.vowels.ContainsKey (feature1) && this.vowels.ContainsKey (feature2)) {
				HashSet<string> lettersWithTheseFeatures = this.vowels [feature0];
				lettersWithTheseFeatures.IntersectWith (this.vowels [feature1]);
				lettersWithTheseFeatures.IntersectWith (this.vowels [feature2]);
				return lettersWithTheseFeatures.ToList () [0];
			
			// no letter has all of these features
			} else {
				return "";
			}
		}

		// return list (set) of all consonants being stored
		public HashSet<string> GetConsonants () {
			HashSet<string> consonantSet = new HashSet<string>();
			foreach (HashSet<string> letterSet in this.consonants.Values) {
				consonantSet.UnionWith(letterSet);
			}
			return consonantSet;
		}

		// return list (set) of all vowels being stored
		public HashSet<string> GetVowels () {
			HashSet<string> vowelSet = new HashSet<string>();
			foreach (HashSet<string> letterSet in this.vowels.Values) {
				vowelSet.UnionWith(letterSet);
			}
			return vowelSet;
		}
	}


	// model syllable structure as onset, nucleus, coda
	public class Syllable {
		// TODO methods/properties for accessing syll parts lists
		public List<string[]> nuclei = new List<string[]>();
		public List<string[]> onsets = new List<string[]>();
		public List<string[]> codas = new List<string[]>();

		public Syllable () {}

		// TODO create and use avg, min, max to roll for word length
		public void HowManySyllables () {}

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

	// simple affixes mapping to properties supporting formats prefix- or -suffix
	public class Affixes {
		
		// TODO methods/properties for accessing dict
		// affixes added to word for properties
		public Dictionary<string,List<string>> affixes = new Dictionary<string,List<string>>();

		public Affixes () {}

		// new property to dictionary
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
	}

	// simple sound & grammar rules to map built syllables to word structure
	public class Rules {
		// TODO add properties/methods for accessing this dict
		// sound change kvs of structure 'feature, feature' -> 'feature, feature'
		public Dictionary<List<string[]>, List<string[]>> soundChanges = new Dictionary<List<string[]>, List<string[]>>();

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
		public void AddRule (List<string[]> source, List<string[]> target) {
			soundChanges[source] = target;
		}

		// TODO take rule set and output a formatted string
		private string FormatRules () {
			string rulesFormatted = "";
			// TODO format each string[] as a string
			foreach (KeyValuePair<List<string[]>,List<string[]>> rule in this.soundChanges) {
				rulesFormatted += string.Format("{0} -> {1}\n", rule.Key, rule.Value);
			}
			return rulesFormatted;

			// TODO List keys check for ref not for value so won't be equal 
			//if (!this.soundChanges.ContainsKey(source)) {
			//	return sources;
			//}
			//return targets;
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
		public List<string> BuildWord (int length, bool proper=false, string[] affixes=null) {

			// choose syllables and build root word
			List<string> word = this.BuildRoot(length);

			// attach relevant affixes to root
			if (affixes != null) {
				foreach (string property in affixes) {
					word = this.affixes.AttachAffix (word, property);
				}
			}

			// format name
			if (proper) {
				word = this.FormatName (word);
			}

			this.ApplyRules(word);

			return word;
		}

		// take syllable topography and return a letter
		private string PickSyllableLetter (string letter, HashSet<string> consonants, HashSet<string> vowels) {
			Debug.Log (letter);
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
			// TODO break this out into a method for Inventory
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
				foreach (string s in possibleLetterGroup) {
					Debug.Log (s);
				}
				return possibleLetterGroup[this.random.Next(0, possibleLetterGroup.Length)];
			}
		}

		// use syllable structure to construct a single syllable
		private List<string> BuildSyllable (HashSet<string> consonants, HashSet<string> vowels) {
			// pick syllable parts
			string[] newOnset = this.syllable.onsets[this.random.Next(0, this.syllable.onsets.Count)];
			string[] newNucleus = this.syllable.nuclei[this.random.Next(0, this.syllable.nuclei.Count)];
			string[] newCoda = this.syllable.codas[this.random.Next(0, this.syllable.codas.Count)];

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
			for (int i=0; i < numSyllables; i++) {
				List<string> newSyllable = this.BuildSyllable(consonants, vowels);
				newRoot.AddRange(newSyllable);
			}
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
			
			// convert word into list of feature arrays
			// TODO just do this in .ApplyRule for each letter as it's checked
			List<string[]> wordFeatures = new List<string[]>();
			for (int i=0; i < word.Count; i++) {
				// pass it up if it's not a recognized letter
				if (!this.inventory.features.ContainsKey (word [i])) {
					wordFeatures.Add (new string[] { });
				// it's a known letter so add the features to the word
				} else {
					string[] letterFeatures = this.inventory.GetFeatures (word [i]);
					wordFeatures.Add (letterFeatures);
				}
			}

			// run rules with the word's letters and features
			List<string> changedWord = word;
			//changedWord = this.ApplyRule (word, wordFeatures);

			// go through and apply every rule to the sample word
			foreach (KeyValuePair<List<string[]>,List<string[]>> rule in this.rules.soundChanges) {
				List<string[]> source = rule.Key;
				List<string[]> target = rule.Value;
				changedWord = this.ApplyRule(source, target, changedWord);
			}
			return changedWord;
		}

		// go through word looking for rule pattern matches
		// TODO document user guidelines for formatting a readable rule
		private List<string> ApplyRule (
			List<string[]> sourceRule,
			List<string[]> targetRule,
			List<string> word)
		{
			// no rule to apply or no word to apply it to
			if (sourceRule.Count == 0 || word.Count == 0) {
				return word;
			}

			// track adjacent matches of SOURCE features within WORD letters
			bool isMatch = false;
			int matchCount = 0;

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
				string[] featureSet = sourceRule[matchCount];

				// merely check for a consonant or vowel match
				if (featureSet.Length == 1 && (featureSet [0] == "C")) {
					// report and tally if this is a consonant where consonant expected
					isMatch = this.inventory.allVowels.Contains (word [i]);
					matchCount += Convert.ToInt32 (isMatch);
				} else if (featureSet.Length == 1 && (featureSet [0] == "V")) {
					// report and tally if this is a vowel where vowel expected
					isMatch = this.inventory.allConsonants.Contains (word [i]);
					matchCount += Convert.ToInt32 (isMatch);
				}
				// TODO account for CC or VV gemination
				// TODO account for C or V insertion incl metathesis

				// neither a letter nor a feature matrix
				else if (word[i] == null || word[i] == "") {
					// keep looking for adjacent matches without adding or removing a match
					isMatch = isMatch;
				}
				// unknown letter
				else if (!this.inventory.features.ContainsKey(word[i])) {
					// reset matches
					isMatch = false;
				}
				// check for specific features and look for changes
				else {
					// setup to check that letter in word matches the searched features
					string[] theseFeatures = this.inventory.features[word[i]];
					string[] thisTarget = targetRule[matchCount];
					// does every single feature match?
					bool fmatches = true;

					// check features in word and set them to match target features
					foreach (string f in featureSet) {
						string newFeature = "";
						// letter matches source with target signaling removal "_"
						if (Array.IndexOf(theseFeatures, f) > -1 && thisTarget[0] == "_") {
							newFeature = "_";
							theseFeatures[Array.IndexOf(theseFeatures, f)] = newFeature;
						// letter matches source with target features
						} else if (Array.IndexOf(theseFeatures, f) > -1) {
							newFeature = thisTarget[Array.IndexOf(featureSet, f)];
							theseFeatures[Array.IndexOf(theseFeatures, f)] = newFeature;
						// source did not match - rule does not apply
						} else {
							fmatches = false;
						}
					}

					// letter match if all features found
					if (fmatches) {
						isMatch = true;
						Debug.Log (theseFeatures.Length);
						string newLetter = this.inventory.GetLetter (theseFeatures [0], theseFeatures [1], theseFeatures [2]);

						// store new letter and its index in temp list until check rest of rule
						modificationMatches.Add (new string[] { newLetter, i.ToString () });
						insertionMatches.Add (new string[] { newLetter, i.ToString () });
					} else {
						isMatch = false;
					}
				}

				// rule in the middle of applying does not apply
				if (!isMatch && matchCount > 0) {
					// reset adjacent matches
					matchCount = 0;
				}
				// rule in the middle of applying does fully apply - add new letters
				else if (matchCount >= sourceRule.Count && matchCount > 0) {
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

			if (modificationMatches.Count == 0 && insertionMatches.Count == 0) {
				return word;
			}
			// change letters at stored indices
			foreach (string[] modification in modificationMatches) {
				int modId = -1;
				if (Int32.TryParse(modification[1], out modId)) {
					word[modId] = modification[0];
				}
			}

			if (insertionMatches.Count == 0) {
				return word;
			}
			// insert new letters at stored indices ( /!\ expects ascending index!)
			int numInserted = 0;
			foreach (string[] insertion in insertionMatches) {
				int insertId = -1;
				if (Int32.TryParse(insertion[1], out insertId)) {
					numInserted += 1;
					word.Insert(insertId+numInserted, insertion[0]);
				}
			}

			// output updated word letters list
			return word;
		}

		//  TODO add support for ranking/ordering rules

	}

	public static void Main(string[] args) {

		// build up a very simple vowel inventory
		// make sure features are within simple set in Inventory's place/manner/voicing
		Inventory inventory = new Inventory();
		inventory.AddConsonant("b", new string[]{"voiced", "bilabial", "plosive"});
		inventory.AddConsonant("p", new string[]{"voiceless", "bilabial", "plosive"});
		inventory.AddConsonant("g", new string[]{"voiced", "velar", "plosive"});
		inventory.AddConsonant("k", new string[]{"voiceless", "velar", "plosive"});
		inventory.AddConsonant("d", new string[]{"voiced", "dental", "plosive"});
		inventory.AddConsonant("t", new string[]{"voiceless", "dental", "plosive"});
		inventory.AddConsonant("h", new string[]{"voiceless", "glottal", "fricative"});
		inventory.AddConsonant("l", new string[]{"voiced", "alveolar", "lateral"});
		inventory.AddConsonant("r", new string[]{"voiced", "alveolar", "approximant"});
		inventory.AddConsonant("w", new string[]{"voiced", "velar", "approximant"});
		// build up very simple consonant inventory
		// make sure features are within simple set in Inventory's height/backness/rounding
		inventory.AddVowel("i", new string[]{"close", "front", "unrounded"});
		inventory.AddVowel("a", new string[]{"open", "central", "unrounded"});
		inventory.AddVowel("u", new string[]{"close", "back", "rounded"});

		// recall letters using same feature order, so this finds "b":
		inventory.GetLetter("voiced", "bilabial", "plosive");
		// this does not find "b":
		Debug.Log (inventory.GetLetter("voiced", "plosive", "bilabial"));

		Syllable syllableStructure = new Syllable();
		syllableStructure.AddOnset(new string[] {"C"});
		syllableStructure.AddOnset(new string[] {""});
		syllableStructure.AddNucleus(new string[] {"V"});
		syllableStructure.AddNucleus(new string[] {"V", "V"});
		syllableStructure.AddCoda(new string[] {"C"});
		syllableStructure.AddCoda(new string[] {""});

		Rules rules = new Rules();
		// assimilate consonant clusters
		rules.AddRule(new List<string[]>{
			new string[] {"voiced"},
			new string[] {"voiceless"} }, new List<string[]>{
			new string[] {"voiceless"},
			new string[] {"voiceless"}
		});
		rules.AddRule(new List<string[]>{
			new string[] {"voiceless"},
			new string[] {"voiced"} }, new List<string[]>{
			new string[] {"voiceless"},
			new string[] {"voiceless"}
		});
		// a dash of lenition
		rules.AddRule(new List<string[]>{
			new string[] {"V"},
			new string[] {"voiced", "plosive"},
			new string[] {"V"} }, new List<string[]>{
			new string[] {"V"},
			new string[] {"voiced", "fricative"},
			new string[] {"V"}
		});
		// avoid awkward clusters
		rules.AddRule(new List<string[]>{
			new string[] {"h"},
			new string[] {"C"} }, new List<string[]> {
			new string[] {""},
			new string[] {"C"}
		});
		rules.AddRule(new List<string[]>{
			new string[] {"r"},
			new string[] {"w"} }, new List<string[]> {
			new string[] {"r"},
			new string[] {"r"}
		});
		// simplify long vowels
		rules.AddRule(new List<string[]>{
			new string[] {"a"},
			new string[] {"a"} }, new List<string[]> {
			new string[] {"a"},
			new string[] {""}
		});
		rules.AddRule(new List<string[]>{
			new string[] {"i"},
			new string[] {"i"} }, new List<string[]> {
			new string[] {"i"},
			new string[] {""}
		});
		rules.AddRule(new List<string[]>{
			new string[] {"u"},
			new string[] {"u"} }, new List<string[]> {
			new string[] {"u"},
			new string[] {""}
		});

		Affixes affixes = new Affixes();
		// add prefixes and suffixes
		// trusts you to use only characters found in inventory (matters for rule application)
		affixes.AddAffix("human", new List<string>{"-", "g", "u", "d"});
		affixes.AddAffix("nonhuman", new List<string>{"-", "i", "d"});
		affixes.AddAffix("strong", new List<string>{"t", "-"});
		affixes.AddAffix("small", new List<string>{"l", "-"});
		affixes.AddAffix("strange", new List<string>{"g", "-"});

		// TODO structure language 
		Language language = new Language(inventory, syllableStructure, rules, affixes);

		// build a long proper noun
		List<string> properNoun = language.BuildWord(3, true, new string[]{"nonhuman", "strong"});
		properNoun = language.ApplyRules(properNoun);
		// build a short regular noun
		List<string> justSomeNoun = language.BuildWord(2);
		justSomeNoun = language.ApplyRules(justSomeNoun);

		// add both to the dictionary
		language.AddEntry(properNoun, "Wolf");
		language.AddEntry(justSomeNoun, "food");
		Debug.Log (properNoun);
	}
}