import pandas as pd
import random

def run_dodo_sim(df_pool, years=100, max_capacity=15, 
                 intro_invasive=True, invasive_year=20, 
                 invasive_mass=250):
    
    # 1. SETUP - Use Scientific as the key label
    founders = df_pool.sample(min(5, len(df_pool))).to_dict('records')
    for f in founders:
        f['x'], f['y'] = random.uniform(10, 90), random.uniform(10, 90)
        f['status'] = 'Alive'
        f['years_as_ghost'] = 0

    island_population = founders
    stats_history = []
    spatial_history = []
    event_logs = []

    for year in range(1, years + 1):
        # --- A. MOVEMENT & SPATIAL RECORDING ---
        for organism in island_population:
            # Random jitter for movement
            organism['x'] += random.uniform(-4, 4)
            organism['y'] += random.uniform(-4, 4)
            
            # Boundary check (Island is 20-80)
            organism['x'] = max(20, min(80, organism['x']))
            organism['y'] = max(20, min(80, organism['y']))

            # Trophic Logic: Summing all vertebrate diet columns
            meat_score = sum(organism.get(col, 0) for col in ['Diet-Vend', 'Diet-Vect', 'Diet-Vfish', 'Diet-Vunk'])
            
            spatial_history.append({
                'Year': year,
                'Species': organism['Scientific'], 
                'X': organism['x'],
                'Y': organism['y'],
                'Mass': organism['BodyMass-Value'],
                'Status': organism['status'],
                'Diet': 'Ghost' if organism['status'] == 'Ghost' else (
                    'Predator' if meat_score > 40 else 'Prey'
                )
            })

        # --- B. GHOST CLEANUP ---
        # Residents stay as ghosts for 1 frame then vanish
        for organism in island_population[:]:
            if organism['status'] == 'Ghost':
                organism['years_as_ghost'] += 1
                if organism['years_as_ghost'] > 1:
                    island_population.remove(organism)

        # --- C. IMMIGRATION ---
        alive_residents = [s for s in island_population if s['status'] == 'Alive']
        if len(alive_residents) < max_capacity and random.random() < 0.2:
            new_arrival = df_pool.sample(1).to_dict('records')[0]
            new_arrival.update({
                'x': random.choice([0, 100]), 'y': random.uniform(0, 100),
                'status': 'Alive', 'years_as_ghost': 0
            })
            island_population.append(new_arrival)
            event_logs.append(f"🏝️ Year {year}: {new_arrival['Scientific']} colonized the island.")

        # --- D. INVASIVE TRIGGER ---
        if intro_invasive and year == invasive_year:
            rat = {
                'Scientific': 'Rattus rattus (Invasive)',
                'BodyMass-Value': invasive_mass, 'Diet-Vend': 90, 
                'x': 50, 'y': 0, 'status': 'Alive', 'years_as_ghost': 0
            }
            island_population.append(rat)
            event_logs.append(f"🚢 Year {year}: INVASION! Rattus rattus has landed.")

        # --- E. SPATIAL PREDATION ---
        predators = [s for s in island_population if s['status'] == 'Alive' and 
                     sum(s.get(col, 0) for col in ['Diet-Vend', 'Diet-Vect', 'Diet-Vfish']) > 40]
        
        for pred in predators:
            prey_pool = [s for s in island_population if s['status'] == 'Alive' and s['Scientific'] != pred['Scientific']]
            for prey in prey_pool:
                # Spatial check: Must be within 15 units to hunt
                dist = ((pred['x']-prey['x'])**2 + (pred['y']-prey['y'])**2)**0.5
                if pred['BodyMass-Value'] > (prey['BodyMass-Value'] * 1.2) and dist < 15:
                    if random.random() < 0.25:
                        prey['status'] = 'Ghost'
                        event_logs.append(f"💀 Year {year}: {pred['Scientific']} hunted {prey['Scientific']}.")
                        break # Predator is full for this year

# --- F. STATS ---
        # Get only the 'Alive' residents to calculate average mass
        alive_residents = [s for s in island_population if s['status'] == 'Alive']
        
        if alive_residents:
            avg_mass = sum(s['BodyMass-Value'] for s in alive_residents) / len(alive_residents)
        else:
            avg_mass = 0

        stats_history.append({
            'Year': year, 
            'Species_Count': len(alive_residents),
            'Avg_Mass': round(avg_mass, 2) # <--- Add this back!
        })

    return pd.DataFrame(stats_history), event_logs, pd.DataFrame(spatial_history)

    return pd.DataFrame(stats_history), event_logs, pd.DataFrame(spatial_history)