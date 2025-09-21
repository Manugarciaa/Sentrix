"""
Shared libraries for Sentrix project
Librerías compartidas para el proyecto Sentrix

This package contains common functionality used by both backend and yolo-service
Este paquete contiene funcionalidad común usada por backend y yolo-service
"""

from .risk_assessment import (
    assess_dengue_risk,
    get_risk_recommendations,
    normalize_risk_level,
    format_risk_assessment_for_frontend,
    RiskLevel,
    BreedingSiteType,
    HIGH_RISK_CLASSES,
    MEDIUM_RISK_CLASSES
)

from .data_models import (
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    AnalysisStatusEnum,
    ValidationStatusEnum,
    CLASS_ID_TO_BREEDING_SITE,
    BREEDING_SITE_TO_CLASS_ID,
    YOLO_RISK_TO_DETECTION_RISK,
    YOLO_CLASS_NAMES,
    normalize_breeding_site_type,
    get_risk_level_for_breeding_site,
    breeding_site_to_class_id,
    class_id_to_breeding_site,
    get_all_breeding_sites
)

from .file_utils import (
    validate_file_extension,
    get_file_mime_type,
    validate_file_size,
    validate_image_file,
    normalize_filename,
    extract_filename_from_url,
    get_file_info,
    find_images_in_directory,
    validate_batch_files,
    ensure_directory_exists,
    safe_filename,
    get_temp_filepath,
    process_image_with_conversion,
    SUPPORTED_IMAGE_EXTENSIONS,
    IMAGE_MIME_TYPES,
    MAX_FILE_SIZE,
    MAX_BATCH_SIZE
)

from .image_formats import (
    ImageFormatConverter,
    SUPPORTED_IMAGE_FORMATS,
    is_format_supported,
    get_format_info,
    needs_conversion,
    convert_heic_to_jpeg
)

from .gps_utils import (
    extract_gps_from_exif,
    extract_camera_info_from_exif,
    validate_gps_coordinates,
    generate_maps_urls,
    calculate_distance_km,
    extract_complete_image_metadata,
    format_gps_for_frontend
)

from .logging_utils import (
    setup_logger,
    get_service_logger,
    get_module_logger,
    log_function_call,
    log_performance,
    log_error_with_context,
    log_detection_result,
    log_batch_progress,
    log_system_info,
    log_config_loaded,
    log_model_info,
    log_api_request,
    setup_backend_logging,
    setup_yolo_logging,
    setup_shared_logging,
    ProgressLogger
)

from .error_handling import (
    ErrorCode,
    SentrixError,
    ValidationError,
    FileProcessingError,
    ImageProcessingError,
    ModelError,
    DatabaseError,
    ServiceError,
    handle_exception,
    validate_required_fields,
    validate_file_size,
    validate_image_format,
    safe_execute,
    ErrorRecorder,
    error_recorder,
    create_error_response
)

from .config_manager import (
    Environment,
    DatabaseConfig,
    YoloServiceConfig,
    CorsConfig,
    LoggingConfig,
    SecurityConfig,
    SentrixConfig,
    ConfigManager,
    get_config_manager,
    load_service_config,
    get_service_config
)

from .project_structure import (
    ProjectStructure,
    get_backend_structure,
    get_yolo_structure,
    setup_service_structure,
    normalize_import_path,
    validate_service_structure,
    get_recommended_file_locations
)

from .import_utils import (
    ImportManager,
    setup_service_imports,
    safe_import,
    lazy_import,
    get_available_backends,
    validate_service_dependencies,
    create_requirements_file,
    get_import_manager
)

__version__ = "1.0.0"

__all__ = [
    # Risk assessment
    "assess_dengue_risk",
    "get_risk_recommendations",
    "normalize_risk_level",
    "format_risk_assessment_for_frontend",
    "RiskLevel",
    "BreedingSiteType",
    "HIGH_RISK_CLASSES",
    "MEDIUM_RISK_CLASSES",

    # Data models
    "DetectionRiskEnum",
    "BreedingSiteTypeEnum",
    "AnalysisStatusEnum",
    "ValidationStatusEnum",
    "CLASS_ID_TO_BREEDING_SITE",
    "BREEDING_SITE_TO_CLASS_ID",
    "YOLO_RISK_TO_DETECTION_RISK",
    "YOLO_CLASS_NAMES",
    "normalize_breeding_site_type",
    "get_risk_level_for_breeding_site",
    "breeding_site_to_class_id",
    "class_id_to_breeding_site",
    "get_all_breeding_sites",

    # File utilities
    "validate_file_extension",
    "get_file_mime_type",
    "validate_file_size",
    "validate_image_file",
    "normalize_filename",
    "extract_filename_from_url",
    "get_file_info",
    "find_images_in_directory",
    "validate_batch_files",
    "ensure_directory_exists",
    "safe_filename",
    "get_temp_filepath",
    "process_image_with_conversion",
    "SUPPORTED_IMAGE_EXTENSIONS",
    "IMAGE_MIME_TYPES",
    "MAX_FILE_SIZE",
    "MAX_BATCH_SIZE",

    # Image format conversion
    "ImageFormatConverter",
    "SUPPORTED_IMAGE_FORMATS",
    "is_format_supported",
    "get_format_info",
    "needs_conversion",
    "convert_heic_to_jpeg",

    # GPS utilities
    "extract_gps_from_exif",
    "extract_camera_info_from_exif",
    "validate_gps_coordinates",
    "generate_maps_urls",
    "calculate_distance_km",
    "extract_complete_image_metadata",
    "format_gps_for_frontend",

    # Logging utilities
    "setup_logger",
    "get_service_logger",
    "get_module_logger",
    "log_function_call",
    "log_performance",
    "log_error_with_context",
    "log_detection_result",
    "log_batch_progress",
    "log_system_info",
    "log_config_loaded",
    "log_model_info",
    "log_api_request",
    "setup_backend_logging",
    "setup_yolo_logging",
    "setup_shared_logging",
    "ProgressLogger",

    # Error handling
    "ErrorCode",
    "SentrixError",
    "ValidationError",
    "FileProcessingError",
    "ImageProcessingError",
    "ModelError",
    "DatabaseError",
    "ServiceError",
    "handle_exception",
    "validate_required_fields",
    "validate_file_size",
    "validate_image_format",
    "safe_execute",
    "ErrorRecorder",
    "error_recorder",
    "create_error_response",

    # Configuration management
    "Environment",
    "DatabaseConfig",
    "YoloServiceConfig",
    "CorsConfig",
    "LoggingConfig",
    "SecurityConfig",
    "SentrixConfig",
    "ConfigManager",
    "get_config_manager",
    "load_service_config",
    "get_service_config",

    # Project structure
    "ProjectStructure",
    "get_backend_structure",
    "get_yolo_structure",
    "setup_service_structure",
    "normalize_import_path",
    "validate_service_structure",
    "get_recommended_file_locations",

    # Import utilities
    "ImportManager",
    "setup_service_imports",
    "safe_import",
    "lazy_import",
    "get_available_backends",
    "validate_service_dependencies",
    "create_requirements_file",
    "get_import_manager"
]