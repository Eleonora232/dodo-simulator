import pandas as pd




class TraitFactory:
    def __init__(self, bird_path, mammal_path, reptile_path):
        # 1. Load Birds (EltonTraits - Tab Separated)
        self.birds = pd.read_csv(bird_path, sep='\t', encoding='latin1')
        
        # 2. Load Mammals (EltonTraits - Tab Separated)
        self.mammals = pd.read_csv(mammal_path, sep='\t', encoding='latin1')
        
        # 3. Load Reptiles (Excel - Specific Sheet and Columns)
        # We specify the columns you mentioned to keep memory usage low
        cols_to_use = [
            'Species', 'Order', 'Suborder', 'Genus', 
            'Family', 'Diet ', 'Diet: comments', 'Maximum body mass (g)'
        ]
        self.reptiles = pd.read_excel(
            reptile_path, 
            sheet_name='Data', 
            usecols=cols_to_use
        )

    def get_organism_data(self, scientific_name):
        """Standardized lookup across all three databases."""
        
        # --- BIRD LOOKUP ---
        bird_match = self.birds[self.birds['Scientific'] == scientific_name]
        if not bird_match.empty:
            row = bird_match.iloc[0]
            return {
                'mass': row['BodyMass-Value'],
                'diet': self._parse_elton_diet(row),
                'taxa': 'bird',
                'family': row['BLFamilyLatin']

            }

        # --- MAMMAL LOOKUP ---
        mam_match = self.mammals[self.mammals['Scientific'] == scientific_name]
        if not mam_match.empty:
            row = mam_match.iloc[0]
            return {
                'mass': row['BodyMass-Value'],
                'diet': self._parse_elton_diet(row),
                'taxa': 'mammal',
                'family': row['MSWFamilyLatin']

            }

        # --- REPTILE LOOKUP ---
        # Note: ReptTraits uses 'Species' column
        rep_match = self.reptiles[self.reptiles['Species'] == scientific_name]
        if not rep_match.empty:
            row = rep_match.iloc[0]
            return {
                'mass': row['Maximum body mass (g)'],
                'diet': self._parse_reptile_diet(row),
                'taxa': 'reptile',
                'family': row['Family']
            }

        return None

    def _parse_elton_diet(self, row):
        """Simplifies Elton's complex 0-100 scores."""
        # Summing vertebrate/invertebrate scores
        meat_score = row['Diet-Vend'] + row['Diet-Vect'] + row['Diet-Vfish'] + row['Diet-Inv']
        return 'carnivore' if meat_score > 50 else 'herbivore'

    def _parse_reptile_diet(self, row):
        """Standardizes ReptTraits 'Diet' column strings."""
        diet_str = str(row['Diet ']).strip().capitalize()
        
        if diet_str == "Carnivorous":
            return "carnivore"
        elif diet_str == "Herbivorous":
            return "herbivore"
        elif diet_str == "Omnivorous":
            return "omnivore"
        else:
            # Handle "NA" or empty values
            return "unknown"