"""
OMNICODEC Methods Registry
All encoding/decoding method specifications are loaded from these modules.
"""
from .base_n import get_specs as base_specs
from .text_escape import get_specs as text_specs
from .compression import get_specs as compression_specs
from .crypto import get_specs as crypto_specs
from .serialization import get_specs as serialization_specs
from .esoteric_transport import get_specs as esoteric_specs

# New advanced method modules
from .unicode_languages import get_specs as unicode_lang_specs
from .esoteric_abnormal import get_specs as esoteric_abnormal_specs
from .advanced_base_n import get_specs as advanced_base_n_specs
from .web_advanced import get_specs as web_advanced_specs
from .serialization_advanced import get_specs as serialization_advanced_specs
from .compression_advanced import get_specs as compression_advanced_specs
from .crypto_symmetric import get_specs as crypto_symmetric_specs
from .visual_advanced import get_specs as visual_advanced_specs
from .scientific_specialized import get_specs as scientific_specialized_specs
from .legacy_archive import get_specs as legacy_archive_specs

# Extended crypto methods
from .crypto_extended import get_specs as crypto_extended_specs


ALL_SPEC_LOADERS = [
    # Original modules
    base_specs,
    text_specs,
    compression_specs,
    crypto_specs,
    serialization_specs,
    esoteric_specs,
    
    # New advanced modules
    unicode_lang_specs,
    esoteric_abnormal_specs,
    advanced_base_n_specs,
    web_advanced_specs,
    serialization_advanced_specs,
    compression_advanced_specs,
    crypto_symmetric_specs,
    visual_advanced_specs,
    scientific_specialized_specs,
    legacy_archive_specs,
    
    # Extended modules
    crypto_extended_specs,
]
