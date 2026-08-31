import os
import dash
import dash_leaflet as dl
from dash import html, dcc, Output, Input, State, no_update
import openslide
from openslide import deepzoom
from flask import Flask, send_file
from io import BytesIO
import numpy as np
import h5py
import cv2
import shutil
import time
import uuid
from PIL import Image
import logging
import sys

# --- LOGGING SETUP ---
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
if not root.handlers:
    root.addHandler(handler)
logger = logging.getLogger(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# --- CONFIGURATION ---
DATA_DIR = "/gstore/scratch/ris-imaging/data/cockpit/7322/"
MASK_DIR = "/gstore/scratch/Users/momayyep/data/cockpit/qqc-results/results/"
TILE_SIZE = 512

wsi_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.ndpi')])
wsi_options = [{'label': f, 'value': f} for f in wsi_files]

active_session = {
    'slide': None, 'dz': None, 'max_level': 0,
    'current_wsi_path': "", 'current_h5_path': "",
    'dims': (0, 0),
    'mask_version': int(time.time()),
    'slide_version': int(time.time())
}

server = Flask(__name__)
app = dash.Dash(__name__, server=server)


def load_new_slide(filename):
    logger.info(f">>> INITIALIZING SLIDE: {filename}")
    wsi_path = os.path.join(DATA_DIR, filename)
    h5_name = filename.replace('.ndpi', '_qqc_refined_tissue.h5')
    slide_name = filename.replace('.ndpi', '')
    h5_path = os.path.join(MASK_DIR, slide_name, h5_name)
    refined_h5_path = h5_path.replace('_qqc_refined_tissue.h5', '_pixel-level.h5')

    if not os.path.exists(refined_h5_path) and os.path.exists(h5_path):
        os.makedirs(os.path.dirname(refined_h5_path), exist_ok=True)
        shutil.copy2(h5_path, refined_h5_path)
        logger.info(f"File Copied: {refined_h5_path}")

    slide = openslide.OpenSlide(wsi_path)
    dz = deepzoom.DeepZoomGenerator(slide, tile_size=TILE_SIZE, overlap=0)

    active_session.update({
        'slide': slide, 'dz': dz, 'max_level': dz.level_count - 1,
        'current_wsi_path': wsi_path, 'current_h5_path': refined_h5_path,
        'dims': slide.dimensions
    })
    return slide.dimensions


if wsi_files:
    load_new_slide(wsi_files[0])


# --- TILE SERVERS ---
@server.route("/tile/<z>/<x>/<y>")
def tile(z, x, y):
    dz = active_session.get('dz')
    if dz is None:
        return "Not Ready", 404

    # Parse coordinates
    x, y, z = int(x), int(y), int(z)

    # Calculate OpenSlide Level
    os_level = active_session['max_level'] + z

    # Check Level Validity
    if os_level < 0 or os_level >= dz.level_count:
        return "Invalid Zoom Level", 404

    cols, rows = dz.level_tiles[os_level]
    if x < 0 or y < 0 or x >= cols or y >= rows:
        return "Out of bounds", 404

    try:
        tile_img = dz.get_tile(os_level, (x, y))
        if tile_img.size != (TILE_SIZE, TILE_SIZE):
            new_img = Image.new("RGB", (TILE_SIZE, TILE_SIZE), "white")
            new_img.paste(tile_img, (0, 0))
            tile_img = new_img
        buf = BytesIO()
        tile_img.save(buf, 'JPEG', quality=85)
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"Tile Error: {e}")
        return "Tile Error", 404


