
import copy
from functools import singledispatch
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import fiona
from fiona.crs import from_epsg

import shapely
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry

import geom

###
class Feat:
"""
"""
  ###
  def __init__(
    self,
    arg = None ) -> None:
  """
  """
    # Initialize geometry
    init_registry = self.__init.registry
    self.__init = singledispatch( init_registry[ object ] )
    self.__init.register( ( dict, BaseGeometry ), self.__init_from_featpair )
    self.__init.register( BaseGeometry, self.__init_from_shapely )
    self.__init.register( dict, self.__init_from_dict )
    self.__init.register( str, self.__init_from_geojson )
    self.__geom = None
    self.__dict = None
    self.__geojson = None
    self.__init( arg )

    # Initialize other vars
    self.meta = col.meta
    self.srid = int( ''.join( filter( str.isdigit, col.meta[ 'crs' ][ 'init' ] ) ) )

    # Hacky ¯\_(ツ)_/¯
    self.reproject = self.__reproject

  ###
  @singledispatch
  def __init(
    self: 'Feat',
    arg: Union[] ) -> None:
    """
    """
    raise TypeError( f"{type( arg )} not supported." )

  ###
  def __init_from_featpair(
    self: 'Feat',
    arg: ( Dict[ str, Any ], BaseGeometry ) ) -> None:
    """
    """
    self.__geom = arg

  ###
  def __init_from_shapely(
    self: 'Feat',
    arg: BaseGeometry ) -> None:
    """
    """
    self.__geom = arg

  ###
  def __init_from_dict(
    self: 'Feat',
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
  def __reproject(
    self: 'Feat',
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
    cls: 'Feat',
    feat: 'Feat',
    srid: int,
    antimeridian_cutting: bool = False,
    antimeridian_offset: float = 10.0,
    precision: int = -1 ) -> 'Geom':
    """
    """
    #return cls( reproject( feat.dict, feat.srid, srid,
      #antimeridian_cutting, antimeridian_offset, precision ), srid = srid )

################################################################################

###
def dataset_extract(
  dataset: str,
  gtype: str,
  dst_srid: int = 0 ) -> List[ Tuple[ Dict[ str, Any ], BaseGeometry ] ]:
  """
  """
  result = []
  with fiona.open( dataset, 'r' ) as source:
    meta = source.meta
    crs = meta[ 'crs' ]
    epsg = crs[ 'init' ]
    src_srid = int( ''.join( filter( str.isdigit, epsg ) ) or 4326 )
    if dst_srid == 0:
      dst_srid = src_srid
    reproject = ( dst_srid != src_srid )
    for feat in source:
      try:
        props = feat[ 'properties' ]
        geom = shape( feat[ 'geometry' ] )
        if reproject:
          geom = reproject( geom, srs_srid, dst_srid )
        if not geom.is_valid:
          # Do something
          #clean = geom.buffer( 0.0 )
          raise RuntimeError( 'dataset_extract: error' )
        result.append( ( props, geom ) )

      except Exception:
        # Do something
        raise RuntimeError( 'dataset_extract: error' )

  return result
