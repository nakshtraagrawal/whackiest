from flask import Flask, request, jsonify, render_template
import networkx as nx

app = Flask(__name__)

class CampusMap:
    def __init__(self):
        self.map = nx.Graph()
        self.add_rooms_and_connections()
    
    def add_rooms_and_connections(self):
        # Rooms with coordinates for visual representation
        # Format: (room_id, description, x, y)
        rooms = [
            # Ground Floor
            ("G01", "Main Entrance", 100, 400),
            ("G02", "Reception", 300, 400),
            ("G03", "Cafeteria", 500, 400),
            ("G04", "Library", 300, 300),
            
            # First Floor
            ("101", "Computer Lab", 100, 200),
            ("102", "Physics Lab", 300, 200),
            ("103", "Chemistry Lab", 500, 200),
            ("104", "Classroom", 500, 100)
        ]
        
        # Add rooms with coordinates
        for room_id, description, x, y in rooms:
            self.map.add_node(room_id, description=description, x=x, y=y)
        
        # Add connections (paths between rooms)
        connections = [
            ("G01", "G02"),  # Main Entrance to Reception
            ("G02", "G03"),  # Reception to Cafeteria
            ("G02", "G04"),  # Reception to Library
            ("G03", "G04"),  # Cafeteria to Library
            ("G02", "102"),  # Reception to Physics Lab (stairs)
            ("101", "102"),  # Computer Lab to Physics Lab
            ("102", "103"),  # Physics Lab to Chemistry Lab
            ("103", "104")   # Chemistry Lab to Classroom
        ]
        
        self.map.add_edges_from(connections)
    
    def get_path_coordinates(self, path):
        """Get coordinates for each room in the path"""
        coordinates = []
        for room in path:
            x = self.map.nodes[room]['x']
            y = self.map.nodes[room]['y']
            coordinates.append({
                'id': room,
                'x': x,
                'y': y,
                'description': self.map.nodes[room]['description']
            })
        return coordinates

    def get_all_rooms(self):
        """Get all rooms with their coordinates"""
        return [{
            'id': room,
            'x': self.map.nodes[room]['x'],
            'y': self.map.nodes[room]['y'],
            'description': self.map.nodes[room]['description']
        } for room in self.map.nodes()]

    def get_all_paths(self):
        """Get all connections for drawing the map"""
        return [(
            {
                'id': start,
                'x': self.map.nodes[start]['x'],
                'y': self.map.nodes[start]['y']
            },
            {
                'id': end,
                'x': self.map.nodes[end]['x'],
                'y': self.map.nodes[end]['y']
            }
        ) for start, end in self.map.edges()]

    def get_directions(self, start_room, end_room):
        try:
            path = nx.shortest_path(self.map, start_room, end_room)
            coordinates = self.get_path_coordinates(path)
            
            # Generate text directions
            directions = []
            for i in range(len(path) - 1):
                current = path[i]
                next_room = path[i + 1]
                current_desc = self.map.nodes[current]['description']
                next_desc = self.map.nodes[next_room]['description']
                directions.append(f"From {current} ({current_desc}), go to {next_room} ({next_desc})")
            
            return {
                'directions': directions,
                'path': coordinates,
                'all_rooms': self.get_all_rooms(),
                'all_paths': self.get_all_paths()
            }
            
        except nx.NetworkXNoPath:
            return {'error': 'No path found between these rooms'}
        except nx.NodeNotFound:
            return {'error': 'One or both rooms not found in the map'}

# Create global instance
campus = CampusMap()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_directions', methods=['POST'])
def get_directions():
    data = request.get_json()
    result = campus.get_directions(data['start'], data['end'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)