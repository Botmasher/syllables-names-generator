using System;
using System.Collections.Generic;

class Main {
	
	// model syllable structure as onset, nucleus, coda
	public class Syllable {
		List<string> nuclei = new List<string>();
		List<string> onsets = new List<string>();
		List<string> codas = new List<string>();
		public Syllable (List<string> onsets, List<string> nuclei, List<string> codas) {
			this.onsets = onsets;
			this.nuclei = nuclei;
			this.codas = codas;
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

	// build and store a syllable
	public class SyllableGenerator {
		Syllable syllParts;
		public SyllableGenerator (syllable) {
			syllParts = syllable;
		}
		void BuildSyllable () {
			// recipe
			// - rules
			// - features
			// - roll for each part
			// - choose parts
			// - build syllable
			// - clean syllable (assim., etc.)
		}
	}

	public static void Main(string[] args) {
		Console.WriteLine ("test print");
	}
}