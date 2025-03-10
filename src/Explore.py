import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sklearn  # pip install scikit-learn 

from PIL import Image
import codecs
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu  # pip install streamlit-menu
st.title("⚽ FIFA Data Lab: The Game")

# Datasets dictionary
datasets = {
    "FIFA17": "Datasets/FIFA17_official_data.csv",
    "FIFA18": "Datasets/FIFA18_official_data.csv",
    "FIFA19": "Datasets/FIFA19_official_data.csv",
    "FIFA20": "Datasets/FIFA20_official_data.csv",
    "FIFA21": "Datasets/FIFA21_official_data.csv",
    "FIFA22": "Datasets/FIFA22_official_data.csv",
}

st.title("Explore")
selected = option_menu(menu_title=None, options=["01: Data", "02: Viz", "03: Pred"], orientation="horizontal")

if selected == "01: Data":
    st.markdown("### :violet[Data Overview]")
    st.markdown("## :blue[Select a dataset]")
    dataset_option = st.selectbox("FIFA Version: ",list(datasets.keys()));
    df = pd.read_csv(datasets[dataset_option])
    st.markdown("### :violet[Data Sumary]")
    st.dataframe(df.describe())

    st.markdown("### :violet[Data Prevew Top 10 rows]")
    st.dataframe(df.head(10))
    # Select category to sort players
    st.markdown("### :violet[ View Top 10 Players Various Categories]")
    categories = [
        "Age", "Overall", "Potential", "Value(€M)", "Wage(€K)",  
        "Acceleration", "SprintSpeed", "Agility", "Balance", "Strength", "Stamina", "Jumping",  
        "Crossing", "Finishing", "Dribbling", "FKAccuracy", "LongPassing", "BallControl", "Positioning", "Vision", "Composure",  
        "StandingTackle", "SlidingTackle", "Interceptions", "Aggression", 
        "GKDiving", "GKHandling", "GKKicking", "GKPositioning", "GKReflexes"  
    ]
    category = st.selectbox("Top Ten in:", categories)
    ## To be Modified
    if category in df.columns:
    # Base columns to display
        base_columns = ["Name","Nationality","Club", "Age", "Overall", "Value(€M)", "Wage(€K)"]
    
    # Add the selected category only if it's not already in base_columns
        columns_to_display = base_columns if category in base_columns else base_columns + [category]
    
    # Get top 10 players sorted by the selected category
        top_10_players = df.sort_values(by=category, ascending=False).head(10)
    
    # Display selected columns
        st.dataframe(top_10_players[columns_to_display])
    else:
        st.write("⚠️ Selected category not found in the dataset.")



        
