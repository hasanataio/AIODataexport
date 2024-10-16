import pandas as pd

def fill_modifier_groups(sheets_dict, modifier_options):
    # Convert all relevant columns to lower case and strip for comparison
    sheets_dict["Modifier"]["modifierName"] = sheets_dict["Modifier"]["modifierName"].str.lower().str.strip()
    sheets_dict["Modifier Option"]["optionName"] = sheets_dict["Modifier Option"]["optionName"].str.lower().str.strip()

    # Drop rows with missing modifierName or optionName
    sheets_dict["Modifier"].dropna(subset=['modifierName'], inplace=True)
    sheets_dict["Modifier Option"].dropna(subset=['optionName'], inplace=True)

    modifier_options["Modifier"] = modifier_options["Modifier"].str.lower().str.strip()
    modifier_options["Option Group Name"] = modifier_options["Option Group Name"].str.lower().str.strip()

    # Drop rows with missing Modifier or Option Group Name
    modifier_options.dropna(subset=['Modifier', 'Option Group Name'], inplace=True)

    print("Modifier DataFrame:")
    print(sheets_dict["Modifier"].head())
    print("\nModifier Option DataFrame:")
    print(sheets_dict["Modifier Option"].head())
    print("\nModifier Options DataFrame:")
    print(modifier_options[["Modifier", "Option Group Name"]].head())

    # Create dictionaries for quick lookups
    modifier_dict = sheets_dict["Modifier"].set_index("modifierName")["id"].to_dict()
    option_group_dict = sheets_dict["Modifier Option"].set_index("optionName")["id"].to_dict()

    print("\nModifier Dictionary:")
    print(modifier_dict)
    print("\nOption Group Dictionary:")
    print(option_group_dict)

    rows = []

    # Iterate through the modifier options to fill in the rows
    for index, row in modifier_options.iterrows():
        modifier_name = row["Modifier"]
        option_group_name = row["Option Group Name"]

        # Get the modifier_id and option_group_id from dictionaries
        modifier_id = modifier_dict.get(option_group_name)
        option_group_id = option_group_dict.get(modifier_name)

        # Check if the modifier_id and option_group_id exist before trying to access them
        if modifier_id is not None and option_group_id is not None:
            rows.append({
                "modifierId": modifier_id,
                "modifierOptionId": option_group_id,
                "isDefaultSelected": False,
                "maxLimit": 1
            })
        else:
            # Print a warning for any missing modifiers or option groups
            if modifier_id is None:
                print(f"Warning: Option Group '{option_group_name}' not found in modifier dictionary")
            if option_group_id is None:
                print(f"Warning: Modifier '{modifier_name}' not found in option group dictionary")

    # Create the DataFrame
    modifiers_groups_df = pd.DataFrame(rows, columns=["modifierId", "modifierOptionId", "isDefaultSelected", "maxLimit"])

    # Drop duplicates
    modifiers_groups_df.drop_duplicates(subset=["modifierId", "modifierOptionId"], keep='first', inplace=True)

    # Fill the sheets_dict["Modifier ModifierOptions"] with the new data
    sheets_dict["Modifier ModifierOptions"] = modifiers_groups_df

    # Debug output
    print("\nGenerated Modifier Groups DataFrame:")
    print(modifiers_groups_df)

    return sheets_dict

# Example usage
sheets_dict = {
    "Modifier": pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "modifierName": ["size", "ignalat classic caprese", "mista", "renata options", "dessert", "coffee mods", "burrata options", "pasta options", "insalate options"]
    }),
    "Modifier Option": pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "optionName": ["1/4 lb.", "6/+", "sale 6/+", "wc", "regular", "sugar", "add roma tomatoes", "add 5 shrimp", "add shrimp"]
    })
}

modifier_options = pd.DataFrame({
    "Modifier": ["add roma tomatoes", "add 5 shrimp", "add shrimp", "with milk", "sugar"],
    "Option Group Name": ["burrata options", "pasta options", "insalate options", "coffee mods", "coffee mods"]
})

# Call the function
result = fill_modifier_groups(sheets_dict, modifier_options)