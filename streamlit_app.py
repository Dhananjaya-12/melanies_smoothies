# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# App title
st.title(f"🥤 Smoothie Orders App (Streamlit v{st.__version__})")
st.write(
    """
    Welcome to the Smoothie App!  
    Build your own smoothie and submit your order below. 🚀
    """
)

# Connect to Snowflake using Streamlit's connection
cnx = st.connection("snowflake")
session = cnx.session()

# Input for smoothie name
name_on_order = st.text_input("Name for your Smoothie:")
if name_on_order:
    st.write("✅ The name of your smoothie will be:", name_on_order)

# Load available fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

st.dataframe(data=my_dataframe, use_container_width=True)

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5,
)

if ingredients_list and name_on_order:
    # Build a string of chosen ingredients
    ingredients_string = " ".join(ingredients_list)

    # Show SQL for debugging (optional)
    st.write("Preview SQL Insert Statement:")
    st.code(
        f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    # Button to run the insert
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.table("smoothies.public.orders").insert(
            {"INGREDIENTS": ingredients_string, "NAME_ON_ORDER": name_on_order}
        )
        st.success(
            f"🎉 Your Smoothie has been ordered, {name_on_order}!",
            icon="✅",
        )
