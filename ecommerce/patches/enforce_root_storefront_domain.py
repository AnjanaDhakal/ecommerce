from ecommerce.patches.move_storefronts_to_root_wildcard import execute


# This separate patch repairs installations where a legacy
# storefront_base_domain setting changed URLs back after the first migration.
