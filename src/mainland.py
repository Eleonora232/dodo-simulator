import requests
import time
import numpy as np

class Mainland:
    def __init__(self, country_code, factory):
        self.country_code = country_code.upper()
        self.factory = factory
        self.taxa_keys = [212, 359, 11592253, 11418114]
        # Use a Session for 5x faster repeated requests
        self.session = requests.Session() 
        
        self.species_pool = self._fetch_all_taxa_fast()
        self._calculate_weights()

    def _fetch_all_taxa_fast(self):
        """Uses Facets + Session-based lookups for maximum speed."""
        final_pool = []
        
        for taxa_key in self.taxa_keys:
            group_name = self._infer_group(taxa_key)
            print(f"Fetching {group_name} summary for {self.country_code}...")

            # 1. Get the Species Keys and Counts in ONE request
            url = "https://api.gbif.org/v1/occurrence/search"
            params = {
                'taxonKey': taxa_key,
                'country': self.country_code,
                'facet': 'speciesKey',
                'facetLimit': 1000, 
                'limit': 0
            }
            
            resp = self.session.get(url, params=params).json()
            species_counts = resp.get('facets', [{}])[0].get('counts', [])
            
            print(f"Found {len(species_counts)} candidate species. Matching names & traits...")

            # 2. Match names and traits
            for item in species_counts:
                s_key = item.get('name')   # The ID
                count = item.get('count')  # The Occurrence count
                
                # Fast lookup for the scientific name
                name_resp = self.session.get(f"https://api.gbif.org/v1/species/{s_key}").json()
                sci_name = name_resp.get('species')
                
                if sci_name:
                    traits = self.factory.get_organism_data(sci_name)
                    if traits:
                        traits['name'] = sci_name
                        traits['abundance'] = count
                        traits['group'] = group_name
                        final_pool.append(traits)
            
            # Small breather between taxonomic groups
            time.sleep(0.1)

        print(f"Initialization Complete: {len(final_pool)} species matched traits.")
        return final_pool

    def _infer_group(self, key):
        if key == 212: return 'bird'
        if key == 359: return 'mammal'
        return 'reptile'
    

    def _calculate_weights(self):
            """Calculates Preston's Log-Normal Migration Weights."""
            if not self.species_pool:
                return
            
            # 1. Get abundances
            counts = np.array([s.get('abundance', 1) for s in self.species_pool])
            
            # 2. log2 transformation (Preston's Octaves)
            log_weights = np.log2(counts + 1)
            
            # 3. Normalize to sum to 1.0
            probabilities = log_weights / np.sum(log_weights)
            
            # 4. IMPORTANT: Write it back to the species objects
            for i, species in enumerate(self.species_pool):
                species['migration_prob'] = probabilities[i]