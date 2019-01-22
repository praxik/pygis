
import copy
from functools import singledispatch
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from fiona.transform import transform_geom

from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry
from shapely.geometry import Point, MultiPoint
from shapely.geometry import LinearRing, LineString, MultiLineString
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry import GeometryCollection

###
Types = (
  Point, MultiPoint,
  LinearRing, LineString, MultiLineString,
  Polygon, MultiPolygon,
  GeometryCollection )

###
class Geom:
  """
  Look into using Trellis for handling (Functional) Reactive Programming:
    http://peak.telecommunity.com/DevCenter/Trellis
  """

  ###
  def __eq__(
      self: 'Geom',
      other: 'Geom' ) -> bool:
    """
    """
    if isinstance( other, self.__class__ ):
      return (
        self.shape == other.shape and
        self.srid == other.srid )
    else:
      return False

  ###
  def __init__(
    self: 'Geom',
    arg = None,
    srid: int = 4326 ) -> None:
    """
    """
    # Initialize geometry
    init_registry = self.__init.registry
    self.__init = singledispatch( init_registry[ object ] )
    self.__init.register( BaseGeometry, self.__init_from_shapely )
    self.__init.register( dict, self.__init_from_dict )
    self.__init.register( str, self.__init_from_geojson )
    self.__shape = None
    self.__dict = None
    self.__geojson = None
    self.__init( arg )

    # Initialize other vars
    self.srid = srid

    # Hacky ¯\_(ツ)_/¯
    self.collection_extract = self.__collection_extract
    self.multi = self.__multi
    self.reproject = self.__reproject

  ###
  @singledispatch
  def __init(
    self: 'Geom',
    arg: Union[ BaseGeometry, Dict[ str, Any ], str ] ) -> None:
    """
    """
    raise TypeError( f"{type( arg )} not supported." )

  ###
  def __init_from_shapely(
    self: 'Geom',
    arg: BaseGeometry ) -> None:
    """
    """
    self.__shape = arg

  ###
  def __init_from_dict(
    self: 'Geom',
    arg: Dict[ str, Any ] ) -> None:
    """
    """
    self.__dict = arg

  ###
  def __init_from_geojson(
    self: 'Geom',
    arg: str ) -> None:
    """
    """
    self.__geojson = arg

  ###
  @property
  def shape(
    self: 'Geom' ) -> BaseGeometry:
    """
    """
    if self.__shape is None:
      self.__shape = shape( self.dict )
    return self.__shape

  ###
  @shape.setter
  def shape(
    self: 'Geom',
    val: BaseGeometry ) -> None:
    """
    """
    if self.__shape is val:
      return
    self.__shape = val
    self.__dict = None
    self.__geojson = None

  ###
  @property
  def dict(
    self: 'Geom' ) -> Dict[ str, Any ]:
    """
    """
    if self.__dict is None:
      if self.__shape is None:
        self.__dict = json.loads( self.geojson )
      else:
        self.__dict = mapping( self.shape )
    return self.__dict

  ###
  @dict.setter
  def dict(
    self: 'Geom',
    val: Dict[ str, Any ] ) -> None:
    """
    """
    if self.__dict is val:
      return
    self.__shape = None
    self.__dict = val
    self.__geojson = None

  ###
  @property
  def geojson(
    self: 'Geom' ) -> str:
    """
    """
    if self.__geojson is None:
      self.__geojson = json.dumps( self.dict )
    return self.__geojson

  ###
  @geojson.setter
  def geojson(
    self: 'Geom',
    val: str ) -> None:
    """
    """
    if self.__geojson is val:
      return
    self.__shape = None
    self.__dict = None
    self.__geojson = val

  ###
  @property
  def is_collection(
    self: 'Geom' ) -> bool:
    """
    """
    return is_collection( self.shape )

  ###
  @property
  def is_empty(
    self: 'Geom' ) -> bool:
    """
    """
    return self.shape.is_empty

  ###
  @property
  def type(
    self: 'Geom' ) -> str:
    """
    """
    return self.shape.geom_type

  ###
  @classmethod
  def build_geometry(
    cls: 'Geom',
    gseq: Sequence[ Optional[ 'Geom' ] ] ) -> Optional[ 'Geom' ]:
    """
    """
    # Remove None and empty geometries from sequence
    gseq = [ g.shape for g in gseq if not( g is None or g.is_empty ) ]
    return cls( build_geometry( gseq ) )

  ###
  def __collection_extract(
    self: 'Geom',
    gtype: str ) -> List[ 'Geom' ]:
    """
    """
    glist = collection_extract( self.shape, gtype )
    return [ self.__class__( g, srid = self.srid ) for g in glist ]

  ###
  def collection_extract(
    cls: 'Geom',
    geom: 'Geom',
    gtype: str ) -> List[ 'Geom' ]:
    """
    """
    glist = collection_extract( geom.shape, gtype )
    return [ cls( g, srid = geom.srid ) for g in glist ]

  ###
  def __multi(
    self: 'Geom' ) -> None:
    """
    """
    self.shape = multi( self.shape )

  ###
  @classmethod
  def multi(
    cls: 'Geom',
    geom: 'Geom' ) -> 'Geom':
    """
    """
    return cls( multi( geom.shape ) )

  ###
  def __reproject(
    self: 'Geom',
    srid: int,
    antimeridian_cutting: bool = False,
    antimeridian_offset: float = 10.0,
    precision: int = -1 ) -> None:
    """
    """
    self.dict = reproject( self.dict, self.srid, srid,
      antimeridian_cutting, antimeridian_offset, precision )
    self.srid = srid

  ###
  @classmethod
  def reproject(
    cls: 'Geom',
    geom: 'Geom',
    srid: int,
    antimeridian_cutting: bool = False,
    antimeridian_offset: float = 10.0,
    precision: int = -1 ) -> 'Geom':
    """
    """
    return cls( reproject( geom.dict, geom.srid, srid,
      antimeridian_cutting, antimeridian_offset, precision ), srid = srid )

