# ML Model Training Data Strategy

## Overview

The ML model uses a two-phase training approach:
1. **Initial Training**: Uses synthetic CSV files to bootstrap the model
2. **Continuous Retraining**: Uses only real appointment data from Firebase

## Training Phases

### Phase 1: Initial Training (Bootstrap)

**When**: First time training or when no real data exists

**Data Source**: Synthetic CSV files
- `durations-synthetic-1.csv` (100 records)
- `durations-synthetic-2.csv` (100 records)
- `durations-synthetic-3.csv` (100 records)
- **Total**: 300 synthetic training samples

**Purpose**: 
- Provides fundamental patterns for the model to learn from
- Ensures the model can make predictions even before real data is collected
- Establishes baseline accuracy

**Log Output**:
```
No real data available - using SYNTHETIC CSV files for initial training
Once real appointment data is collected, future retraining will use real data only
```

### Phase 2: Continuous Retraining (Real Data)

**When**: Real appointment data exists in Firebase (`mlTrainingData` collection)

**Data Source**: **ONLY** Firebase real appointment data
- Actual appointment durations from completed sessions
- Real patient types, procedures, days, and times
- Custom procedures learned from clinic usage
- **Synthetic CSVs are NOT used** in this phase

**Purpose**:
- Learns from actual clinic patterns and workflows
- Adapts to clinic-specific procedures and timing
- Improves accuracy based on real-world data
- Custom procedures get accurate predictions over time

**Log Output**:
```
Using REAL appointment data from Firebase for retraining
Skipping synthetic CSV files (only used for initial training)
```

## How It Works

### Decision Logic

```python
if real_firebase_data_exists:
    use_only_real_data()  # Skip synthetic CSVs
else:
    use_synthetic_csvs()  # Initial training only
```

### Example Flow

1. **First Run** (No Firebase data):
   - Loads 300 records from 3 synthetic CSV files
   - Trains model with synthetic data
   - Model can now make predictions

2. **After Appointments** (Firebase has data):
   - Exports real appointment data from Firebase
   - **Skips synthetic CSVs**
   - Trains model with only real data
   - Model learns actual clinic patterns

3. **Weekly Retraining**:
   - Always uses only real Firebase data
   - Synthetic CSVs are never used again
   - Model continuously improves with new data

## Benefits

✅ **Accurate Learning**: Model learns from real clinic patterns, not synthetic assumptions  
✅ **Custom Procedures**: Automatically learns custom procedures added by clinics  
✅ **Clinic-Specific**: Adapts to each clinic's actual workflow and timing  
✅ **Continuous Improvement**: Gets better as more real data is collected  
✅ **No Synthetic Bias**: Once real data exists, model is purely data-driven  

## Configuration

The script automatically detects which phase to use:

- **Check Firebase**: `mlTrainingData` collection with `usedForTraining: false`
- **If data exists**: Use real data only
- **If no data**: Use synthetic CSVs for initial training

No manual configuration needed - it's automatic!

## Monitoring

Check training logs to see which phase is active:

```bash
# Check retraining.log
cat "smart scheduling/retraining.log"

# Look for:
# "Using REAL appointment data" → Phase 2 (real data)
# "using SYNTHETIC CSV files" → Phase 1 (initial training)
```

## FAQ

**Q: Will synthetic data be used again after real data exists?**  
A: No. Once real data is available, synthetic CSVs are permanently skipped.

**Q: What if Firebase data is deleted?**  
A: The script will fall back to synthetic CSVs for initial training again.

**Q: Can I force using synthetic data?**  
A: Only if you clear all Firebase training data. Otherwise, real data is always preferred.

**Q: How much real data is needed?**  
A: Minimum 50 samples (configurable via `MIN_TRAINING_SAMPLES`). More is better!

