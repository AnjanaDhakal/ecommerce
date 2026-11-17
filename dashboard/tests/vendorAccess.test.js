import test from 'node:test'
import assert from 'node:assert/strict'

import { hasVendorAccess } from '../src/utils/vendorAccess.js'

test('accepts a vendor role profile', () => {
  assert.equal(
    hasVendorAccess([{ role_profile_name: 'Ecommerce Vendor', roles: [] }]),
    true,
  )
})

test('accepts a directly assigned vendor role', () => {
  assert.equal(
    hasVendorAccess([{ role_profile_name: null, roles: ['Ecommerce Vendor'] }]),
    true,
  )
})

test('accepts the standard Frappe message wrapper', () => {
  assert.equal(
    hasVendorAccess({
      message: [{ role_profile_name: 'Ecommerce Vendor', roles: [] }],
    }),
    true,
  )
})

test('rejects missing and non-vendor role data', () => {
  assert.equal(hasVendorAccess(undefined), false)
  assert.equal(
    hasVendorAccess([{ role_profile_name: 'Ecommerce User', roles: [] }]),
    false,
  )
})
