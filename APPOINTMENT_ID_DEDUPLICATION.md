# Appointment ID-Based Duplicate Detection Fix

## Problem Identified

The ML training pipeline had a potential bug where duplicate detection would incorrectly mark legitimate appointments as duplicates if they had the same:
- Procedure type
- Patient type  
- Day of week
- Time period
- Duration

**Example Scenario:**
- Patient books "Extraction" for "Adult" on "Monday" "Morning" → 25 minutes
- Same patient books another "Extraction" for "Adult" on "Monday" "Morning" → 25 minutes (different appointment, same details)
- Without `appointment_id`, both would be treated as duplicates and one would be removed

## Solution

### Changes Made

1. **Added `appointmentId` support to CSV loading**
   - The script now preserves `appointment_id` from CSV files
   - If `appointment_id` is missing, generates a unique ID based on source and index

2. **Updated duplicate detection logic**
   - Duplicates are now detected **only** based on `appointmentId` (not feature columns)
   - This ensures that appointments with identical details but different IDs are both kept
   - Logs show how many duplicates were removed

3. **Training data strategy**
   - **Initial training**: Uses synthetic CSV files (`durations-synthetic-1.csv`, `durations-synthetic-2.csv`, `durations-synthetic-3.csv`) when no real data exists
   - **Retraining**: Once real appointment data is available in Firebase, uses ONLY real data (synthetic CSVs are skipped)
   - This ensures the model learns from actual clinic patterns, not synthetic data

4. **Firebase data integration**
   - Firebase training data now includes `appointmentId` (from `appointmentId` or `appointment_id` field, or auto-generated)

### CSV File Requirements

Your CSV files should include an `appointment_id` column:

```csv
appointment_id,service_type,patient_type,day_of_week,appointment_time,avg_duration
test-0001,Extraction,Adult,Monday,Morning,22.5
test-0002,Scale and polish,Adult,Tuesday,Afternoon,18
...
```

### Benefits

✅ **Accurate duplicate detection**: Only removes true duplicates (same appointment ID)  
✅ **Preserves legitimate data**: Multiple appointments with same details are all kept  
✅ **Better training data**: More diverse examples improve model accuracy  
✅ **Audit trail**: Can track which specific appointments were used for training  

### Usage

Run the training script as before:

```bash
python "smart scheduling/auto_retrain_model.py"
```

The script will:
1. Check if real Firebase data exists
2. If real data exists: Use ONLY real data (skip synthetic CSVs)
3. If no real data: Use synthetic CSVs for initial training
4. Export new data from Firebase (if configured)
5. Remove duplicates based on `appointmentId` only
6. Train the model with the cleaned dataset

### Logging

The script now logs:
- Number of records loaded from each CSV file
- Total samples before deduplication
- Number of duplicates removed (based on `appointmentId`)
- Final unique training sample count

Example output:
```
Loaded 100 records from durations-synthetic-1.csv
Loaded 100 records from durations-synthetic-2.csv
Loaded 100 records from durations-synthetic-3.csv
Total training samples before deduplication: 300
Removed 0 duplicate records based on appointmentId
Total unique training samples: 300
```

