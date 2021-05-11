def get_surface_height(substrate, coordinates, percentage_of_box_to_search=80.0):
    cutoff = substrate["c"] * (percentage_of_box_to_search / 100)
    z = [xyz[2] for xyz in coordinates if xyz[2] < cutoff]
    return max(z)