elif selected == "02: Viz":
    st.markdown("### :violet[Data Visualization]")
    st.markdown("## :blue[Select a dataset]")
    dataset_option = st.selectbox("FIFA Version: ",list(datasets.keys()));
    df = pd.read_csv(datasets[dataset_option])

    def convert_value(val):
        if isinstance(val, str):
            val = val.replace('€', '').strip()
            if 'M' in val:
                return float(val.replace('M', ''))
            elif 'K' in val:
                return float(val.replace('K', '')) / 1000
        try:
            return float(val)
        except:
            return None

    df['Value(€M)'] = df['Value(€M)'].apply(convert_value)

    # Combine all FIFA datasets into one DataFrame
    combined_df = pd.DataFrame()

    for year, path in datasets.items():
        temp_df = pd.read_csv(path)
        temp_df["FIFA Edition"] = year  # add column to track edition
        combined_df = pd.concat([combined_df, temp_df], ignore_index=True)

    # Convert Value column
    def convert_value(val):
        if isinstance(val, str):
            val = val.replace('€', '').strip()
            if 'M' in val:
                return float(val.replace('M', ''))
            elif 'K' in val:
                return float(val.replace('K', '')) / 1000
        try:
            return float(val)
        except:
            return None

    combined_df["Value(€M)"] = combined_df["Value(€M)"].apply(convert_value)

    # Select only numeric columns
    Numeric_df = df.select_dtypes(include=['number'])

    # Define the expected columns
    expected_columns = ["Age", "Wage(€K)", "Crossing", "Finishing", "Dribbling", 
                        "Acceleration", "Agility", "Strength", "Penalties", "Best Overall Rating"]
    
    Numeric_df.columns = Numeric_df.columns.str.strip()

    # Check for missing columns
    missing_columns = [col for col in expected_columns if col not in Numeric_df.columns]
    if missing_columns:
        st.warning(f"Missing columns: {missing_columns}")
    else:
        # Select only the required columns
        Filtered_Numeric_df = Numeric_df[expected_columns]

        # Compute correlation matrix
        correlation_matrix = Filtered_Numeric_df.corr()

        # Display heatmap
        st.markdown("## 🔥 Heatmap of Feature Correlations")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)

        # Highest Valued Players per FIFA Edition
        
        st.markdown("### 💸 Top 10 Highest-Valued Players")

        # Get the top 10 highest-valued players for the selected FIFA edition
        top_valued_players = df.nlargest(10, 'Value(€M)')

        # Create a bar plot
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = sns.barplot(
            y=top_valued_players['Name'],
            x=top_valued_players['Value(€M)'],
            palette="plasma",
            ax=ax
        )

        # Add value labels to each bar
        for container in bars.containers:
            ax.bar_label(container, fmt='%.0f', label_type='edge', padding=3, fontsize=10, color='black', weight='bold')

        
        ax.set_title(f"Top 10 Highest-Valued Players in FIFA {dataset_option}")
        ax.set_xlabel("Value(€M)")
        ax.set_ylabel("Player Name")

        # Display the plot 
        st.pyplot(fig)

        # 🎯 Track a Specific Player Across FIFA Editions
        st.markdown("## 📈 Player Progression Across Editions")

        # Select player name
        player_names = combined_df["Name"].dropna().unique()
        selected_player = st.selectbox("Select a player to track:", sorted(player_names))

        # Filter player data across editions
        player_data = combined_df[combined_df["Name"] == selected_player]

        # Sort by edition
        player_data = player_data.sort_values(by="FIFA Edition")

        # Plot value and overall rating progression
        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.plot(player_data["FIFA Edition"], player_data["Value(€M)"], marker='o', label="Value (€M)", color='green')
        ax1.set_ylabel("Value (€M)", color='green')
        ax1.tick_params(axis='y', labelcolor='green')

        # Second y-axis for overall rating
        ax2 = ax1.twinx()
        ax2.plot(player_data["FIFA Edition"], player_data["Overall"], marker='s', label="Overall Rating", color='blue')
        ax2.set_ylabel("Overall Rating", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')

        # Title and labels
        plt.title(f"{selected_player}'s Value and Overall Rating Over FIFA Editions")
        fig.tight_layout()

        # Show plot
        st.pyplot(fig)


        st.markdown("Player Nationality Distribution")
        st.write("Explore which countries contribute the most players in each FIFA edition.")

        # Get top 10 nationalities
        top_nationalities = df["Nationality"].value_counts().head(10)

        # Create plot
        fig, ax = plt.subplots(figsize=(8, 6))      

        sns.barplot(x=top_nationalities.values, y=top_nationalities.index, ax=ax, palette="crest")
        ax.set_xlabel("Number of Players")
        ax.set_ylabel("Nationality")
        ax.set_title(f"{10} Player Nationalities in FIFA {dataset_option}")

        # Show plot
        st.pyplot(fig)

        st.markdown("## 🔥 Distributions of Football Players")
        st.write("select a category to view Football Players Distibution")

        categories = {
            "Age": "Age",
            "Wage (€K)": "Wage(€K)",
            "Weight (lbs)": "Weight(lbs)",
            "Preferred Foot": "Preferred Foot",
            "Best Overall Rating": "Best Overall Rating"
        }

        bins = {
            "Age": [15, 20, 25, 30, 35, 40, 45],
            "Wage (€K)": [0, 50, 100, 200, 500, 1000, 5000],
            "Weight (lbs)": [120, 140, 160, 180, 200, 220, 250],
            "Best Overall Rating": [40, 50, 60, 70, 80, 90, 100]
        }
        # Allow user to select a category
        selected_category = st.selectbox("Choose a category:", list(categories.keys()))

        # Allow user to choose Pie or Bar Chart
        chart_type = st.radio("Select Chart Type:", ["Pie Chart", "Bar Chart"])

        # Convert numeric values into bins if necessary
        if selected_category in bins:
            df[categories[selected_category]].fillna(df[categories[selected_category]].median(), inplace=True)
            df[selected_category] = pd.cut(df[categories[selected_category]], bins=bins[selected_category])

        # Plotting the distribution
        fig, ax = plt.subplots(figsize=(8, 6))
    sizes = df[selected_category].value_counts()
    if chart_type == "Pie Chart":
        # Pie Chart
        labels = sizes.index.astype(str)

        wedges, texts, autotexts = ax.pie(
            sizes,
            startangle=90,
            colors=sns.color_palette("Set2"),
            wedgeprops={'edgecolor': 'black'},
            labels=None, 
            autopct=lambda p: f'{p:.2f}%' if p > 3 else "",  # Hide very small values
            pctdistance=0.6
        )

        ax.legend(wedges, labels, title=selected_category, loc="center left", bbox_to_anchor=(1, 0.5))
        ax.set_ylabel("")
        ax.set_title(f"Distribution of {selected_category}")
    else:
        # Bar Chart
        sns.barplot(x=sizes.index.astype(str), y=sizes.values, ax=ax, palette="Set2", edgecolor="black")
        ax.set_ylabel("")
        ax.set_title(f"Distribution of {selected_category}")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    # Show Chart
    st.pyplot(fig)

    st.markdown("## 🔥 Distributions of Football Players")
    

   
elif selected == "03: Pred":
    st.markdown("### :violet[Data Prediction]")
    st.markdown("<p style='font-size:20px; color:white;'>Select a dataset</p>", unsafe_allow_html=True)
    dataset_option = st.selectbox("FIFA Version: ",list(datasets.keys()));
        