@server.route("/mask_tile/<z>/<x>/<y>")
def mask_tile(z, x, y):
    if active_session.get('dz') is None:
        return "Not Ready", 404
    z_leaf, x, y = int(z), int(x), int(y)
    if x < 0 or y < 0:
        return "Out of bounds", 404

    os_level = active_session['max_level'] + z_leaf
    scale = int(2**(active_session['max_level'] - os_level))
    x_s, y_s = x * TILE_SIZE * scale, y * TILE_SIZE * scale

    try:
        with h5py.File(active_session['current_h5_path'], 'r') as f:
            ds = f["wsi_masks"]["predicted_region_mask_l0_1"]
            h_max, w_max = ds.shape

            if x_s >= w_max or y_s >= h_max:
                return "Out of bounds", 404

            read_w = min(TILE_SIZE * scale, w_max - x_s)
            read_h = min(TILE_SIZE * scale, h_max - y_s)
            if read_w <= 0 or read_h <= 0:
                return "Empty", 404

            data = ds[y_s: y_s + read_h: scale, x_s: x_s + read_w: scale]

        if data.size == 0:
            return "Empty", 404

        rgba = np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)
        h_paste, w_paste = data.shape
        rgba[:h_paste, :w_paste, 0] = 255
        rgba[:h_paste, :w_paste, 3] = (data > 0) * 120

        buf = BytesIO()
        Image.fromarray(rgba, 'RGBA').save(buf, 'PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logger.error(f"Mask Tile Error: {e}")
        return "Mask Error", 404

# --- LAYOUT & CSS ---


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Transform the square Leaflet handles into small circles */
            .leaflet-div-icon {
                background: #fff !important;
                border: 1px solid #333 !important;
                border-radius: 50% !important;
                width: 8px !important;
                height: 8px !important;
                margin-left: -4px !important;
                margin-top: -4px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.4);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


app.layout = html.Div([
    html.Div([
        html.H3("WSI Refiner", style={'marginTop': '0px'}),
        html.Label("1. Select Slide:"),
        dcc.Dropdown(
            id='slide-selector',
            options=wsi_options,
            value=wsi_files[0] if wsi_files else None,
            persistence=True,
            persistence_type='local'
        ),

        html.Hr(),
        html.Label("2. Editing Mode:"),
        dcc.RadioItems(
            id="mode-select",
            options=[{'label': ' Add Tissue', 'value': 'add'},
                     {'label': ' Remove Tissue', 'value': 'remove'}],
            value='add', labelStyle={
                'display': 'block', 'padding': '10px', 'fontSize': '16px'}
        ),

        html.Hr(),
        html.Button("APPLY TO H5", id="btn-apply", n_clicks=0,
                    style={'width': '100%', 'padding': '15px',
                           'backgroundColor': '#2c3e50', 'color': 'white',
                           'fontSize': '16px', 'cursor': 'pointer'}),

        html.Button("RELOAD MASK", id="btn-reload", n_clicks=0,
                    style={'width': '100%', 'marginTop': '10px',
                           'padding': '15px', 'backgroundColor': '#e67e22',
                           'color': 'white', 'fontSize': '16px',
                           'cursor': 'pointer', 'border': 'none'}),

        html.Button("DELETE DRAWING", id="btn-delete-drawing", n_clicks=0,
                    style={'width': '100%', 'marginTop': '10px',
                           'padding': '10px', 'backgroundColor': '#c0392b',
                           'color': 'white', 'border': 'none',
                           'cursor': 'pointer'}),

        html.Button(
            "ZOOM TO FIT", id="btn-zoom-fit", n_clicks=0,
            style={'width': '100%', 'marginTop': '10px', 'padding': '10px'}),

        html.Hr(),
        html.Label("Mask Opacity:"),
        dcc.Slider(
            id="opacity-slider",
            min=0,
            max=1,
            step=0.1,
            value=0.6,
            marks={0: '0', 0.5: '0.5', 1: '1'},
            tooltip={"placement": "bottom", "always_visible": False}
        ),

        html.Hr(),
        html.Div(id="status-box", style={
            'fontSize': '14px', 'fontWeight': 'bold',
            'color': '#2980b9', 'whiteSpace': 'pre-wrap'})
    ], style={
        'position': 'absolute', 'top': '10px', 'right': '10px', 'zIndex': 1000,
        'background': 'white', 'padding': '20px', 'width': '300px',
        'borderRadius': '8px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.4)'
    }),

    html.Div(id="map-container", style={'width': '100vw', 'height': '100vh'},
             children=[dl.Map(id="map", center=[0, 0], zoom=1)]),

    dcc.Store(id='poly-store', data=None)
])

# --- CALLBACKS ---


# VIEW UPDATE (Slide Change)
@app.callback(
    [Output("map-container", "children"),
     Output("status-box", "children"),
     Output("poly-store", "data", allow_duplicate=True)],
    [Input("slide-selector", "value"), Input("btn-zoom-fit", "n_clicks")],
    [State("mode-select", "value")],
    # FIX: Allows initial call even with duplicate output
    prevent_initial_call='initial_duplicate'
)
def update_view(filename, zoom_btn, mode_value):
    if active_session['current_wsi_path']:
        current_loaded = os.path.basename(active_session['current_wsi_path'])
    else:
        current_loaded = None

    if filename and filename != current_loaded:
        w, h = load_new_slide(filename)
        active_session['slide_version'] = int(time.time())
        active_session['mask_version'] = active_session['slide_version']
    else:
        w, h = active_session['dims']

    sv = active_session['slide_version']
    wsi_url = f"/tile/{{z}}/{{x}}/{{y}}?v={sv}"
    mask_url = f"/mask_tile/{{z}}/{{x}}/{{y}}?v={active_session['mask_version']}"

    draw_color = "green" if mode_value == "add" else "red"

    # FIX: Use Dynamic ID (uuid) for the Map to force a full re-render on slide change.
    # We removed 'key' and are changing 'id' instead to support older dash-leaflet.
    new_map_id = f"map-{uuid.uuid4()}"

    new_map = dl.Map(
        id=new_map_id, center=[-h/2, w/2],
        zoom=-4, crs="Simple", minZoom=-10, maxZoom=0,
        children=[
            dl.TileLayer(url=wsi_url, id="wsi-layer",
                         noWrap=True, tileSize=TILE_SIZE),
            dl.TileLayer(url=mask_url, id="mask-layer", opacity=0.6,
                         noWrap=True, tileSize=TILE_SIZE),
            dl.LayerGroup(id="drawing_layer_wrapper", children=[
                dl.FeatureGroup(id=f"feature_group-{uuid.uuid4()}", children=[
                    dl.EditControl(
                        id="edit_control", position="topleft",
                        draw={
                            "polyline": False, "circle": False,
                            "marker": False, "circlemarker": False,
                            "polygon": {"shapeOptions": {"color": draw_color}},
                            "rectangle": {"shapeOptions": {"color": draw_color}}
                        })
                    ])
                ])
            ], style={'width': '100vw', 'height': '100vh'})

    return new_map, f"Active: {filename}", None


# DRAWING MANAGER
@app.callback(
    [Output("poly-store", "data"), Output("drawing_layer_wrapper", "children")],
    [Input("edit_control", "geojson"),
     Input("btn-delete-drawing", "n_clicks"),
     Input("mode-select", "value")],
    [State("drawing_layer_wrapper", "children")],
    prevent_initial_call=True
)
def manage_drawings(geojson_data, delete_clicks, mode_value, current_wrapper_children):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    draw_color = "green" if mode_value == "add" else "red"

    # FIX: Generate a Random ID for the FeatureGroup.
    # Changing the ID forces React to destroy the old component (and the Leaflet layer with it),
    # effectively "clearing" the map of drawings.
    new_fg_id = f"feature_group-{uuid.uuid4()}"

    new_control_group = [dl.FeatureGroup(id=new_fg_id, children=[
        dl.EditControl(id="edit_control", position="topleft", draw={
            "polyline": False, "circle": False, "marker": False,
            "circlemarker": False,
            "polygon": {"shapeOptions": {"color": draw_color}},
            "rectangle": {"shapeOptions": {"color": draw_color}}
        })
    ])]

    # CASE A/B: Mode Switch or Delete -> Replace with NEW ID (Clears drawing)
    if trigger_id == "mode-select" or trigger_id == "btn-delete-drawing":
        if trigger_id == "btn-delete-drawing":
            logger.info("Drawing Deleted by User.")
        return None, new_control_group

    # CASE C: User Drew Shape -> Capture Data
    if trigger_id == "edit_control" and geojson_data:
        try:
            features = geojson_data.get('features', [])
            if not features:
                return no_update, no_update

            last_feature = features[-1]
            geometry = last_feature.get('geometry', {})
            coords = geometry.get('coordinates', [])

            if geometry.get('type') in ['Polygon', 'MultiPolygon'] and len(coords) > 0:
                outer_ring = coords[0]
                pts = [[int(p[0]), int(-p[1])] for p in outer_ring]
                logger.info(f"CAPTURED POLYGON ({len(pts)} pts).")
                return pts, no_update
        except Exception as e:
            logger.error(f"Error parsing drawing: {e}")
            return no_update, no_update

    return no_update, no_update


# SAVE TO DISK
@app.callback(
    [Output("btn-apply", "children"), Output("status-box", "children", allow_duplicate=True)],
    Input("btn-apply", "n_clicks"),
    [State("poly-store", "data"), State("mode-select", "value")],
    prevent_initial_call=True
)
def save_to_h5(n, poly_data, mode):
    if not poly_data:
        return "APPLY TO H5", "ERROR: Draw first!"

    try:
        with h5py.File(active_session['current_h5_path'], 'r+') as f:
            mask_ds = f["wsi_masks"]["predicted_region_mask_l0_1"]
            pts = np.array(poly_data, dtype=np.int32)

            if pts.size == 0:
                return "APPLY TO H5", "Error: Empty drawing"

            x_min, y_min = np.min(pts, axis=0).clip(0)
            x_max, y_max = np.max(pts, axis=0)

            h_max, w_max = mask_ds.shape
            x_max = min(x_max, w_max)
            y_max = min(y_max, h_max)
            x_min = min(x_min, x_max)
            y_min = min(y_min, y_max)

            if x_max - x_min <= 0 or y_max - y_min <= 0:
                return "APPLY TO H5", "Error: Selection outside image bounds"

            roi = mask_ds[y_min:y_max, x_min:x_max]
            canvas = np.zeros(roi.shape, dtype=np.uint8)
            cv2.fillPoly(canvas, [pts - [x_min, y_min]], 1)

            if mode == 'add':
                roi[canvas == 1] = 1
            else:
                roi[canvas == 1] = 0

            mask_ds[y_min:y_max, x_min:x_max] = roi
            logger.info(f"H5 WRITTEN: {mode} mode.")

        return "APPLY TO H5", "SAVED (Pending Reload)"

    except Exception as e:
        logger.error(f"CRITICAL H5 ERROR: {e}")
        return "Error!", f"Error: {str(e)}"


# REFRESH MASK
@app.callback(
    Output("mask-layer", "url"),
    Input("btn-reload", "n_clicks"),
    prevent_initial_call=True
)
def refresh_mask_layer(n):
    active_session['mask_version'] = int(time.time())
    new_url = f"/mask_tile/{{z}}/{{x}}/{{y}}?v={active_session['mask_version']}"
    logger.info("Refreshing mask layer view...")
    return new_url


# MASK OPACITY CONTROL
@app.callback(
    Output("mask-layer", "opacity"),
    Input("opacity-slider", "value"),
    prevent_initial_call=True
)
def update_mask_opacity(opacity_value):
    return opacity_value


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)
