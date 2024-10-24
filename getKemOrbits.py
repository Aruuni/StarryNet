import math
from lxml import etree

def create_kml(coordinates_file, output_file, icon_path, num_orbits, satellites_per_orbit, satellite_altitude, inclination, cone=False):
    def calculate_cone_radius(height, angle):
        return height * math.tan(math.radians(angle))

    def generate_circle_coordinates(center_lat, center_lon, radius, num_points=18):
        circle_coords = []
        for i in range(num_points):
            angle = math.radians(float(i) / num_points * 360)
            lat = center_lat + (radius / 111) * math.cos(angle)  # 111 km per degree latitude
            lon = center_lon + (radius / (111 * math.cos(math.radians(center_lat)))) * math.sin(angle)
            circle_coords.append((lon, lat))
        circle_coords.append(circle_coords[0])  # Close the circle
        return circle_coords

    def haversine(lon1, lat1, lon2, lat2):
        R = 6371  # Radius of the Earth in km
        dlon = math.radians(lon2 - lon1)
        dlat = math.radians(lat2 - lat1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    # Read the coordinates from the file
    with open(coordinates_file, 'r') as file:
        lines = file.readlines()

    # Split coordinates into orbits
    coordinates = []
    for i in range(num_orbits):
        orbit_coords = []
        for line in lines[i*satellites_per_orbit:(i+1)*satellites_per_orbit]:
            lat, lon, alt = map(float, line.strip().split(','))
            alt = int(alt) * 1000  # Multiply altitude by 1000
            orbit_coords.append((lon, lat, alt))
        coordinates.append(orbit_coords)

    # Calculate the cone radius for the satellite's range
    cone_angle = 45  # Example cone angle in degrees
    cone_radius = calculate_cone_radius(satellite_altitude, cone_angle)

    # Create the root KML element
    kml = etree.Element('kml', xmlns="http://www.opengis.net/kml/2.2")

    # Create a Document element
    document = etree.SubElement(kml, 'Document')

    # Create a Style for the satellites
    style = etree.SubElement(document, 'Style', id="satelliteStyle")
    icon_style = etree.SubElement(style, 'IconStyle')
    icon = etree.SubElement(icon_style, 'Icon')
    href = etree.SubElement(icon, 'href')
    href.text = f'file://{icon_path}'  # Local path to the icon
    scale = etree.SubElement(icon_style, 'scale')
    scale.text = '3.0'  # Larger icon size for visibility

    # Style for the cone projections
    cone_style = etree.SubElement(document, 'Style', id="coneStyle")
    poly_style = etree.SubElement(cone_style, 'PolyStyle')
    color = etree.SubElement(poly_style, 'color')
    color.text = '7dff0000'  # Red color with transparency
    line_style = etree.SubElement(cone_style, 'LineStyle')
    line_width = etree.SubElement(line_style, 'width')
    line_width.text = '1'  # Thinner lines

    # Add Placemarks for each satellite in this orbit
    for orbit_index, orbit_coords in enumerate(coordinates):
        for idx, (lon, lat, alt) in enumerate(orbit_coords):
            placemark = etree.SubElement(document, 'Placemark')
            name = etree.SubElement(placemark, 'name')
            name.text = f'Orbit {orbit_index + 1} Satellite {idx + 1}'
            style_url = etree.SubElement(placemark, 'styleUrl')
            style_url.text = '#satelliteStyle'
            point = etree.SubElement(placemark, 'Point')
            altitude_mode = etree.SubElement(point, 'altitudeMode')
            altitude_mode.text = 'absolute'  # Use the altitude from the file
            coordinates_elem = etree.SubElement(point, 'coordinates')
            coordinates_elem.text = f'{lon},{lat},{alt}'

            # Add cone projection for the satellite range
            if cone:
                circle_coords = generate_circle_coordinates(lat, lon, cone_radius)
                placemark_cone = etree.SubElement(document, 'Placemark')
                name_cone = etree.SubElement(placemark_cone, 'name')
                name_cone.text = f'Orbit {orbit_index + 1} Satellite {idx + 1} Cone'
                style_url_cone = etree.SubElement(placemark_cone, 'styleUrl')
                style_url_cone.text = '#coneStyle'
                polygon = etree.SubElement(placemark_cone, 'Polygon')
                altitude_mode = etree.SubElement(polygon, 'altitudeMode')
                altitude_mode.text = 'clampToGround'
                outer_boundary_is = etree.SubElement(polygon, 'outerBoundaryIs')
                linear_ring = etree.SubElement(outer_boundary_is, 'LinearRing')
                coordinates_elem_cone = etree.SubElement(linear_ring, 'coordinates')
                coordinates_elem_cone.text = " ".join(f"{lon},{lat},0" for lon, lat in circle_coords)

                # Add the line from the satellite to the ground circle
                for lon_circle, lat_circle in circle_coords:
                    placemark_line = etree.SubElement(document, 'Placemark')
                    line_style = etree.SubElement(placemark_line, 'LineStyle')
                    line_width = etree.SubElement(line_style, 'width')
                    line_width.text = '1'  # Thinner lines
                    line_string = etree.SubElement(placemark_line, 'LineString')
                    altitude_mode = etree.SubElement(line_string, 'altitudeMode')
                    altitude_mode.text = 'absolute'
                    coordinates_elem_line = etree.SubElement(line_string, 'coordinates')
                    coordinates_elem_line.text = f'{lon},{lat},{alt} {lon_circle},{lat_circle},0'

    # Connect all satellites in sequence and the last to the first to form a loop
    for orbit_index, orbit_coords in enumerate(coordinates):
        placemark = etree.SubElement(document, 'Placemark')
        linestyle = etree.SubElement(placemark, 'LineStyle')
        linewidth = etree.SubElement(linestyle, 'width')
        linewidth.text = '2'  # Line width
        linestring = etree.SubElement(placemark, 'LineString')
        altitude_mode = etree.SubElement(linestring, 'altitudeMode')
        altitude_mode.text = 'absolute'
        coordinates_elem = etree.SubElement(linestring, 'coordinates')
        coordinates_elem.text = " ".join(f"{lon},{lat},{alt}" for lon, lat, alt in orbit_coords) + " " + f"{orbit_coords[0][0]},{orbit_coords[0][1]},{orbit_coords[0][2]}"

    # Add ISLs between corresponding satellites in adjacent orbits if within range
    max_isl_range = 5016  # Maximum ISL range in km
    for i in range(satellites_per_orbit):
        for j in range(num_orbits):
            lon1, lat1, alt1 = coordinates[j][i]
            lon2, lat2, alt2 = coordinates[(j + 1) % num_orbits][i]
            distance = haversine(lon1, lat1, lon2, lat2)
            if distance <= max_isl_range:
                placemark_isl = etree.SubElement(document, 'Placemark')
                linestyle_isl = etree.SubElement(placemark_isl, 'LineStyle')
                linewidth_isl = etree.SubElement(linestyle_isl, 'width')
                linewidth_isl.text = '2'  # Line width for ISLs
                linestring_isl = etree.SubElement(placemark_isl, 'LineString')
                altitude_mode_isl = etree.SubElement(linestring_isl, 'altitudeMode')
                altitude_mode_isl.text = 'absolute'
                coordinates_elem_isl = etree.SubElement(linestring_isl, 'coordinates')
                coordinates_elem_isl.text = f"{lon1},{lat1},{alt1} {lon2},{lat2},{alt2}"

    # Write the KML to a file
    tree = etree.ElementTree(kml)
    tree.write(output_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')

# Example usage with a local icon path
local_icon_path = '/home/mihai/Desktop/StarryNet/satellite.png'  # Replace with your actual local path
online_path = "https://www.arcgis.com/sharing/rest/content/items/d8ea778740864e7bbf49e2574b514afa/data"

cone = False
num_orbits = 10
satellites_per_orbit = 22
inclination = 53
satellite_altitude = 550
print('Creating KML file...')
print('starlink-%s-%s-550-%s.kml' % (num_orbits, satellites_per_orbit, inclination))
create_kml('starlink-%s-%s-550-%s-grid-LeastDelay/position/0.txt' % (num_orbits, satellites_per_orbit, inclination), 
           '/home/mihai/Desktop/satellites-%s-%s-550-%s.kml'% (num_orbits, satellites_per_orbit, inclination), 
           local_icon_path.replace('\\', '/'), 
           num_orbits, 
           satellites_per_orbit,
           satellite_altitude,
           inclination,
           cone)
