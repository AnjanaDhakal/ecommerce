export function hasVendorAccess(response) {
  const payload = response?.message ?? response
  const roleData = Array.isArray(payload) ? payload[0] : payload

  return Boolean(
    roleData &&
      (roleData.role_profile_name === 'Ecommerce Vendor' ||
        roleData.roles?.includes('Ecommerce Vendor')),
  )
}
