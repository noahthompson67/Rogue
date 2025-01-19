import random
import math


def generate_loopy_path(
        length=100,
        step_range=(1, 5),
        loopiness=2,
        x_bounds=(-100, 100),
        y_bounds=(-100, 100)
):
    """
    Generate a list of coordinates outlining a random, loopy closed path,
    ensuring all adjacent points are near each other.

    Args:
        length (int): Number of points in the path (including the starting/ending point).
        step_range (tuple): Minimum and maximum step size for each point.
        loopiness (float): Determines the amount of curvature. Higher values create tighter loops.
        x_bounds (tuple): Lower and upper bounds for x-coordinates.
        y_bounds (tuple): Lower and upper bounds for y-coordinates.

    Returns:
        list: A list of (x, y) tuples representing the closed path.
    """
    path = [(0, 0)]  # Start at the origin
    angle = random.uniform(0, 2 * math.pi)  # Initial random direction

    for i in range(length - 1):
        # Gradually adjust angle to keep the points near each other
        angle += random.uniform(-math.pi / loopiness, math.pi / loopiness)

        # Random step size
        step_size = random.uniform(*step_range)

        # Calculate new point
        last_x, last_y = path[-1]
        new_x = last_x + step_size * math.cos(angle)
        new_y = last_y + step_size * math.sin(angle)

        # Clamp coordinates to the specified bounds
        new_x = max(x_bounds[0], min(new_x, x_bounds[1]))
        new_y = max(y_bounds[0], min(new_y, y_bounds[1]))

        path.append((new_x, new_y))

    # Adjust the final point to ensure it closes the loop smoothly
    path[-1] = path[0]

    return path


# Example usage
loopy_path = generate_loopy_path(
    length=200,
    step_range=(2, 10),
    loopiness=3,
    x_bounds=(-50, 50),
    y_bounds=(-50, 50)
)
print(loopy_path)



import matplotlib.pyplot as plt

# Generate a path
loopy_path = generate_loopy_path(length=200, step_range=(2, 10), loopiness=3)

# Extract x and y coordinates
x_coords, y_coords = zip(*loopy_path)

# Plot the path
plt.plot(x_coords, y_coords, marker='o', markersize=2)
plt.title("Random Loopy Path")
plt.xlabel("X")
plt.ylabel("Y")
plt.axis('equal')
plt.show()
