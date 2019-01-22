
from itertools import chain
import unittest

from shapely.geometry import Point, MultiPoint
from shapely.geometry import LinearRing, LineString, MultiLineString
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry import GeometryCollection

from pygis.vec.geom import Geom

###
def speedups() -> bool:
  """
  Speedups are now enabled by default if they are available.
  You can check if speedups are enabled with the enabled attribute.
  """
  from shapely import speedups
  return speedups.enabled

###
class GeomTestCase( unittest.TestCase ):

  ### Create some simple test geometry
  def setUp( self ):
    # Create some points
    self.pnt1 = Point( 0, 0 )
    self.pnt2 = Point( 0, 1 )
    self.pnt3 = Point( 1, 1 )
    self.pnt4 = Point( 1, 0 )
    self.pnt5 = Point( 2, 2 )
    self.pnt6 = Point( 2, 4 )
    self.pnt7 = Point( 4, 4 )
    self.pnt8 = Point( 4, 2 )
    self.pnts = (
      self.pnt1, self.pnt2, self.pnt3, self.pnt4,
      self.pnt5, self.pnt6, self.pnt7, self.pnt8 )

    # Create some line strings
    self.lstr1 = LineString( ( self.pnt1, self.pnt2 ) )
    self.lstr2 = LineString( ( self.pnt2, self.pnt3 ) )
    self.lstr3 = LineString( ( self.pnt3, self.pnt4 ) )
    self.lstr4 = LineString( ( self.pnt4, self.pnt1 ) )
    self.lstr5 = LineString( ( self.pnt5, self.pnt6 ) )
    self.lstr6 = LineString( ( self.pnt6, self.pnt7 ) )
    self.lstr7 = LineString( ( self.pnt7, self.pnt8 ) )
    self.lstr8 = LineString( ( self.pnt8, self.pnt5 ) )
    self.lstrs = (
      self.lstr1, self.lstr2, self.lstr3, self.lstr4,
      self.lstr5, self.lstr6, self.lstr7, self.lstr8 )

    # Create some polygons
    self.poly1 = Polygon( (
      ( p.x, p.y ) for p in ( self.pnt1, self.pnt2, self.pnt3, self.pnt4 ) ) )
    self.poly2 = Polygon( (
      ( p.x, p.y ) for p in ( self.pnt3, self.pnt4, self.pnt5, self.pnt6 ) ) )
    self.polys = ( self.poly1, self.poly2 )

    # Create a sequence of geoms
    self.geoms = tuple( chain( *( self.pnts, self.lstrs, self.polys ) ) )

  ###
  def test_is_collection( self ):
    g = Geom( self.pnt1 )
    self.assertTrue( g.type == 'Point' )
    self.assertFalse( g.is_collection )

    g = Geom( MultiPoint( self.pnts ) )
    self.assertTrue( g.type == 'MultiPoint' )
    self.assertTrue( g.is_collection )

    g = Geom( self.lstr1 )
    self.assertTrue( g.type == 'LineString' )
    self.assertFalse( g.is_collection )

    g = Geom( MultiLineString( self.lstrs ) )
    self.assertTrue( g.type == 'MultiLineString' )
    self.assertTrue( g.is_collection )

    g = Geom( self.poly1 )
    self.assertTrue( g.type == 'Polygon' )
    self.assertFalse( g.is_collection )

    g = Geom( MultiPolygon( self.polys ) )
    self.assertTrue( g.type == 'MultiPolygon' )
    self.assertTrue( g.is_collection )

    g = Geom( GeometryCollection( self.geoms ) )
    self.assertTrue( g.type == 'GeometryCollection' )
    self.assertTrue( g.is_collection )

  ###
  def test_multi( self ):
    g = Geom( self.pnt1 )
    self.assertTrue( g.type == 'Point' )
    g.multi()
    self.assertTrue( g.type == 'MultiPoint' )

    g = Geom( self.lstr1 )
    self.assertTrue( g.type == 'LineString' )
    g.multi()
    self.assertTrue( g.type == 'MultiLineString' )

    g = Geom( self.poly1 )
    self.assertTrue( g.type == 'Polygon' )
    g.multi()
    self.assertTrue( g.type == 'MultiPolygon' )

  ###
  def test_build_geometry( self ):
    gseq = ( Geom( p ) for p in self.pnts )
    g = Geom.build_geometry( gseq )
    self.assertTrue( g.type == 'MultiPoint' )

    gseq = ( Geom( l ) for l in self.lstrs )
    g = Geom.build_geometry( gseq )
    self.assertTrue( g.type == 'MultiLineString' )

    gseq = ( Geom( p ) for p in self.polys )
    g = Geom.build_geometry( gseq )
    self.assertTrue( g.type == 'MultiPolygon' )

    gseq = ( Geom( g ) for g in self.geoms )
    g = Geom.build_geometry( gseq )
    self.assertTrue( g.type == 'GeometryCollection' )

  ###
  def test_collection_extract( self ):
    g = Geom( GeometryCollection( self.geoms ) )
    self.assertTrue( g.type == 'GeometryCollection' )

    glst = g.collection_extract( 'Point' )
    for p in glst:
      self.assertTrue( p.type == 'Point' )

    glst = g.collection_extract( 'LineString' )
    for l in glst:
      self.assertTrue( l.type == 'LineString' )

    glst = g.collection_extract( 'Polygon' )
    for p in glst:
      self.assertTrue( p.type == 'Polygon' )

  ###
  def test_reproject( self ):
    g = Geom( self.poly2, srid = 4326 )
    g.reproject( 3857 )
    self.assertTrue( g.srid == 3857 )

###
if __name__ == '__main__':
  unittest.main()
