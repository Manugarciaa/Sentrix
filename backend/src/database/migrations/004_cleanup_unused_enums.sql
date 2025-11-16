-- Migration: Clean up unused duplicate enums
-- Created: 2025-10-19
-- Purpose: Remove duplicate enums that are not used by any tables

-- Drop unused breeding site enums
DROP TYPE IF EXISTS breeding_site_type CASCADE;
DROP TYPE IF EXISTS breedingsitetypeenum CASCADE;

-- Drop unused detection risk enums
DROP TYPE IF EXISTS detection_risk CASCADE;
DROP TYPE IF EXISTS detectionriskenum CASCADE;

-- Drop unused location source enums
DROP TYPE IF EXISTS location_source CASCADE;
DROP TYPE IF EXISTS locationsourceenum CASCADE;

-- Drop unused risk level enums
DROP TYPE IF EXISTS risk_level CASCADE;
DROP TYPE IF EXISTS risklevelenum CASCADE;

-- Drop unused user role enums
DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS userroleenum CASCADE;

-- Drop unused validation status enums
DROP TYPE IF EXISTS validation_status CASCADE;
DROP TYPE IF EXISTS validationstatusenum CASCADE;

-- Add comments to the enums we're keeping
COMMENT ON TYPE breeding_site_type_enum IS 'Breeding site types - matches shared/data_models.py BreedingSiteTypeEnum';
COMMENT ON TYPE detection_risk_enum IS 'Detection risk levels - matches shared/data_models.py DetectionRiskEnum';
COMMENT ON TYPE location_source_enum IS 'Location data sources - matches shared/data_models.py LocationSourceEnum';
COMMENT ON TYPE risk_level_enum IS 'Analysis risk levels - matches shared/data_models.py RiskLevelEnum (alias of DetectionRiskEnum)';
COMMENT ON TYPE user_role_enum IS 'User roles - matches shared/data_models.py UserRoleEnum';
COMMENT ON TYPE validation_status_enum IS 'Validation status - matches shared/data_models.py ValidationStatusEnum';

-- Migration complete