################################################################################

###
def flatten(
  gtype: str ) -> str:
  """
  """
  if gtype == 'MultiPoint':
    return 'Point'
  if gtype == 'MultiLineString':
    return 'LineString'
  if gtype == 'MultiPolygon':
    return 'Polygon'

  return gtype

###
@singledispatch
def is_collection(
  arg: Optional[ Union[ str, BaseGeometry ] ] ) -> bool:
  """
  Returns `True` if the geometry type of the argument is either:
    GeometryCollection
    Multi{Point,Polygon,Linestring,Curve,Surface}
  """
  if arg is None:
    return False

  raise TypeError( f"{type( arg )} not supported." )

###
@is_collection.register( str )
def __(
  gtype: str ) -> bool:
  """
  """
  if gtype in (
    'MultiPoint', 'MultiLineString', 'MultiPolygon',
    'GeometryCollection' ):
    return True

  return False

###
@is_collection.register( BaseGeometry )
def __(
  geom: BaseGeometry ) -> bool:
  """
  """
  return is_collection( geom.geom_type )

###
def multi(
  geom: Optional[ BaseGeometry ] ) -> Optional[ BaseMultipartGeometry ]:
  """
  Returns the geometry as a Multi* geometry.
  If the geometry is already a Multi*, it is returned unchanged.
  """
  if geom is None:
    return None

  if geom.is_empty or is_collection( geom ):
    return geom
    #return copy.deepcopy( geom ) # May need to clone here?

  gtype = geom.geom_type
  if gtype == 'Point':
    return MultiPoint( [ geom ] )
  elif gtype == 'LineString':
    return MultiLineString( [ geom ] )
  elif gtype == 'Polygon':
    return MultiPolygon( [ geom ] )
  else:
    raise RuntimeError( "multi: unhandled type (" + gtype + ")" )

