"""Enums and constants for the DaVinci Resolve Scripting API."""

from enum import Enum


class ResolvePage(str, Enum):
    """Pages (workspaces) available in DaVinci Resolve."""

    MEDIA = "media"
    CUT = "cut"
    EDIT = "edit"
    FUSION = "fusion"
    COLOR = "color"
    FAIRLIGHT = "fairlight"
    DELIVER = "deliver"


class TrackType(str, Enum):
    """Track types in a Resolve timeline."""

    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"


class CompositeMode(str, Enum):
    """Composite (blend) modes for timeline items."""

    NORMAL = "Normal"
    ADD = "Add"
    SUBTRACT = "Subtract"
    DIFFERENCE = "Difference"
    MULTIPLY = "Multiply"
    SCREEN = "Screen"
    OVERLAY = "Overlay"
    HARDLIGHT = "Hardlight"
    SOFTLIGHT = "Softlight"
    DARKEN = "Darken"
    LIGHTEN = "Lighten"
    COLOR_DODGE = "Color Dodge"
    COLOR_BURN = "Color Burn"
    LINEAR_DODGE = "Linear Dodge"
    LINEAR_BURN = "Linear Burn"
    LINEAR_LIGHT = "Linear Light"
    VIVID_LIGHT = "Vivid Light"
    PIN_LIGHT = "Pin Light"
    HARD_MIX = "Hard Mix"
    EXCLUSION = "Exclusion"
    HUE = "Hue"
    SATURATION = "Saturation"
    COLOR = "Color"
    LUMINOSITY = "Luminosity"


class ClipColor(str, Enum):
    """Clip label colors available in DaVinci Resolve."""

    ORANGE = "Orange"
    APRICOT = "Apricot"
    YELLOW = "Yellow"
    LIME = "Lime"
    OLIVE = "Olive"
    GREEN = "Green"
    TEAL = "Teal"
    NAVY = "Navy"
    BLUE = "Blue"
    PURPLE = "Purple"
    VIOLET = "Violet"
    PINK = "Pink"
    TAN = "Tan"
    BEIGE = "Beige"
    BROWN = "Brown"
    CHOCOLATE = "Chocolate"


class MarkerColor(str, Enum):
    """Marker colors available in DaVinci Resolve."""

    BLUE = "Blue"
    CYAN = "Cyan"
    GREEN = "Green"
    YELLOW = "Yellow"
    RED = "Red"
    PINK = "Pink"
    PURPLE = "Purple"
    FUCHSIA = "Fuchsia"
    ROSE = "Rose"
    LAVENDER = "Lavender"
    SKY = "Sky"
    MINT = "Mint"
    LEMON = "Lemon"
    SAND = "Sand"
    COCOA = "Cocoa"
    CREAM = "Cream"


class FlagColor(str, Enum):
    """Flag colors for clips and timeline items."""

    BLUE = "Blue"
    CYAN = "Cyan"
    GREEN = "Green"
    YELLOW = "Yellow"
    RED = "Red"
    PINK = "Pink"
    PURPLE = "Purple"
    FUCHSIA = "Fuchsia"
    ROSE = "Rose"
    LAVENDER = "Lavender"
    SKY = "Sky"
    MINT = "Mint"
    LEMON = "Lemon"
    SAND = "Sand"
    COCOA = "Cocoa"
    CREAM = "Cream"


class ExportType(str, Enum):
    """Export format types for timelines."""

    AAF = "AAF"
    DRT = "DRT"
    EDL = "EDL"
    FCPXML = "FCPXML"
    HDR10_PROFILE_A = "HDR10 Profile A"
    HDR10_PROFILE_B = "HDR10 Profile B"
    OTIO = "OTIO"
    TEXT_CSV = "Text CSV"
    TEXT_TAB = "Text Tab"


class TimelineExportSubtype(str, Enum):
    """Sub-types for certain export formats."""

    NONE = ""
    SMPTE = "SMPTE"
    AVID = "Avid"
    CMX_3600 = "CMX 3600"


# Commonly used Resolve project settings keys
PROJECT_SETTINGS = [
    "audioCaptureNumChannels",
    "audioOutputHasTimecode",
    "audioPlayoutNumChannels",
    "colorAcesGamutCompressType",
    "colorAcesIDT",
    "colorAcesNodeLUTProcessing",
    "colorAcesODT",
    "colorGalleryStillsLocation",
    "colorGalleryStillsNamingCustomPattern",
    "colorGalleryStillsNamingEnabled",
    "colorGalleryStillsNamingPrefix",
    "colorGalleryStillsNamingSuffix",
    "colorKeyframeDynamicsEndSetting",
    "colorKeyframeDynamicsStartSetting",
    "colorLuminanceMixerDefaultZero",
    "colorScienceMode",
    "colorSpaceInput",
    "colorSpaceInputGamma",
    "colorSpaceOutput",
    "colorSpaceOutputGamma",
    "colorSpaceTimeline",
    "colorSpaceTimelineGamma",
    "colorUseBGRPixelOrderForDPX",
    "colorUseContrastSCurve",
    "colorUseLegacyLogGrades",
    "colorUseLocalVersionsAsDefault",
    "colorUseStereoConvergenceForEffects",
    "deckLinkMonitorSelection",
    "deckLinkMonitorVideoFormat",
    "isAutoColorManage",
    "isExtForceConformEnabled",
    "perfAutoRenderCacheAfterTime",
    "perfAutoRenderCacheComposite",
    "perfAutoRenderCacheEnable",
    "perfAutoRenderCacheFuEffect",
    "perfAutoRenderCacheTransition",
    "perfCacheClipsLocation",
    "perfOptimisedCodec",
    "perfOptimisedMediaOn",
    "perfOptimizedResolutionRatio",
    "perfProxyMediaMode",
    "perfProxyMediaOn",
    "perfProxyResolutionRatio",
    "perfRenderCacheCodec",
    "perfRenderCacheMode",
    "superScale",
    "timelineDropFrameTimecode",
    "timelineFrameRate",
    "timelineInputResMismatchBehavior",
    "timelineInputResMismatchCustomPreset",
    "timelineInterlaceProcessing",
    "timelineOutputPixelAspectRatio",
    "timelineOutputResMatchTimelineRes",
    "timelineOutputResMismatchBehavior",
    "timelineOutputResMismatchCustomPreset",
    "timelineOutputResolutionHeight",
    "timelineOutputResolutionWidth",
    "timelinePlaybackFrameRate",
    "timelineResolutionHeight",
    "timelineResolutionWidth",
    "timelineSaveThumbsInProject",
    "timelineWorkingLuminance",
    "timelineWorkingLuminanceMode",
    "useCATransform",
    "useColorSpaceAwareGradingToolsIn",
    "useInverseDRT",
    "videoCleanApertureCropEnabled",
    "videoDATALevel",
    "videoDeckFormat",
    "videoDeckAdd32Pulldown",
    "videoDeckUse444SDI",
    "videoDeckUseHDROutput",
    "videoDeckUseStereoSDI",
    "videoMonitorBitDepth",
    "videoMonitorFormat",
    "videoMonitorMatrixEnabled",
    "videoMonitorScaling",
    "videoMonitorSDIConfiguration",
    "videoMonitorUse444SDI",
    "videoMonitorUseHDROutput",
    "videoMonitorUseLUT",
    "videoMonitorUseMatrixOverrideFor422SDI",
    "videoMonitorUseStereoSDI",
    "videoPlayoutBitDepth",
    "videoPlayoutFormat",
    "videoPlayoutLUT",
    "videoPlayoutLUTIndex",
]
