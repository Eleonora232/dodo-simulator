import streamlit as st
import pandas as pd
import plotly.express as px
from src.engine import run_dodo_sim 
from src.data_fetcher import get_clean_island_pool

st.set_page_config(page_title="The Dodo Simulator", layout="wide")

st.title("🏝️ The Dodo Simulator")
st.markdown("Explore how isolation and invasive species shape island evolution.")

# --- SIDEBAR CONTROLS ---

st.sidebar.header("Simulation Parameters")

years = st.sidebar.slider("Simulation Duration (Years)", 10, 200, 100)
capacity = st.sidebar.slider("Island Carrying Capacity (K)", 5, 50, 20)

st.sidebar.divider()
st.sidebar.subheader("Invasive Species Event")
intro_invasive = st.sidebar.checkbox("Introduce Invasive Predator?", value=True)
inv_year = st.sidebar.slider("Year of Introduction", 1, years, 40, disabled=not intro_invasive)
inv_mass = st.sidebar.number_input("Predator Mass (g)", 50, 5000, 300, step=50)

# --- RUN SIMULATION ---
# For now, we'll assume df_final is loaded or cached
# df_final = pd.read_csv('data/final_pool.csv') 
df_final = get_clean_island_pool(country="MG", taxon_key=212)

if st.button("🚀 Run Simulation"):
    with st.spinner("Simulating..."):
        # Unpack both the dataframe and the logs
        results, logs, spatial_df = run_dodo_sim(
            df_final, 
            years=years, 
            max_capacity=capacity,
            intro_invasive=intro_invasive, 
            invasive_year=inv_year,
            invasive_mass=inv_mass
        )

    # --- TOP CHARTS ---
    # (Your Plotly code from before goes here)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Biodiversity Over Time")
        fig_count = px.line(results, x='Year', y='Species_Count', 
                            title="Number of Species on Island",
                            line_shape="spline", color_discrete_sequence=["#2ecc71"])
        st.plotly_chart(fig_count, use_container_width=True)

    with col2:
        st.subheader("Evolutionary Drift (Body Mass)")
        fig_mass = px.line(results, x='Year', y='Avg_Mass', 
                           title="Average Body Mass (Gigantism Check)",
                           line_shape="spline", color_discrete_sequence=["#e74c3c"])
        st.plotly_chart(fig_mass, use_container_width=True)

    st.subheader("🏝️ Interactive Island Ecosystem")
# --- NEW: SEEDING THE DATA ---
# We create 3 fake rows for Year 1 to force the legend to show all categories
    seed_rows = pd.DataFrame([
        {'Year': 1, 'Diet': 'Prey', 'X': -100, 'Y': -100, 'Mass': 1, 'Status': 'Alive', 'Species': 'Seed'},
        {'Year': 1, 'Diet': 'Predator', 'X': -100, 'Y': -100, 'Mass': 1, 'Status': 'Alive', 'Species': 'Seed'},
        {'Year': 1, 'Diet': 'Ghost', 'X': -100, 'Y': -100, 'Mass': 1, 'Status': 'Ghost', 'Species': 'Seed'}
    ])
    spatial_df = pd.concat([seed_rows, spatial_df], ignore_index=True)

    # --- NOW CREATE THE CHART ---
# ... (after your spatial_df seeding logic) ...

    fig_island = px.scatter(
        spatial_df, 
        x="X", y="Y", 
        animation_frame="Year", 
        animation_group="Species",
        size="Mass", 
        color="Diet",
        category_orders={"Diet": ["Prey", "Predator", "Ghost"]}, 
        color_discrete_map={'Prey': '#00CC96', 'Predator': '#FF4B4B', 'Ghost': '#FFFFFF'},
        hover_name="Species",
        range_x=[0, 100], range_y=[0, 100],
        template="plotly_dark"
    )

# --- THE "PRETTY" OVERHAUL ---
    fig_island.update_layout(
        images=[dict(
            source="https://i.ibb.co/CKc55vm2/Island-pic.png",
            xref="x", yref="y",
            x=0, y=100,      # Top-left corner
            sizex=100, sizey=100,
            sizing="contain", # CHANGE THIS from "stretch" to "contain"
            opacity=0.6,      # Bumped up for visibility
            layer="below"
        )],
        # --- THIS PART FIXES THE UGLY SQUASHING ---
        xaxis=dict(
            showgrid=False, showticklabels=False, title="",
            range=[0, 100], 
            fixedrange=True # Prevents user from zooming and breaking the map
        ),
        yaxis=dict(
            showgrid=False, showticklabels=False, title="",
            range=[0, 100],
            fixedrange=True,
            scaleanchor="x", # THIS IS THE MAGIC LINE: keeps it a square
            scaleratio=1
        ),
        # Make the container a nice square
        width=700,
        height=700,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    # 4. Make ghosts look like faint Xs and living things look solid
    fig_island.update_traces(marker=dict(line=dict(width=1, color='white')))

    st.plotly_chart(fig_island, use_container_width=True)
    # --- THE ACTIVITY LOG ---
    st.divider()
    st.subheader("📜 Island History Log")
    
    # Using a scrollable container so it doesn't take up the whole page
    log_container = st.container(height=300)
    with log_container:
        for entry in logs: # Show newest events at the top
            st.write(entry)



    st.success("Simulation complete! Notice the 'Dodo' growth before the predator arrived.")