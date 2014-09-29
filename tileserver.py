from __future__ import division

from collections import namedtuple
import math

from flask import Flask, Blueprint, render_template

import mapnik

tileserver = Blueprint('tiles', __name__)
web_ui = Blueprint('web_ui', __name__, template_folder='templates')


# ============================================================
#                          WARNING
# ============================================================
#
# We need the PostGIS data to be *already* converted to
# the same projection as the base layer, otherwise bounding
# box will get slightly "rotated" during coordinate conversion
# leading to misaligned tiles!
#
# Create a view to convert the data:
#
# CREATE OR REPLACE VIEW stradario_trento_900913 AS
# SELECT id, field1, field2, .., fieldN, st_transform(geom, 900913) as geom
# FROM stradario_trento;
# ALTER VIEW stradario_trento_900913 OWNER TO gis;
#
# ============================================================


POSTGIS_TABLE = dict(
    host='localhost',
    port=5433,
    user='gis',
    password='gis',
    dbname='geocatalogo',
    table='stradario_trento_900913')
LAYER_NAME = 'stradario_trento'

# WGS84 = '+proj=longlat +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +no_defs'  # 4326
# UTM32N = '+proj=utm +zone=32 +datum=WGS84 +units=m +no_defs'  # 32632

# Google Mercator - EPSG:900913
GOOGLEMERC = ('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
              '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs')
DATA_PROJECTION = mapnik.Projection(GOOGLEMERC)

TILE_WIDTH = 256  # Square tiles only!


minmax = lambda val, lower, upper: min(max(val, lower), upper)

tile_coords = namedtuple('TileCoords', 'x,y')
geo_coords = namedtuple('Coords', 'lat,lon')


def deg2num(lat_deg, lon_deg, zoom):
    """Convert coordinates to tile number"""

    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((
        1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)))
        / math.pi) / 2.0 * n)
    return tile_coords(x=xtile, y=ytile)


def num2deg(xtile, ytile, zoom):
    """Convert tile number to coordinates (of the upper corner)"""

    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return mapnik.Coord(y=lat_deg, x=lon_deg)


class TiledMapRenderer(object):
    def __init__(self, mapobj):
        self.m = mapobj

    def render_tile(self, z, x, y):
        """
        :param z: Zoom level
        :param x: Tile horizontal position
        :param y: Tile vertical position
        """

        topleft = num2deg(x, y, z)
        bottomright = num2deg(x + 1, y + 1, z)

        # Bounding box for the tile
        bbox = mapnik.Box2d(topleft, bottomright)

        bbox = DATA_PROJECTION.forward(bbox)

        print("Bouding box: ", bbox)

        # self.m.resize(TILE_WIDTH, TILE_WIDTH)
        self.m.zoom_to_box(bbox)

        MIN_BUFFER = 256
        self.m.buffer_size = max(self.m.buffer_size, MIN_BUFFER)

        # Render image with default Agg renderer
        im = mapnik.Image(TILE_WIDTH, TILE_WIDTH)
        mapnik.render(self.m, im)
        return im


@web_ui.route('/')
def index():
    return render_template('leaflet_map.html')


@tileserver.route('/<layer>/<int:z>/<int:x>/<int:y>.png')
def render_tile(layer, z, x, y):
    """
    Render the tile using mapnik.
    """

    m = mapnik.Map(TILE_WIDTH, TILE_WIDTH)
    # m.background = mapnik.Color('steelblue')

    s = mapnik.Style()
    r = mapnik.Rule()

    # polygon_symbolizer = mapnik.PolygonSymbolizer(mapnik.Color('#00ffff'))
    # r.symbols.append(polygon_symbolizer)

    line_symbolizer = mapnik.LineSymbolizer(
        mapnik.Color('#ff00ff'), 14)
    line_symbolizer.stroke.opacity = 0.5
    r.symbols.append(line_symbolizer)

    text_symbolizer = mapnik.TextSymbolizer(
        mapnik.Expression('[desvia]'),
        'DejaVu Sans Book', 10, mapnik.Color('black'))
    text_symbolizer.halo_fill = mapnik.Color('white')
    text_symbolizer.halo_radius = 2
    text_symbolizer.label_placement = mapnik.label_placement.LINE_PLACEMENT
    r.symbols.append(text_symbolizer)

    s.rules.append(r)
    m.append_style('My Style', s)

    # Initialize layer from PostGIS table
    ds = mapnik.PostGIS(**POSTGIS_TABLE)
    layer = mapnik.Layer(LAYER_NAME)
    layer.datasource = ds
    layer.styles.append('My Style')
    m.layers.append(layer)

    m.zoom_all()

    renderer = TiledMapRenderer(m)
    im = renderer.render_tile(z, x, y)

    # im = mapnik.Image(TILE_WIDTH, TILE_WIDTH)
    # mapnik.render(m, im, 13, 0, 0)
    # # im.save('/tmp/bla.png')

    return im.tostring('png'), 200, {'Content-type': 'image/png'}


def make_app():
    app = Flask('tileserver')
    app.register_blueprint(tileserver, url_prefix='/tiles')
    app.register_blueprint(web_ui, url_prefix='')
    return app


if __name__ == '__main__':
    app = make_app()
    app.run(debug=True, port=5000)
