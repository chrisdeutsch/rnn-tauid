# The name of the package:
atlas_subdir(NtupleCreator)

# Component(s) in the package:
atlas_add_root_dictionary(NtupleCreatorLib
  NtupleCreatorDictSource
  ROOT_HEADERS NtupleCreator/*.h Root/LinkDef.h
  EXTERNAL_PACKAGES ROOT)

# add the library itself:
atlas_add_library(NtupleCreatorLib
  NtupleCreator/*.h NtupleCreator/*.ihh Root/*.cxx ${NtupleCreatorDictSource}
  PUBLIC_HEADERS NtupleCreator
  INCLUDE_DIRS
  LINK_LIBRARIES EventLoop EventLoopAlgs xAODEventInfo xAODTau
  PRIVATE_LINK_LIBRARIES)
