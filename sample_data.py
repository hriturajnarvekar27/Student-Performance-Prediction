import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate 1000 rows
n_samples = 1000
data = {
    'roll_number': [f'R{i:04d}' for i in range(1, n_samples + 1)],
    'previous_percentage': np.random.beta(5, 2, n_samples) * 45 + 50,  # Beta distribution: more values closer to 95
    'past_attendance': np.random.beta(5, 2, n_samples) * 40 + 60,      # More values closer to 100
    'study_hours': np.random.uniform(5, 20, n_samples),
    'commute_time': np.random.uniform(0, 2, n_samples),
    'board_exam_marks': np.random.beta(5, 2, n_samples) * 35 + 60,     # More values closer to 95
    'tuition_hours': np.random.uniform(0, 10, n_samples),
}

# Adjusted attendance prediction: Stronger influence of past_attendance
data['attendance'] = (0.9 * data['past_attendance'] +
                      0.05 * data['study_hours'] -
                      0.05 * data['commute_time'] +
                      np.random.normal(0, 0.1, n_samples)).clip(60, 100)

# Adjusted exam marks prediction: Removed fieldwork_hours
data['exam_marks'] = (0.5 * data['previous_percentage'] +
                      0.3 * data['attendance'] +
                      0.1 * data['study_hours'] -
                      0.05 * data['commute_time'] +
                      0.1 * data['board_exam_marks'] +
                      np.random.normal(0, 0.1, n_samples)).clip(50, 100)

# Create DataFrame and save
df = pd.DataFrame(data)
df.to_csv('sample_data.csv', index=False)
print("Updated sample dataset created: sample_data.csv")