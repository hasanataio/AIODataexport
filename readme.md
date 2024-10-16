# Data Extraction and Transformation from Toast and Square

## Overview

This README provides detailed instructions for extracting employee and menu data from Toast and Square, transforming the data, and generating configuration files for the AIO (Artificial Intelligence Operator) system. The process involves downloading CSV files, uploading them to an application, and using scripts to populate various sheets in the output files.

## Data Extraction from Toast

### Employee Data

**Toast Exportables:**

1. **Employees Data**: Includes employee names, roles, salary types, contact details (emails, phone numbers, etc.). This data is primarily used for automation purposes.

**Manually Extracted (No Exportables):**

1. **General Settings**: Includes table layout, business details, business name, online ordering details.
2. **Service Charges**

ayroll Information

- Payroll info such as salary types is extracted from the payroll provider.
- Roles are assigned using AI and compared in the user_roles Excel file.
- If a user has multiple roles, they are added twice with different role IDs in the user_roles column.

### Menu Data

**Toast Exportables:**

1. **Default Assigned Menu Names**: Assigned based on the restaurant's name.
2. **Menu Categories**:
   - Parent categories are based on names of menus in Toast.
   - Generates IDs for categories.
   - Archived menus marked as "Yes" are shown on the Point of Sale (POS).
   - POS display names are truncated for future reference.
3. **Menu Groups**:
   - Assigns setting IDs for archived menus.
   - Assigns parent categories based on the Parent Name column.
   - If a parent category is not found, it's checked in the same column.
4. **Items**:
   - Item names, base prices, and categories are extracted.
   - Category assignment is based on item names, sub-categories, and categories.

### Modifier Groups and Options

- Modifier Groups are obtained from Toast's Option Group Name.
- Modifier Options are obtained from Toast's Modifier.
- `ItemName` is the Parent Menu Selection in the report.
- `MenuExport` has parent categories and should be added to the category sheet.
- `MenuGroup` has sub-categories and should be added to the category sheet (mapping from parent as well).
- `MenuItem` is for items.
- `MenuOption` has modifiers groups.
- `MenuOptionGroup` has modifiers.

## Data ETL Process

1. Obtain access to Toast.
2. Export employee info and job information in CSV format with specific naming conventions.
3. Assign roles based on job descriptions and wages.
4. Fill data in the output file using a script.
5. Perform checks on pay types and define them accordingly.
6. No current UI available for running scripts.

### Steps

1. Download the following files from Toast:

   - "Menu_Export.csv"
   - "MenuGroup_Export.csv"
   - "MenuItem_Export.csv"
   - "MenuOptionGroup_Export.csv"
   - "MenuOption_Export.csv"
   - "ItemSelectionDetails.csv"
   - "ItemModifierSelectionDetails.csv"

2. Upload the files to the application.

3. The code has the Config File already loaded and will fill these sheets:

   - `Menu`, `Category`, `Item`, `Category Items`, `Modifier`, `Modifier Option`, `Item Modifiers`, `Modifier ModifierOptions`

   - `parent_categories` are exported from "Menu_Export.csv".
   - `sub_categories` are exported from "MenuGroup_Export.csv".
   - The `Category` sheet is filled using the above two files.
   - Item details are exported from "MenuItem_Export.csv".
   - The `Item` sheet is filled using this file.
   - Modifiers are exported from "MenuOptionGroup_Export.csv".
   - The `Modifier` sheet is filled using this file.
   - Modifier options are exported from "MenuOption_Export.csv".
   - The `Modifier Option` sheet is filled using this file.
   - Item categories are exported from "ItemSelectionDetails.csv".
   - The `Category Items` sheet is filled using this report, comparing the IDs to the `Category` and `Item` sheets already filled.
   - Modifier groups are exported from "ItemModifierSelectionDetails.csv".
   - The `Item Modifiers` sheet is filled using this report, comparing the IDs to the `Item` and `Modifier` sheets already filled.
   - Modifier options are exported from "ItemModifierSelectionDetails.csv".
   - The `Modifier ModifierOptions` sheet is filled using this report, comparing the IDs to the `Modifier` and `Modifier Option` sheets already filled.

4. Download the Config File from the application.

## Data Extraction from Square

### Employee Data

**Square Exportables:**

1. **Employees Data**: Includes employee names, roles, salary types, contact details (emails, phone numbers, etc.). The app transforms this data into the desired AIO config file.

## Data Export Application

The application for data export can be accessed at [Data Export](http://44.231.228.32:8007/).

## Conclusion

This guide outlines the process of extracting data from Toast and Square for employees and menu items, as well as the ETL (Extract, Transform, Load) process involved. Follow the steps carefully to ensure accurate data extraction and transformation.
