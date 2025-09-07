# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Connect to Snowflake using Streamlit secrets
cnx = st.connection("snowflake")
session = cnx.session()

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Build your dream smoothie by choosing fruits below:")

# Input: Customer Name
name_on_order = st.text_input("Your Name:")
if name_on_order:
    st.write(f"Smoothie will be prepared for: **{name_on_order}**")

# Get fruit options from Snowflake
fruit_options_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .to_pandas()
)

# Ingredient selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options_df["FRUIT_NAME"].tolist(),
    max_selections=5,
)

# Show nutrition info and preview order
if ingredients_list:
    st.subheader("🍎 Nutrition Information")
    ingredients_string = ", ".join(ingredients_list)

    for fruit in ingredients_list:
        search_on = fruit_options_df.loc[
            fruit_options_df["FRUIT_NAME"] == fruit, "SEARCH_ON"
        ].iloc[0]

        if search_on == "N/A":
            st.info(f"{fruit} added to your smoothie! ✅ (No nutrition data available)")
        else:
            response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            if response.status_code == 200:
                fruit_data = response.json()
                st.write(f"**{fruit}** nutrition:")
                st.dataframe(pd.json_normalize(fruit_data), use_container_width=True)
            else:
                st.warning(f"Could not fetch nutrition info for {fruit}")

    # Submit order
    if st.button("🥤 Submit Order"):
        insert_sql = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES (?, ?)
        """
        session.sql(insert_sql, (ingredients_string, name_on_order)).collect()
        st.success(f"Your smoothie order has been placed, {name_on_order}! ✅")
