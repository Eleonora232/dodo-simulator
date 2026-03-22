import pandas as pd
from pygbif import species as species_api

def get_clean_island_pool(country='MG', taxon_key=212):
    # 1. Load Local Traits (Using your specific filenames)
    # Using 'latin1' to handle special characters in bird names
    df_birds = pd.read_csv('data/BirdFuncDat.txt', sep='\t', encoding='latin1')

    print(f"Fetching species from GBIF for {country}...")
    
    # 2. GBIF Search
    search_results = species_api.name_lookup(
        higherTaxonKey=taxon_key,
        country=country,
        rank='SPECIES',
        limit=100  # Increased limit to get a better pool
    )

    if 'results' not in search_results or not search_results['results']:
        return pd.DataFrame() # Return empty if nothing found

    df_gbif = pd.DataFrame(search_results['results'])
    
    # Cleaning the names
    df_gbif['clean_name'] = df_gbif['scientificName'].apply(lambda x: " ".join(x.split()[:2]))

    # 3. Dynamic Column Selection (Safety Check)
    # We only take columns if they actually exist in this specific GBIF response
    gbif_cols = ['clean_name', 'family', 'genus', 'order', 'species']
    existing_cols = [c for c in gbif_cols if c in df_gbif.columns]
    df1 = df_gbif[existing_cols]

    # 4. Trait Selection (Based on your review)
    trait_cols = [
        'Scientific', 'Diet-Inv', 'Diet-Vect', 'Diet-Vend', 
        'Diet-Vfish', 'Diet-Scav', 'Diet-Fruit', 
        'Diet-Nect', 'Diet-Seed', 'Diet-PlantO', 'BodyMass-Value'
    ]
    # Filter only columns that exist in df_birds to prevent crash
    existing_trait_cols = [c for c in trait_cols if c in df_birds.columns]
    df2 = df_birds[existing_trait_cols]

    # 5. The Join
    df_final = pd.merge(df1, df2, left_on='clean_name', right_on='Scientific', how='inner')
    
    # Remove duplicates (sometimes GBIF returns synonyms)
    df_final = df_final.drop_duplicates(subset=['Scientific'])
    
    print(f"✅ Success! Created pool with {len(df_final)} species.")
    return df_final

# Testing the call
# df_test = get_clean_island_pool('MG', 212)