# Open the text file
with open('Looking.txt', 'r') as file:
    # Read all lines
    lines = file.readlines()

# Initialize counters
total_count = 0
correct_posture_count = 0

# Loop through each line
for line in lines:
    # Strip any leading/trailing whitespace
    line = line.strip()
    # If the line indicates correct posture, count it
    if line == 'Correct Posture':
        correct_posture_count += 1
    # Always count total lines
    total_count += 1

# Calculate the accuracy percentage
accuracy_percentage = (correct_posture_count / total_count) * 100

# Print the result
print("Total count:", total_count)
print("Correct Posture count:", correct_posture_count)
print("Accuracy percentage:", accuracy_percentage)
