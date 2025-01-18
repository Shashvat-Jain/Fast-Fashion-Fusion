# Workflow Documentation

## Data Ingestion Workflow

1. **DataIngestion Page**:
   - A button is available on the page labeled `Find New Product Types`.
   - On clicking the button:
     - The system finds and displays new product types.
     - These products are saved to the directory:
       ```
       ../backend/data_ingestion_engine/data
       ```
   - After saving, the `img2txt2txt_engine` performs feature extraction on the saved data:
     - The extracted features are saved to:
       ```
       ../backend/img2txt2txt_engine/data
       ```

---

## Verification Workflow

1. **Verification Page**:
   - Retrieves data from the directory:
     ```
     ../backend/img2txt2txt_engine/data
     ```
   - Displays all rows from the file in the directory with checkboxes for each row.

2. **Checkbox Functionality**:
   - If a checkbox is ticked:
     - The corresponding row is added to:
       ```
       ../backend/verification_engine/data
       ```

3. **Post-Saving Actions**:
   - **Trend Engine**:
     - Takes the data from:
       ```
       ../backend/verification_engine/data
       ```
     - Performs trend analysis.
   - **Ontology Engine**:
     - Updates the ontology using the data from:
       ```
       ../backend/verification_engine/data
       ```

---