###
def build_geometry(
  gseq: Sequence[ Optional[ BaseGeometry ] ] ) -> Optional[ BaseGeometry ]:
  """
  """
  # Remove None and empty geometries from sequence
  gseq = [ g for g in gseq if not( g is None or g.is_empty ) ]

  # Return if gseq is None or empty
  if not gseq:
    return None

  # Determine some facts about the geometries in the list
  geom = None
  gtype = 'Null'
  heterogeneous = False
  collection = False
  for g in gseq:
    geom = g
    t = g.geom_type
    if gtype == 'Null':
      gtype = t
    if gtype != t:
      heterogeneous = True
    if is_collection( t ):
      collection = True

  # For the empty geometry, return an empty GeometryCollection
  if gtype == 'Null':
    return GeometryCollection()

  # This should always return a geometry
  if len( gseq ) == 1:
    return geom

  # For heterogenous collection or containing a collection
  if heterogeneous or collection:
    return GeometryCollection( gseq )

  # At this point we know the collection is homogenous
  if gtype == 'Point':
    return MultiPoint( gseq )
  elif gtype == 'LineString':
    return MultiLineString( gseq )
  elif gtype == 'Polygon':
    return MultiPolygon( gseq )
  else:
    raise RuntimeError( "build_geometry: unhandled type (" + gtype + ")" )

###
def collection_extract(
  geom: Optional[ BaseGeometry ],
  gtype: str,
  glist: List[ BaseGeometry ] = None ) -> List[ BaseGeometry ]:
  """
  Given a (multi)geometry, returns a (multi)geometry consisting only of elements of the specified type.
  Sub-geometries that are not the specified type are ignored.
  If there are no sub-geometries of the right type, an EMPTY geometry will be returned.
  Only points, lines and polygons are supported.
  """
  if glist is None:
    glist = []

  # Ensure the right type was input
  if gtype not in ( 'Point', 'LineString', 'Polygon' ):
    raise RuntimeError( 'collection_extract: '
      'only point, linestring and polygon may be extracted' )

  # Don't bother adding empty geometries
  if geom is None or geom.is_empty:
    return glist

  # Process each sub-geometry
  gt = geom.geom_type
  if gt == gtype:
    glist.append( geom )
    #glist.append( copy.deepcopy( geom ) ) # May need to clone here?
  elif is_collection( gt ):
    for g in geom.geoms:
      collection_extract( g, gtype, glist )

  return glist

###
@singledispatch
def reproject(
  arg: Optional[ Union[ Dict[ str, Any ], BaseGeometry ] ],
  src_srid: int,
  dst_srid: int,
  antimeridian_cutting: bool = False,
  antimeridian_offset: float = 10.0,
  precision: int = -1 ) -> None:
  """
  antimeridian_cutting: bool, optional
    ``True`` to cut output geometries in two at the antimeridian,
    the default is ``False`.
  antimeridian_offset: float, optional
    A distance in decimal degrees from the antimeridian,
    outside of which geometries will not be cut.
  precision: int, optional
    Optional rounding precision of output coordinates,
    in number of decimal places.
  """
  if arg is None:
    return None

  raise TypeError( f"{type( arg )} not supported." )

###
@reproject.register( dict )
def __(
  geom: Dict[ str, Any ],
  src_srid: int,
  dst_srid: int,
  antimeridian_cutting: bool = False,
  antimeridian_offset: float = 10.0,
  precision: int = -1 ) -> Dict[ str, Any ]:
  """
  """
  return transform_geom( f"EPSG:{src_srid}", f"EPSG:{dst_srid}", geom,
    antimeridian_cutting, antimeridian_offset, precision )

###
@reproject.register( BaseGeometry )
def __(
  geom: BaseGeometry,
  src_srid: int,
  dst_srid: int,
  antimeridian_cutting: bool = False,
  antimeridian_offset: float = 10.0,
  precision: int = -1 ) -> BaseGeometry:
  """
  """
  return shape( reproject( mapping( geom ), src_srid, dst_srid,
    antimeridian_cutting, antimeridian_offset, precision ) )

